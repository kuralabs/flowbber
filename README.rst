======================================
Flowbber - The Data Pipeline Framework
======================================

Flowbber is a generic tool and framework that allows to execute custom
pipelines for data gathering, publishing and analysis.


Documentation
=============

    https://docs.kuralabs.io/flowbber/


Install
=======

.. code-block:: sh

    pip3 install flowbber


Changelog
=========

1.1.0 (2017-09-07)
------------------

New
~~~

- Added "optional" and "timeout" features to pipeline components.

Changes
~~~~~~~

- Git helpers now live into its own utilities module ``flowbber.utils.git``.

Fixes
~~~~~

- Fixed bug where pipeline execution counter didn't increment.


1.0.0 (2017-08-30)
------------------

New
~~~

- Initial version.


License
=======

::

   Copyright (C) 2017 KuraLabs S.R.L

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing,
   software distributed under the License is distributed on an
   "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
   KIND, either express or implied.  See the License for the
   specific language governing permissions and limitations
   under the License.
