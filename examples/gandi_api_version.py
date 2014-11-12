import asyncio
import sys

from aioxmlrpc.client import ServerProxy


@asyncio.coroutine
def routine(future, endpoint, apikey):
    api = ServerProxy(endpoint, allow_none=True)
    result = yield from api.version.info(apikey)
    future.set_result(result)


def main(argv=sys.argv):
    endpoint = 'https://rpc.gandi.net/xmlrpc/'
    apikey = None  # your API KEY here
    future = asyncio.Future()
    loop = asyncio.get_event_loop()
    asyncio.async(routine(future, endpoint, apikey))
    loop.run_until_complete(future)
    print(future.result())
    loop.stop()

if __name__ == '__main__':
    main()

