import asyncio
from datetime import datetime
import socket
from math import pow

import pytest

from aioxmlrpc.client import ServerProxy
from aioxmlrpc.server import SimpleXMLRPCServer


async def wait_for_socket(
    host: str, port: int, timeout: int = 5, poll_time: float = 0.1
):
    """Wait until the socket is open, or raise an error if the timeout is exceeded."""
    for _ in range(timeout * int(1 / poll_time)):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            if sock.connect_ex((host, port)) == 0:
                break
        await asyncio.sleep(poll_time)
    else:
        raise RuntimeError(f"Server on {host}:{port} did not start in time.")


async def multiply(a: int, b: int) -> int:
    await asyncio.sleep(0)
    return a * b


class ExampleService:
    def get_data(self):
        return "42"

    class dt:
        @staticmethod
        def now():
            return datetime.today()


@pytest.fixture
async def server():
    addr = ("localhost", 8000)
    async with SimpleXMLRPCServer(addr) as server:
        server.register_function(pow)
        server.register_function(multiply)
        server.register_function(lambda x, y: x + y, "add")  # type: ignore
        server.register_instance(ExampleService(), allow_dotted_names=True)
        server.register_multicall_functions()

        task = server.serve_forever()
        await wait_for_socket(*addr)
        yield "http://localhost:8000/RPC2"

        server.server.should_exit = True
        await task


@pytest.fixture
async def client(server: str) -> ServerProxy:
    return ServerProxy(server)
