Configuration
=============

To configure the scenario, the library needs 2 main information

Robot design
````````````

The library needs to know how the robot is built so that it can derive how it moves on the mat.
Those information are centralized on a json configuration file

.. literalinclude:: ../conf/robot.json
  :language: JSON

The **design** entry contains the definition of the robot structure:

- *filename* is the link to the robot `ldraw`_ design file relative to this configuration file
  directory. This file can be obtained from a robot designed in `Studio2.0`_ exported in
  ldraw format.
- *ldu* defines the size of the `ldraw unit` in centimeters

The **abaqus** entry contains the path to the workbook containing the robot abaqus relative to
this configuration file directory. The abaqus contains 2 information in 2 sheets :

- The link between a motor command its angular speed. In spike, it is not linked to the size
  of the motor, both have the same angular speed, though different torque.
- The link between wheels ldraw part identifier and their diameters in centimeters.

Check this `abaqus link`_ to get an example of the current abaqus file format

The **components** entry lists the connection between robot key components. For each component
we give :

- the *type* attribute defining the component type
- the *id* attribute setting the ldraw unique identifier of the component
- the *port* attribute setting the hub port to which the component is connected - In case of the
  wheel, it is the port of the motor moving the wheel
- the *index* attribute setting the index of the component between all the component of the same
  type in the ldraw model
- for wheels only, the *spin* attribute defines the relation between the motor speed and the
  wheel speed. It is negative if the wheel does not rotate in the same direction as the motor
  (due to gears for example) and its absolute value reflects the proportionality between the
  motor speed and the wheel speed (typically the gear ratio)

The ldraw format is managed using a fork of the python-ldraw project, which provides parsing
functions. The use of those parser requires having a database of all useful lego parts available
when using the library. You must build a folder structure such as :

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

The `ldraw for developers`_ website provides a basic database with the tools to generate the
parts.lst file from the content of p and parts. Sadly, the spike parts are not included in this
database. The spike parts can be retrieved in the configuration folder of Studio2.0 once installed
on a local endpoint, and the parts.list can then be rebuilt using the tool provided by ldraw.

Finally, a configuration file shall define the path of the database so that the library python-ldraw
can discover it. This file shall be copied locally in ~/.config/pyldraw/config.yml.

.. literalinclude:: ../conf/config.yml
  :language: yaml

Scenario Context
````````````````

The library enable to choose the way the sensors measures are computed and delivered to the library
interface.

For a better mastering of the scenario, the user has the choice between playing it in real time
which is closer to what happens on the hub, or in time controlled mode, when the user chooses
when the time pass and to what extent.


.. literalinclude:: ../conf/scenario.json
  :language: JSON


The **data** entry defines the way data are fed to the components:

- *mode* enables to choose between "compute" and "read". In *read* mode, the components
  measurements are all directly read from a workbook and fed to the components. No API calling
  can change those measurements. In *compute* mode, the components measurements are derived
  from the robots kinematics that are directly impacted by the robot commands.
- *coordinates* [compute only] sets the robot starting coordinates for the scenario
- *filename* [read only] gives the path to a workbook containing the data to feed the components


The **time** entry defines the way the time passes during a scenario :

- *mode* enables to choose between "realtime" and "controlled". In *readtime* mode, the time
  is given by the clock located on the execution endpoint, as it would do on the real spike hub.
  The processing time of the algorithms then impacts the measurement frequency
  In *controlled time*, the time increases when the user decides it.
- *period* [controlled only] sets the number of seconds passing at each scenario steps


.. _`ldraw`: https://www.ldraw.org/
.. _`ldraw unit`: https://brickwiki.org/wiki/LDraw_unit
.. _`Studio2.0`: https://www.bricklink.com/v3/studio/download.page
.. _`abaqus link`: https://github.com/nadegelemperiere/spike-mock/blob/main/conf/abaqus.xlsx
.. _`ldraw for developers`: https://www.ldraw.org/parts/direct-parts-access.html