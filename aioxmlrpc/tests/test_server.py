import asyncio
from aioxmlrpc.server import SimpleXMLRPCDispatcher, SimpleXMLRPCRequestHandler


class Version:
    def info(self):
        return "1.0.0"


class Api:
    def __init__(self):
        self.version = Version()

if __name__ == "__main__":
    dispatcher = SimpleXMLRPCDispatcher()
    dispatcher.register_instance(Api(), allow_dotted_names=True)
    loop = asyncio.get_event_loop()
    f = loop.create_server(
        lambda: SimpleXMLRPCRequestHandler(dispatcher=dispatcher, debug=True, keep_alive=75),
        '0.0.0.0', '8080')
    loop.run_until_complete(f)
    loop.run_forever()