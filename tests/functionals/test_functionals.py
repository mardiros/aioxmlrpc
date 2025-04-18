from datetime import datetime
from aioxmlrpc.client import ServerProxy


async def test_method(client: ServerProxy):
    assert await client.pow(4, 2) == 16


async def test_lambda(client: ServerProxy):
    assert await client.add(4, 2) == 6


async def test_coroutine(client: ServerProxy):
    assert await client.multiply(4, 2) == 8


async def test_dotted(client: ServerProxy):
    assert await client.get_data() == "42"
    assert await client.dt.now() == datetime.today()
