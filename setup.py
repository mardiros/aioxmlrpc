import os
import re
import sys

from setuptools import setup, find_packages

py_version = sys.version_info[:2]
if py_version < (3, 3):
    raise RuntimeError('Unsupported Python version. Python 3.3+ required')

here = os.path.abspath(os.path.dirname(__file__))
NAME = 'aioxmlrpc'
with open(os.path.join(here, 'README.rst')) as readme:
    README = readme.read()
with open(os.path.join(here, 'CHANGES.rst')) as changes:
    CHANGES = changes.read()

with open(os.path.join(here, NAME, '__init__.py')) as version:
    VERSION = re.compile(r".*__version__ = '(.*?)'",
                         re.S).match(version.read()).group(1)


requires = ['aiohttp >= 0.20']
if py_version < (3, 4):
    requires.append('asyncio')


setup(name=NAME,
      version=VERSION,
      description='XML-RPC client for asyncio',
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
          'Programming Language :: Python',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Environment :: Web Environment',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License'
          ],
      author='Guillaume Gauvrit',
      author_email='guillaume@gauvr.it',
      url='https://github.com/mardiros/aioxmlrpc',
      keywords='asyncio xml-rpc rpc',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='{}.tests'.format(NAME),
      install_requires=requires
      )
