"""
XML-RPC Server with asyncio.

This module adapt the ``xmlrpc.server`` module of the standard library to
work with asyncio.

"""

import asyncio
import aiohttp
import xmlrpc.server
from aiohttp.server import ServerHttpProtocol
from xmlrpc.client import gzip_decode

__ALL__ = ['SimpleXMLRPCRequestHandler', 'SimpleXMLRPCDispatcher']

SimpleXMLRPCDispatcher = xmlrpc.server.SimpleXMLRPCDispatcher


class SimpleXMLRPCRequestHandler(ServerHttpProtocol):
    """
    Simple XMLRPC Request handler compatible with low layer of aiohttp
    """
    rpc_paths = ('/', '/RPC2')

    def __init__(self, *, dispatcher, **kwargs):
        """
        :param dispatcher: XMLRPC dispatcher come from library (SimpleXMLRPCDispatcher or multipath)
        """
        super().__init__(**kwargs)
        self._dispatcher = dispatcher

    def is_rpc_path_valid(self, path):
        if self.rpc_paths:
            return path in self.rpc_paths
        else:
            # If .rpc_paths is empty, just assume all paths are legal
            return True

    @asyncio.coroutine
    def handle_request(self, message, payload):

        if not self.is_rpc_path_valid(message.path):
            yield from self.send_404(message.version)
            return

        # retrieve data
        data = yield from self.decode_request_content(message, payload)

        # call RPC
        xml = self._dispatcher._marshaled_dispatch(data, path=message.path)

        # send response
        yield from self.send_response(200, message.version, xml)

    @asyncio.coroutine
    def decode_request_content(self, message, payload):
        data = yield from payload.read()
        encoding = message.headers.get("content-encoding", "indentity").lower()

        if encoding == "identity":
            return data
        elif encoding == "gzip":
            try:
                return gzip_decode(data)
            except NotImplementedError:
                yield from self.send_response(501, message.version)
            except ValueError:
                yield from self.send_response(400, message.version)

    @asyncio.coroutine
    def send_response(self, code, version, text=b""):
        response = aiohttp.Response(
            self.writer, code, http_version=version
        )
        response.add_header("Content-type", "text/xml")
        response.add_header("Content-length", str(len(text)))
        response.send_headers()
        response.write(text)
        yield from response.write_eof()

    @asyncio.coroutine
    def send_404(self, version):
        yield from self.send_response(404, version, b"No such page")
