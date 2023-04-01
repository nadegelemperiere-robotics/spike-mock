=======================================================
FLL bot mocking to emulate scenarii and test functions
=======================================================

About The Project
=================

This project contains python classes emulating lego spike library API

.. image:: https://badgen.net/github/checks/nadegelemperiere/spike-mock
   :target: https://github.com/nadegelemperiere/spike-mock/actions/workflows/release.yml
   :alt: Status
.. image:: https://badgen.net/github/commits/nadegelemperiere/spike-mock/main
   :target: https://github.com/nadegelemperiere/spike-mock
   :alt: Commits
.. image:: https://badgen.net/github/last-commit/nadegelemperiere/spike-mock/main
   :target: https://github.com/nadegelemperiere/spike-mock
   :alt: Last commit

Built And Packaged With
-----------------------

.. image:: https://img.shields.io/static/v1?label=python&message=3.11.0rc1&color=informational
   :target: https://www.python.org/
   :alt: Python

Testing
=======

Tested With
-----------

.. image:: https://img.shields.io/static/v1?label=python&message=3.11.0rc1&color=informational
   :target: https://www.python.org/
   :alt: Python
.. image:: https://img.shields.io/static/v1?label=robotframework&message=6.0.2&color=informational
   :target: http://robotframework.org/
   :alt: Robotframework

How To
------

See `user manual`

.. _`user manual`: docs/manual.rst


Environment
-----------

Tests can be executed in an environment :

* in which python, pip and bash has been installed, by executing the script `scripts/robot.sh`_, or

* in which docker is available, by using the `fll test image`_ in its latest version, which already contains python, pip and bash, by executing the script `scripts/test.sh`_

.. _`fll test image`: https://github.com/nadegelemperiere/fll-test-docker
.. _`scripts/robot.sh`: scripts/robot.sh
.. _`scripts/test.sh`: scripts/test.sh

Results
-------

The test results for latest release are here_

.. _here: https://nadegelemperiere.github.io/spike-mock/report.html


Issues
======

.. image:: https://img.shields.io/github/issues/nadegelemperiere/spike-mock.svg
   :target: https://github.com/nadegelemperiere/spike-mock/issues
   :alt: Open issues
.. image:: https://img.shields.io/github/issues-closed/nadegelemperiere/spike-mock.svg
   :target: https://github.com/nadegelemperiere/spike-mock/issues
   :alt: Closed issues

Known limitations
=================

Roadmap
=======

Next step is to add a mat image to :

- Emulate color sensor
- Display the robot displacement

Contributing
============

.. image:: https://contrib.rocks/image?repo=nadegelemperiere/spike-mock
   :alt: GitHub Contributors Image

Contact
=======

Nadege Lemperiere - nadege.lemperiere@gmail.com

Acknowledgments
===============

[python-ldraw](https://github.com/rienafairefr/python-ldraw)

[robotpy-wpimath](https://robotpy.readthedocs.io/projects/wpimath/en/latest/)