0.9.0  - Released on 2024-11-06
-------------------------------
* Add typing.
* Breaking change: drop support of python 3.7 and python 3.8.
* Switch packaging to uv / pdm.
* CI update
* Update LICENSE to MIT

0.8.1  - Released on 2024-04-25
-------------------------------
* Add PEP-517 metadata in python package

0.8.0  - Released on 2024-04-09
-------------------------------
* Update dependencies

0.7.0 - Released on 2023-05-08
------------------------------
* New feature: Add missing context kwargs argument for ServerProxy compatibility.
* Breaking change: Argument headers must be a kwargs like in the standard library.
* Breaking change: Non standard arguments timeout and session must be kwargs too.
* Update dependencies

0.6.5 - Released on 2023-04-27
------------------------------
* Update dependencies

0.6.4 - Released on 2022-06-02
------------------------------
* Update dependencies

0.6.3 released on 2021-12-15
----------------------------
* Fix ProtocolError

0.6.2 released on 2021-12-13
----------------------------
* Update httpx to ^0.21.1
* Switch CI to github action

0.6.1 released on 2021-10-06
----------------------------
* Switch to httpx

0.5 released on 2017-09-10
--------------------------
* Remove compatibility with aiohttp < 1.0 (Ovv)

0.4 released on 2017-03-30
--------------------------
* Fix NXDOMAIN Exception handling (Vladimir Rutsky)
* Fix cancel of futures handling (Gustavo Tavares Cabral)

0.3 released on 2016-06-16
--------------------------
* Fix socket closing issue


0.2 released on 2016-05-26
--------------------------
* Update compatibility for aiohttp >= 0.20

.. important::

   This break the compatibility of python 3.3


0.1 released on 2014-05-17
--------------------------
* Initial version implementing ``aioxmlrpc.client``
