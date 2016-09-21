import asyncio
import aioxmlrpc.server
from xmlrpc.server import SimpleXMLRPCDispatcher

def toto():
    return True

if __name__ == "__main__":
    dispatcher = SimpleXMLRPCDispatcher()
    dispatcher.register_function(toto)
    loop = asyncio.get_event_loop()
    f = loop.create_server(
        lambda: aioxmlrpc.server.SimpleXMLRPCRequestHandler(dispatcher=dispatcher, debug=True, keep_alive=75),
        '0.0.0.0', '8080')
    srv = loop.run_until_complete(f)
    print('serving on', srv.sockets[0].getsockname())
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass