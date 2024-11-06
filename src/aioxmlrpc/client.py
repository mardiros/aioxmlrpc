"""
XML-RPC Client with asyncio.

This module adapt the ``xmlrpc.client`` module of the standard library to
work with asyncio.

"""

import asyncio
import logging
from typing import (
    Any,
    Awaitable,
    Callable,
    Optional,
    cast,
)
from xmlrpc import client as xmlrpc

import httpx

__ALL__ = ["ServerProxy", "Fault", "ProtocolError"]

RPCResult = Any
RPCParameters = Any

# you don't have to import xmlrpc.client from your code
Fault = xmlrpc.Fault
ProtocolError = xmlrpc.ProtocolError

log = logging.getLogger(__name__)


class _Method:
    # some magic to bind an XML-RPC method to an RPC server.
    # supports "nested" methods (e.g. examples.getStateName)
    def __init__(
        self, send: Callable[[str, RPCParameters], Awaitable[RPCResult]], name: str
    ) -> None:
        self.__send = send
        self.__name = name

    def __getattr__(self, name: str) -> "_Method":
        return _Method(self.__send, "%s.%s" % (self.__name, name))

    async def __call__(self, *args: RPCParameters) -> RPCResult:
        ret = await self.__send(self.__name, args)
        return ret


class AioTransport(xmlrpc.Transport):
    """
    ``xmlrpc.Transport`` subclass for asyncio support
    """

    def __init__(
        self,
        session: httpx.AsyncClient,
        use_https: bool,
        *,
        use_datetime: bool = False,
        use_builtin_types: bool = False,
        auth: Optional[httpx._types.AuthTypes] = None,
        timeout: Optional[httpx._types.TimeoutTypes] = None,
    ):
        super().__init__(use_datetime, use_builtin_types)
        self.use_https = use_https
        self._session = session

        self.auth = auth or httpx.USE_CLIENT_DEFAULT
        self.timeout = timeout

    async def request(  # type: ignore
        self,
        host: str,
        handler: str,
        request_body: dict[str, Any],
        verbose: bool = False,
    ) -> RPCResult:
        """
        Send the XML-RPC request, return the response.
        This method is a coroutine.
        """
        url = self._build_url(host, handler)
        response = None
        try:
            response = await self._session.post(
                url,
                data=request_body,
                auth=self.auth,
                timeout=self.timeout,
            )
            body = response.text
            if response.status_code != 200:
                raise ProtocolError(
                    url,
                    response.status_code,
                    body,
                    # response.headers is a case insensitive dict from httpx,
                    # the ProtocolError is typed as simple dict
                    cast(dict[str, str], response.headers),
                )
        except asyncio.CancelledError:
            raise
        except ProtocolError:
            raise
        except Exception as exc:
            log.error("Unexpected error", exc_info=True)
            if response is not None:
                errcode = response.status_code
                headers = cast(dict[str, str], response.headers)
            else:
                errcode = 0
                headers = {}

            raise ProtocolError(url, errcode, str(exc), headers)
        return self.parse_response(body)

    def parse_response(  # type: ignore
        self,
        body: str,
    ) -> RPCResult:
        """
        Parse the xmlrpc response.
        """
        p, u = self.getparser()
        p.feed(body)
        p.close()
        return u.close()

    def _build_url(self, host: str, handler: str) -> str:
        """
        Build a url for our request based on the host, handler and use_http
        property
        """
        scheme = "https" if self.use_https else "http"
        return f"{scheme}://{host}{handler}"


class ServerProxy(xmlrpc.ServerProxy):
    """
    ``xmlrpc.ServerProxy`` subclass for asyncio support
    """

    def __init__(
        self,
        uri: str,
        encoding: Optional[str] = None,
        verbose: bool = False,
        allow_none: bool = False,
        use_datetime: bool = False,
        use_builtin_types: bool = False,
        auth: Optional[httpx._types.AuthTypes] = None,
        *,
        headers: Optional[dict[str, Any]] = None,
        context: Optional[httpx._types.VerifyTypes] = None,
        timeout: httpx._types.TimeoutTypes = 5.0,
        session: Optional[httpx.AsyncClient] = None,
    ) -> None:
        if not headers:
            headers = {
                "User-Agent": "python/aioxmlrpc",
                "Accept": "text/xml",
                "Content-Type": "text/xml",
            }
        if context is None:
            context = True
        self._session = session or httpx.AsyncClient(headers=headers, verify=context)
        transport = AioTransport(
            use_https=uri.startswith("https://"),
            session=self._session,
            auth=auth,
            timeout=timeout,
            use_datetime=use_datetime,
            use_builtin_types=use_builtin_types,
        )

        super().__init__(
            uri,
            transport,
            encoding,
            verbose,
            allow_none,
            use_datetime,
            use_builtin_types,
        )

    async def __request(  # type: ignore
        self,
        methodname: str,
        params: RPCParameters,
    ) -> RPCResult:
        # call a method on the remote server
        request = xmlrpc.dumps(
            params, methodname, encoding=self.__encoding, allow_none=self.__allow_none
        ).encode(self.__encoding)

        response = await self.__transport.request(  # type: ignore
            self.__host, self.__handler, request, verbose=self.__verbose
        )

        if len(response) == 1:  # type: ignore
            response = response[0]

        return response

    def __getattr__(self, name: str) -> _Method:  # type: ignore
        return _Method(self.__request, name)
