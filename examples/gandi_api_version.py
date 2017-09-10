import asyncio

from aioxmlrpc.client import ServerProxy

ENDPOINT = 'https://rpc.gandi.net/xmlrpc/'


@asyncio.coroutine
def main():
    client = ServerProxy(ENDPOINT, allow_none=True)
    for _ in range(5):
        data = yield from client.version.info()
        print(data)
    yield from client.close()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
