from unittest import TestCase
from aiohttp import HttpVersion11, RawRequestMessage, streams
import asyncio


def stream_reader_factory(data):
    """
    Fill a StreamReader with raw data
    :param data: bytes
    :return: StreamReader
    """
    s = streams.StreamReader()
    s.feed_data(data)
    s.feed_eof()
    return s


def request_factory(data):
    """
    Built parameter for handle_request function
    :param data: raw xml
    :return: dict(message:RawRequestMessage, payload:StreamReader)
    """
    return {
        'message': RawRequestMessage(
            method='POST',
            path='/RPC2',
            headers={
                'HOST': 'localhost:8080',
                'ACCEPT-ENCODING': 'gzip',
                'CONTENT-TYPE': 'text/xml',
                'USER-AGENT': 'Python-xmlrpc/3.4',
                'CONTENT-LENGTH': '%s' % len(data)
            },
            version=HttpVersion11,
            raw_headers=[],
            should_close=False,
            compression=None
        ),
        'payload': stream_reader_factory(data)
    }


def request_info():
    """
    forge request for info function
    """
    return request_factory(b"""<?xml version='1.0'?>
<methodCall>
    <methodName>info</methodName>
    <params>
    </params>
</methodCall>
""")


class ServerProxyTestCase(TestCase):
    def test_normal_function_ok(self):
        """
        Normal remote function call
        """
        from aioxmlrpc.server import SimpleXMLRPCServer
        def info():
            return 'ok_return_from_info'

        server = SimpleXMLRPCServer()
        server.register_function(info)

        handler = server.request_handler()
        class Mock:
            def __init__(self):
                self.data = b''
            def write(self, data):
                self.data += data
            @asyncio.coroutine
            def drain(self, *args, **kwargs):
                pass

        handler.writer = Mock()
        asyncio.get_event_loop().run_until_complete(asyncio.gather(
           handler.handle_request(**request_info())
        ))

        self.assertTrue(b"<?xml version='1.0'?>\n<methodResponse>\n<params>\n<param>\n<value><string>ok_return_from_info</string></value>\n</param>\n</params>\n</methodResponse>\n" in handler.writer.data)

    def test_coroutine_function_ok(self):
        """
        Remlote Coroutine Call RCC
        """
        from aioxmlrpc.server import SimpleXMLRPCServer
        @asyncio.coroutine
        def info():
            yield from asyncio.sleep(1)
            return 'ok_return_from_info_coroutine'

        server = SimpleXMLRPCServer()
        server.register_function(info)

        handler = server.request_handler()

        class Mock:
            def __init__(self):
                self.data = b''

            def write(self, data):
                self.data += data

            @asyncio.coroutine
            def drain(self, *args, **kwargs):
                pass

        handler.writer = Mock()
        asyncio.get_event_loop().run_until_complete(asyncio.gather(
            handler.handle_request(**request_info())
        ))

        self.assertTrue(b"<?xml version='1.0'?>\n<methodResponse>\n<params>\n<param>\n<value><string>ok_return_from_info_coroutine</string></value>\n</param>\n</params>\n</methodResponse>\n" in handler.writer.data)

    def test_instance(self):
        """
        Use an object to keep context
        """
        from aioxmlrpc.server import SimpleXMLRPCServer
        class Api:
            def info(self):
                return 'ok_return_from_api_instance'

        server = SimpleXMLRPCServer()
        server.register_instance(Api())

        handler = server.request_handler()

        class Mock:
            def __init__(self):
                self.data = b''

            def write(self, data):
                self.data += data

            @asyncio.coroutine
            def drain(self, *args, **kwargs):
                pass

        handler.writer = Mock()
        asyncio.get_event_loop().run_until_complete(asyncio.gather(
            handler.handle_request(**request_info())
        ))

        self.assertTrue(
            b"<?xml version='1.0'?>\n<methodResponse>\n<params>\n<param>\n<value><string>ok_return_from_api_instance</string></value>\n</param>\n</params>\n</methodResponse>\n" in handler.writer.data)

    def test_instance_coroutine(self):
        """
        call a coroutine of an object
        """
        from aioxmlrpc.server import SimpleXMLRPCServer
        class Api:
            @asyncio.coroutine
            def info(self):
                asyncio.sleep(1)
                return 'ok_return_from_api_instance_coroutine'

        server = SimpleXMLRPCServer()
        server.register_instance(Api())

        handler = server.request_handler()

        class Mock:
            def __init__(self):
                self.data = b''

            def write(self, data):
                self.data += data

            @asyncio.coroutine
            def drain(self, *args, **kwargs):
                pass

        handler.writer = Mock()
        asyncio.get_event_loop().run_until_complete(asyncio.gather(
            handler.handle_request(**request_info())
        ))

        self.assertTrue(
            b"<?xml version='1.0'?>\n<methodResponse>\n<params>\n<param>\n<value><string>ok_return_from_api_instance_coroutine</string></value>\n</param>\n</params>\n</methodResponse>\n" in handler.writer.data)

    def test_dispatcher(self):
        """
        handle  normal RPC through a _dispatch function
        """
        from aioxmlrpc.server import SimpleXMLRPCServer
        class Api:
            def _dispatch(self, name, *args):
                return 'ok_return_from_dispatcher_%s' % name

        server = SimpleXMLRPCServer()
        server.register_instance(Api())

        handler = server.request_handler()

        class Mock:
            def __init__(self):
                self.data = b''

            def write(self, data):
                self.data += data

            @asyncio.coroutine
            def drain(self, *args, **kwargs):
                pass

        handler.writer = Mock()
        asyncio.get_event_loop().run_until_complete(asyncio.gather(
            handler.handle_request(**request_info())
        ))

        self.assertTrue(
            b"<?xml version='1.0'?>\n<methodResponse>\n<params>\n<param>\n<value><string>ok_return_from_dispatcher_info</string></value>\n</param>\n</params>\n</methodResponse>\n" in handler.writer.data)

    def test_dispatcher_coroutines(self):
        from aioxmlrpc.server import SimpleXMLRPCServer
        class Api:
            @asyncio.coroutine
            def _dispatch(self, name, *args):
                yield from asyncio.sleep(1)
                return 'ok_return_from_dispatcher_%s' % name

        server = SimpleXMLRPCServer()
        server.register_instance(Api())

        handler = server.request_handler()

        class Mock:
            def __init__(self):
                self.data = b''

            def write(self, data):
                self.data += data

            @asyncio.coroutine
            def drain(self, *args, **kwargs):
                pass

        handler.writer = Mock()
        asyncio.get_event_loop().run_until_complete(asyncio.gather(
            handler.handle_request(**request_info())
        ))

        self.assertTrue(
            b"<?xml version='1.0'?>\n<methodResponse>\n<params>\n<param>\n<value><string>ok_return_from_dispatcher_info</string></value>\n</param>\n</params>\n</methodResponse>\n" in handler.writer.data)


    def test_unknown_function_ok(self):
        """
        test error case
        """
        from aioxmlrpc.server import SimpleXMLRPCServer
        def not_info():
            return 'ok_return_from_info'

        server = SimpleXMLRPCServer()
        server.register_function(not_info)

        handler = server.request_handler()
        class Mock:
            def __init__(self):
                self.data = b''
            def write(self, data):
                self.data += data
            @asyncio.coroutine
            def drain(self, *args, **kwargs):
                pass

        handler.writer = Mock()
        asyncio.get_event_loop().run_until_complete(asyncio.gather(
           handler.handle_request(**request_info())
        ))

        self.assertTrue(b"method \"info\" is not supported" in handler.writer.data)
