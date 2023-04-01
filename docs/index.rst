.. spike-mock documentation master file, created by
   sphinx-quickstart on Mon Mar 20 18:41:03 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to spike-mock's documentation!
======================================

This document is a user manual providing information on how to use spike mock to
build synthetic robot scenario. This library has been designed with the purpose of
validating robot displacement code on controlled data and in a controlled
environment where logging and debugging are easier.

It is in no way an alternative to testing on the real hardware, it's more a
way to separate variables when developing and debugging. It provides a way to make
sure the tested code works as it is expected to in theory and is mature enough before
confronting it to real life experiments where many factors may impact performances and behaviour.

.. toctree::
   :caption: Using spike mock
   :maxdepth: 1

   installation
   getting_started
   design
   configuration
   test
   limitations

.. toctree::
   :caption: Spike library mocking API reference:
   :hidden:

   api

.. toctree::
   :caption: Synthetic scenario management API reference:
   :hidden:

   api2
