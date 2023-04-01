Getting started
===============

This section describes how to do a quick start on using this mock library from small ajustments
in an already defined configuration. Adapting to a specific context, especially to a new robot
design will require to deep down into the detailed configuration section.

Environment
```````````

To get an environment in which you can easily perform your first test on the spike mock library,
download the docker image we use for testing. If you need more information on the docker image
content, check our github repository `fll-test-docker`_

.. code-block:: bash

    docker pull nadegelemperiere/fll-test-docker:latest

Configuration
`````````````

Example of configuration files can be found in the repository `configuration folder`_, including :

- A robot `ldraw`_ design file and the associated `Studio2.0`_ file that enables its exported.
- A scenario file configured to :

  - compute robot movements according to the command we give it
  - let time pass according to the endpoint clock

To parse ldraw files, a ldraw parts database shall be available locally, which includes the
lego spike parts we use in our robot model. Such a database can be found in the installation
folder of Studio2.0, merging *C:\Program Files\Studio 2.0\ldraw* and
*C:\Program Files\Studio 2.0\ldraw\UnOfficial*. Ldraw provides a tool to generate a global
parts.lst file from the parts folders `here`. Arrange the database as shown below :

::

    database
    ├── parts.lst
    ├── parts
    │   ├── 1.dat
    │   └── 2.dat
    │   └── ...
    ├── p
    │   ├── 1-4ccyli.dat
    │   └── 1-4cchrd.dat
    │   └── ...

.. _`here`: https://www.ldraw.org/parts/direct-parts-access.html


Run
---

To run the mock library on a spike code,

.. code-block:: bash

docker run  -it --rm \
            --volume $scriptpath/../:/package:rw \
            --volume $scriptpath/../../ldraw-parts:/parts:ro \
            --workdir /package \
            nadegelemperiere/fll-test-docker:latest  \
            ./scripts/robot.sh $@

Analysis
--------


.. _`ldraw`: https://www.ldraw.org/
.. _`Studio2.0`: https://www.bricklink.com/v3/studio/download.page
.. _`fll-test-docker`: https://github.com/nadegelemperiere/fll-test-docker
.. _`configuration folder`: https://github.com/nadegelemperiere/spike-mock/tree/main/conf