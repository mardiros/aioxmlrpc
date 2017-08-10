import sys
import asyncio
import aiohttp

from unittest import TestCase
from unittest import mock

from aioxmlrpc.client import ServerProxy, ProtocolError, Fault

RESPONSES = {

    'http://localhost/test_xmlrpc_ok': {'status': 200,
                                        'body': """<?xml version="1.0"?>
<methodResponse>
   <params>
      <param>
         <value><int>1</int></value>
      </param>
   </params>
</methodResponse>"""
                                        },
    'http://localhost/test_xmlrpc_fault': {'status': 200,
                                           'body': """<?xml version="1.0"?>
<methodResponse>
  <fault>
    <value>
      <struct>
        <member>
          <name>faultCode</name>
            <value><int>4</int></value>
            </member>
        <member>
           <name>faultString</name>
           <value><string>You are not lucky</string></value>
        </member>
      </struct>
    </value>
  </fault>
</methodResponse>
"""
                                           },
    'http://localhost/test_http_500': {'status': 500,
                                       'body': """
I am really broken
"""
                                       }

}

PY35 = sys.version_info >= (3, 5)

@asyncio.coroutine
def dummy_response(method, url, **kwargs):
    class Response:
        def __init__(self):
            response = RESPONSES[url]
            self.status = response['status']
            self.body = response['body']
            self.headers = {}

        @asyncio.coroutine
        def text(self):
            return self.body

    return Response()


@asyncio.coroutine
def dummy_request(*args, **kwargs):

    if isinstance(args[0], aiohttp.ClientSession):
        return dummy_response(*args[1:], **kwargs)
    else:
        return dummy_response(*args, **kwargs)


class ServerProxyWithSessionTestCase(TestCase):
    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.session = aiohttp.ClientSession(loop=self.loop)
        self.session.request = dummy_request

    def tearDown(self):
        self.loop.run_until_complete(self.session.close())

    def test_xmlrpc_ok(self):
        client = ServerProxy('http://localhost/test_xmlrpc_ok',
                             loop=self.loop,
                             session=self.session)
        response = self.loop.run_until_complete(
            client.name.space.proxfyiedcall()
        )
        self.assertEqual(response, 1)
        self.assertIs(self.loop, client._loop)

    def test_xmlrpc_fault(self):
        client = ServerProxy('http://localhost/test_xmlrpc_fault',
                             loop=self.loop,
                             session=self.session)

        with self.assertRaises(Fault):
            self.loop.run_until_complete(client.name.space.proxfyiedcall())

    def test_http_500(self):
        client = ServerProxy('http://localhost/test_http_500',
                             loop=self.loop,
                             session=self.session)

        with self.assertRaises(ProtocolError):
            self.loop.run_until_complete(client.name.space.proxfyiedcall())

    def test_xmlrpc_ok_global_loop(self):
        client = ServerProxy('http://localhost/test_xmlrpc_ok',
                             session=self.session)
        response = self.loop.run_until_complete(
            client.name.space.proxfyiedcall()
        )
        self.assertIs(self.loop, client._loop)
        self.assertEqual(response, 1)


class ServerProxyWithoutSessionTestCase(TestCase):

    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        session_request = mock.patch('aiohttp.ClientSession.request', new=dummy_request)
        session_request.start()
        self.addCleanup(session_request.stop)

    def test_close_session(self):
        client = ServerProxy('http://localhost/test_xmlrpc_ok',
                             loop=self.loop)
        response = self.loop.run_until_complete(
            client.name.space.proxfyiedcall()
        )
        self.assertEqual(response, 1)
        self.assertIs(self.loop, client._loop)
        self.loop.run_until_complete(client.close())

    if PY35:
        def test_contextmanager(self):
            self.loop.run_until_complete(self.xmlrpc_with_context_manager())

        async def xmlrpc_with_context_manager(self):
            async with ServerProxy('http://localhost/test_xmlrpc_ok',
                                   loop=self.loop) as client:
                response = await client.name.space.proxfyiedcall()
            self.assertEqual(response, 1)
            self.assertIs(self.loop, client._loop)


@asyncio.coroutine
def failing_request(*args, **kwargs):
    raise OSError


class HTTPErrorTestCase(TestCase):
    def setUp(self):
        self.loop = asyncio.new_event_loop()
        self.session = aiohttp.ClientSession(loop=self.loop)
        self.session.request = failing_request

    def tearDown(self):
        self.loop.run_until_complete(self.session.close())

    def test_http_error(self):
        client = ServerProxy('http://nonexistent/nonexistent', loop=self.loop,
                             session=self.session)
        with self.assertRaises(ProtocolError):
            self.loop.run_until_complete(client.name.space.proxfyiedcall())
