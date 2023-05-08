=========
aioxmlrpc
=========

.. image:: https://github.com/mardiros/aioxmlrpc/actions/workflows/main.yml/badge.svg
   :target: https://github.com/mardiros/aioxmlrpc/actions/workflows/main.yml


.. image:: https://codecov.io/gh/mardiros/aioxmlrpc/branch/master/graph/badge.svg?token=BR3KttC9uJ
   :target: https://codecov.io/gh/mardiros/aioxmlrpc


Asyncio version of the standard lib ``xmlrpc``

Currently only ``aioxmlrpc.client``, which works like ``xmlrpc.client`` but
with coroutine is implemented.

Fill free to fork me if you want to implement the server part.


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


Run the example

::

    poetry run examples/gandi_api_version.py

