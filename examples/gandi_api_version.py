import asyncio

from aioxmlrpc.client import ServerProxy

ENDPOINT = 'https://rpc.gandi.net/xmlrpc/'


async def main():

    async with ServerProxy(ENDPOINT, allow_none=True) as client:
        for _ in range(5):
            data = await client.version.info()
            print(data)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
