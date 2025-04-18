"""
XML-RPC Server with asyncio.

This module adapt the ``xmlrpc.server`` module of the standard library to
work with asyncio.

Handle RPC of classic and coroutine functions

"""

import asyncio
import inspect
from types import TracebackType
from typing import (
    Any,
    Awaitable,
    Callable,
    Coroutine,
    Iterable,
    Optional,
    Tuple,
    overload,
)
from xmlrpc import server
from xmlrpc.client import loads, dumps, Fault

import uvicorn
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route


__all__ = ["SimpleXMLRPCDispatcher", "SimpleXMLRPCServer"]

_Marshallable = Any


class SimpleXMLRPCDispatcher(server.SimpleXMLRPCDispatcher):
    async def _marshaled_dispatch(self, data: str) -> bytes:  # type: ignore
        """
        Override function from SimpleXMLRPCDispatcher to handle coroutines RPC case
        """
        try:
            params, method = loads(data, use_builtin_types=self.use_builtin_types)
            if method is None:
                raise ValueError("Invalid")

            response = await self._dispatch(method, params)
            # wrap response in a singleton tuple
            response = (response,)
            response = dumps(
                response,
                methodresponse=True,
                allow_none=self.allow_none,
                encoding=self.encoding,
            )
        except Fault as fault:
            response = dumps(fault, allow_none=self.allow_none, encoding=self.encoding)
        except Exception as exc:
            # report exception back to server
            response = dumps(
                Fault(1, "%s:%s" % (type(exc), exc)),
                encoding=self.encoding,
                allow_none=self.allow_none,
            )

        return response.encode(self.encoding, "xmlcharrefreplace")

    async def _dispatch(  # type: ignore
        self, method: str, params: Iterable[_Marshallable]
    ) -> _Marshallable:  # type: ignore
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
                if hasattr(self.instance, "_dispatch"):
                    resp = await self.instance._dispatch(method, params)
                    if inspect.iscoroutine(self.instance._dispatch):
                        return await resp
                    else:
                        return resp
                else:
                    # call instance method directly
                    try:
                        func = server.resolve_dotted_attribute(
                            self.instance,
                            method,
                            getattr(self, "allow_dotted_names", True),
                        )
                    except AttributeError:
                        pass

        if func is not None:
            result = func(*params)
            if inspect.iscoroutine(result):
                return await result
            else:
                return result
        else:
            raise Exception('method "%s" is not supported' % method)

    async def system_multicall(self, call_list: list[dict[str, _Marshallable]]):  # type: ignore
        async def handle_call(call: dict[str, _Marshallable]) -> _Marshallable:
            method_name = call["methodName"]
            params = call["params"]

            try:
                result = await self._dispatch(method_name, params)
                return [result]
            except Fault as fault:
                return {"faultCode": fault.faultCode, "faultString": fault.faultString}
            except BaseException as exc:
                return {"faultCode": 1, "faultString": f"{type(exc).__name__}:{exc}"}

        return await asyncio.gather(*(handle_call(call) for call in call_list))


class SimpleXMLRPCServer(SimpleXMLRPCDispatcher):
    rpc_paths = ["/", "/RPC2", "/xmlrpc"]

    def __init__(
        self,
        addr: Tuple[str, int],
        logRequests: bool = True,
        allow_none: bool = False,
        encoding: str | None = None,
        use_builtin_types: bool = False,
    ) -> None:
        super().__init__(allow_none, encoding, use_builtin_types)
        self.host, self.port = addr
        self.logRequests = logRequests
        self.app = Starlette(
            routes=[
                Route(route, self.handle_xmlrpc, methods=["POST"])
                for route in self.rpc_paths
            ],
        )

    async def handle_xmlrpc(self, request: Request) -> Response:
        body = await request.body()
        response = await self._marshaled_dispatch(body.decode())
        return Response(response, media_type="text/xml")

    def serve_forever(self) -> asyncio.Task[Any]:
        config = uvicorn.Config(
            self.app, host=self.host, port=self.port, log_level="error", loop="asyncio"
        )
        self.server = uvicorn.Server(config)
        return asyncio.create_task(self.server.serve())

    @overload  # type: ignore
    def register_function(
        self, function: Callable[..., _Marshallable], name: Optional[str] = None
    ) -> Callable[..., _Marshallable]: ...

    @overload
    def register_function(
        self,
        function: Coroutine[Awaitable[_Marshallable], Any, Any],
        name: Optional[str] = None,
    ) -> Coroutine[Awaitable[_Marshallable], Any, Any]: ...

    def register_function(  # type: ignore
        self,
        function: Any,
        name: Optional[str] = None,
    ) -> Any:
        super().register_function(function, name)

    async def __aenter__(self) -> "SimpleXMLRPCServer":
        return self

    def __enter__(self) -> "SimpleXMLRPCServer":
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None: ...

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None: ...
