=========
aioxmlrpc
=========

.. image:: https://github.com/mardiros/aioxmlrpc/actions/workflows/tests.yml/badge.svg
   :target: https://github.com/mardiros/aioxmlrpc/actions/workflows/tests.yml


.. image:: https://codecov.io/gh/mardiros/aioxmlrpc/branch/master/graph/badge.svg?token=BR3KttC9uJ
   :target: https://codecov.io/gh/mardiros/aioxmlrpc


Asyncio version of the standard lib ``xmlrpc``

``aioxmlrpc.client``, which works like ``xmlrpc.client`` but uses coroutines,
has been implemented.

``aioxmlrpc.server``, which works pretty much like ``xmlrpc.server`` but
can be run in asyncio loop and handle normal remote procedure call (RPC) and remote coroutines call (RCC).

``aioxmlrpc`` is based on ``httpx`` for the transport, and just patch
the necessary from the python standard library to get it working.


Installation
------------

aioxmlrpc is available on PyPI, it can simply be installed with your favorite
tool, example with pip here.

::

    pip install aioxmlrpc


Getting Started
---------------

Client
~~~~~~

This example show how to print the current version of the Gandi XML-RPC api.


::

    import asyncio
    from aioxmlrpc.client import ServerProxy


    async def print_gandi_api_version():
        api = ServerProxy('https://rpc.gandi.net/xmlrpc/')
        result = await api.version.info()
        print(result)

    if __name__ == '__main__':
        loop = asyncio.get_event_loop()
        loop.run_until_complete(print_gandi_api_version())
        loop.stop()


Run the example

::

    uv run examples/gandi_api_version.py


Server
~~~~~~

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
