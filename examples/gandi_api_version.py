#!/usr/bin/env python
import asyncio

from aioxmlrpc.client import ServerProxy

ENDPOINT = "https://rpc.gandi.net/xmlrpc/"


async def main():
    client = ServerProxy(ENDPOINT, allow_none=True)
    for _ in range(5):
        data = await client.version.info()
        print(data)


if __name__ == "__main__":
    asyncio.run(main())
