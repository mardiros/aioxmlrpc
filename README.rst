=========
aioxmlrpc
=========


.. image:: https://travis-ci.org/mardiros/aioxmlrpc.png?branch=master
   :target: https://travis-ci.org/mardiros/aioxmlrpc


Getting Started
===============

Asyncio version of the standard lib ``xmlrpc``

Currently only ``aioxmlrpc.client``, which works like ``xmlrpc.client`` but
with coroutine is implemented.

Fill free to fork me if you want to implement the server part.


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
