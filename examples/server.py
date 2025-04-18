import asyncio
from aioxmlrpc.server import SimpleXMLRPCServer


class Api:
    def info(self):
        return "1.0.0"

    async def sleep(self):
        await asyncio.sleep(1)
        return "done"


async def main():
    server = SimpleXMLRPCServer(("0.0.0.0", 8080))
    server.register_instance(Api(), allow_dotted_names=True)
    await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())
