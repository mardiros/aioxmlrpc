"""
XML-RPC Server with asyncio.

This module adapt the ``xmlrpc.server`` module of the standard library to
work with asyncio.

Handle RPC of classic and coroutine functions

"""

import sys
import asyncio
import aiohttp
import xmlrpc.server
from aiohttp.server import ServerHttpProtocol
from xmlrpc.client import gzip_decode, loads, dumps, Fault

__ALL__ = ['SimpleXMLRPCRequestHandler', 'SimpleXMLRPCDispatcher', 'SimpleXMLRPCServer']

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
        xml = yield from self._dispatcher._marshaled_dispatch(data, path=message.path)

        # send response
        yield from self.send_response(200, message.version, xml)

    @asyncio.coroutine
    def decode_request_content(self, message, payload):
        data = yield from payload.read()
        encoding = message.headers.get("content-encoding", "indentity").lower()

        if encoding == "indentity":
            return data
        elif encoding == "gzip":
            try:
                return gzip_decode(data)
            except NotImplementedError:
                yield from self.send_response(501, message.version)
            except ValueError:
                yield from self.send_response(400, message.version)
        else:
            yield from self.send_response(501, message.version, b"encoding not supported")

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


class SimpleXMLRPCServer(SimpleXMLRPCDispatcher):
    @asyncio.coroutine
    def _marshaled_dispatch(self, data, path=None):
        """
        Override function from SimpleXMLRPCDispatcher to handle coroutines RPC case
        """
        try:
            params, method = loads(data, use_builtin_types=self.use_builtin_types)

            response = yield from self._dispatch(method, params)
            # wrap response in a singleton tuple
            response = (response,)
            response = dumps(response, methodresponse=1,
                             allow_none=self.allow_none, encoding=self.encoding)
        except Fault as fault:
            response = dumps(fault, allow_none=self.allow_none,
                             encoding=self.encoding)
        except:
            # report exception back to server
            exc_type, exc_value, exc_tb = sys.exc_info()
            response = dumps(
                Fault(1, "%s:%s" % (exc_type, exc_value)),
                encoding=self.encoding, allow_none=self.allow_none,
                )

        return response.encode(self.encoding)

    @asyncio.coroutine
    def _dispatch(self, method, params):
        """
        Override function from SimpleXMLRPCDispatcher to handle coroutine
        RPC call
        """
        func = None
        try:
            # check to see if a matching function has been registered
            func = self.funcs[method]
        except KeyError:
            if self.instance is not None:
                # check for a _dispatch method
                if hasattr(self.instance, '_dispatch'):
                    if asyncio.iscoroutinefunction(self.instance._dispatch):
                        return (yield from self.instance._dispatch(method, params))
                    else:
                        return self.instance._dispatch(method, params)
                else:
                    # call instance method directly
                    try:
                        func = xmlrpc.server.resolve_dotted_attribute(
                            self.instance,
                            method,
                            self.allow_dotted_names
                            )
                    except AttributeError:
                        pass

        if func is not None:
            if asyncio.iscoroutinefunction(func):
                result = yield from func(*params)
                return result
            else:
                return func(*params)
        else:
            raise Exception('method "%s" is not supported' % method)

    def request_handler(self, **kwargs):
        """
        Use as Request handler factory
        """
        return SimpleXMLRPCRequestHandler(dispatcher=self, **kwargs)