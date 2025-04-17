=========
aioxmlrpc
=========


.. image:: https://travis-ci.org/mardiros/aioxmlrpc.png?branch=master
   :target: https://travis-ci.org/mardiros/aioxmlrpc


Getting Started
===============

Asyncio version of the standard lib ``xmlrpc``

``aioxmlrpc.client``, which works like ``xmlrpc.client`` but
with coroutine is implemented.

``aioxmlrpc.server``, which works pretty much like ``xmlrpc.server`` but
can be run in asyncio loop and handle normal remote procedure call (RPC) and remote coroutines call (RCC).

``aioxmlrpc`` is based on ``aiohttp`` for the transport, and just patch
the necessary from the python standard library to get it working.


Installation
------------

::

    pip install aioxmlrpc


Example of usage
----------------

This example show how to print the current version of the Gandi XML-RPC api.


::

    import asyncio
    from aioxmlrpc.client import ServerProxy


    @asyncio.coroutine
    def print_gandi_api_version():
        api = ServerProxy('https://rpc.gandi.net/xmlrpc/')
        result = yield from api.version.info()
        print(result)

    if __name__ == '__main__':
        loop = asyncio.get_event_loop()
        loop.run_until_complete(print_gandi_api_version())
        loop.stop()


Exemple of usage
----------------

This example show an exemple of the server side.


::

   import asyncio
   from aioxmlrpc.server import SimpleXMLRPCServer


   class Api:
       def info(self):
           return "1.0.0"
       @asyncio.coroutine
       def sleep(self):
            yield from asyncio.sleep(1)
            return "done"

   if __name__ == "__main__":
       server = SimpleXMLRPCServer()
       server.register_instance(Api(), allow_dotted_names=True)
       loop = asyncio.get_event_loop()
       f = loop.create_server(lambda: server.request_handler(debug=True, keep_alive=75), '0.0.0.0', '8080')
       loop.run_until_complete(f)
       loop.run_forever()

