.. toctree::

===============
Developer Guide
===============


Setup Development Environment
=============================

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

Output will be available at ``.tox/test/tmp/``.

.. code-block:: sh

   webdev .tox/doc/tmp/

- Test results: ``tests.xml``.
- Coverage results: ``coverage.xml``.
- Coverage report: ``coverage.html``.


Building Documentation
======================

.. code-block:: sh

   tox -e doc

Output will be available at ``.tox/doc/tmp/html``.

.. code-block:: sh

   webdev .tox/doc/tmp/html
