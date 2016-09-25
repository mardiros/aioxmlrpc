"""
XML-RPC Server with asyncio.

This module adapt the ``xmlrpc.server`` module of the standard library to
work with asyncio.

"""

import asyncio
import aiohttp.server
from xmlrpc.client import gzip_decode


class SimpleXMLRPCRequestHandler(aiohttp.server.ServerHttpProtocol):
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
    def report_404(self, message):
        text = b'No such page'
        response = aiohttp.Response(
            self.writer, 404, http_version=message.version
        )
        response.add_header("Content-type", "text/plain")
        response.add_header("Content-length", str(len(text)))
        response.send_headers()
        response.write(text)
        yield from response.write_eof()

    @asyncio.coroutine
    def handle_request(self, message, payload):

        if not self.is_rpc_path_valid(message.path):
            yield from self.report_404()
            return

        data = yield from payload.read()

        # handle gzip encoding
        encoding = self.headers.get("content-encoding", "identity").lower()


        xml = self._dispatcher._marshaled_dispatch(data, path=message.path)
        response = aiohttp.Response(
            self.writer, 200, http_version=message.version
        )
        response.add_header("Content-type", "text/xml")
        response.add_header("Content-length", str(len(xml)))
        response.send_headers()
        response.write(xml)
        yield from response.write_eof()

    @asyncio.coroutine
    def decode_request_content(self, message, payload):
        data = yield from payload.read()
        encoding = message.headers.get("content-encoding", "indentity").lower()

        if encoding == "identity":
            return data
        elif encoding == "gzip":
            try:
                data = gzip_decode(data)
            except NotImplementedError:
                # error 501
                pass
            except ValueError:
                # error 400
                pass