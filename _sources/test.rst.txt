Tests
=====

`Latest release tests results`_

Dynamics test suite
-------------------

The dynamics tests suite validates that the robot displacement and its impact on sensors are correctly
modelled in the scenario library. It :

- reads the scenario data and expected robot measurements from an excel workbook
- launches the scenario according to the parameters defined in the workbook
- compare the results to the measurements defined in the workbook

Therefore, adding new tests cases are easy : it only requires to add new lines in the workbook sheet
corresponding to the function that should be tested. The woorkbook contains visual basic macros and
formulas which will derive the reuslting measurements to expect according to the new scenario data.


.. _`Latest release tests results`: report.html