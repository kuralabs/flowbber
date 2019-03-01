.. toctree::

===============
Developer Guide
===============


Setup Development Environment
=============================

Using Docker
------------

A ready to be used development environment with all dependencies is available
as a Docker_ image under the name ``kuralabs/flowbber:latest``.

To start the development environment, execute the following command in the
Flowbber repository root:

.. code-block:: sh

   docker run -it \
       --env http_proxy=${http_proxy} \
       --env https_proxy=${https_proxy} \
       --env no_proxy=${no_proxy} \
       --volume $(pwd):/ws \
       kuralabs/flowbber:latest bash
   cd /ws


.. _Docker: https://hub.docker.com/search/?type=edition&offering=community&operating_system=linux


Manually
--------

#. Install ``pip3`` and development dependencies:

   .. code-block:: sh

      wget https://bootstrap.pypa.io/get-pip.py
      sudo python3 get-pip.py
      sudo pip3 install tox flake8 pep8-naming

#. Install a C/C++ toolchain for native extensions and cythonized binary wheel
   packaging:

   .. code-block:: sh

      sudo apt install python3-dev build-essential cmake graphviz

#. Optionally, it is recommended to install the ``webdev`` package to run a
   development web server from a local directory:

   .. code-block:: sh

      sudo pip3 install webdev
      webdev .tox/doc/tmp/html

#. To run tests, you need a InfluxDB_ database and a MongoDB_ database running
   locally.


.. _InfluxDB: https://www.influxdata.com/
.. _MongoDB: https://www.mongodb.com/


Building Package
================

.. code-block:: sh

   tox -e build

Output will be available at ``dist/``.

- Source distribution: ``flowbber-<version>.tar.gz``.
- Python wheel: ``flowbber-<version>-py3-none-any.whl``
- Binary wheel: ``flowbber-<version>-cp35-cp35m-linux_x86_64.whl``

.. note::

   The tags of the binary wheel will change depending on the interpreter and
   operating system you build the binary wheel on.


Running Test Suite
==================

.. code-block:: sh

   tox -e test

Output will be available at ``.tox/env/tmp/``.

.. code-block:: sh

   webdev .tox/env/tmp/

- Test results: ``tests.xml``.
- Coverage results: ``coverage.xml``.
- Coverage report: ``coverage.html``.


Building Documentation
======================

.. code-block:: sh

   tox -e doc

Output will be available at ``.tox/env/tmp/html``.

.. code-block:: sh

   webdev .tox/env/tmp/html
