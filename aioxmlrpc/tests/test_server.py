import asyncio
from aioxmlrpc.server import SimpleXMLRPCServer


class Api:
    def info(self):
        return "1.0.0"

if __name__ == "__main__":
    server = SimpleXMLRPCServer()
    server.register_instance(Api(), allow_dotted_names=True)
    loop = asyncio.get_event_loop()
    f = loop.create_server(lambda: server.request_handler(debug=True, keep_alive=75), '0.0.0.0', '8080')
    loop.run_until_complete(f)
    loop.run_forever()