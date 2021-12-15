import pytest
from httpx import Request, Response
from aioxmlrpc.client import Fault, ProtocolError, ServerProxy

RESPONSES = {
    "http://localhost/test_xmlrpc_ok": {
        "status": 200,
        "body": """<?xml version="1.0"?>
<methodResponse>
   <params>
      <param>
         <value><int>1</int></value>
      </param>
   </params>
</methodResponse>""",
    },
    "http://localhost/test_xmlrpc_fault": {
        "status": 200,
        "body": """<?xml version="1.0"?>
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
""",
    },
    "http://localhost/test_http_500": {
        "status": 500,
        "body": """
I am really broken
""",
    },
}


# class Response:
#     def __init__(self, url):
#         response = RESPONSES[url]
#         self.status_code = response["status"]
#         self.text = response["body"]
#         self.headers = {}


class DummyAsyncClient:
    async def post(self, url, *args, **kwargs):
        response = RESPONSES[url]
        return Response(
            status_code=response["status"], headers={}, text=response["body"],
            request=Request("POST", url)
        )


@pytest.mark.asyncio
async def test_xmlrpc_ok():
    client = ServerProxy("http://localhost/test_xmlrpc_ok", session=DummyAsyncClient())
    response = await client.name.space.proxfyiedcall()
    assert response == 1


@pytest.mark.asyncio
async def test_xmlrpc_fault():
    client = ServerProxy(
        "http://localhost/test_xmlrpc_fault", session=DummyAsyncClient()
    )

    with pytest.raises(Fault):
        await client.name.space.proxfyiedcall()


@pytest.mark.asyncio
async def test_http_500():
    client = ServerProxy("http://localhost/test_http_500", session=DummyAsyncClient())

    with pytest.raises(ProtocolError):
        await client.name.space.proxfyiedcall()


@pytest.mark.asyncio
async def test_network_error():
    client = ServerProxy("http://nonexistent/nonexistent")

    with pytest.raises(ProtocolError):
        await client.name.space.proxfyiedcall()
