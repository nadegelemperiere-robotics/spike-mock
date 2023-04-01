# -------------------------------------------------------
# Copyright (c) [2022] Nadege LEMPERIERE
# All rights reserved
# -------------------------------------------------------
""" Force sensor mock APi """
# -------------------------------------------------------
# Nadège LEMPERIERE,  @04 november 2022
# Latest revision: 04 november 2022
# -------------------------------------------------------

# Standard includes
from time import sleep
from threading import Lock

# Local includes
from spike.scenario.scenario import Scenario

class ForceSensor() :
    """ Force sensor mocking class


        Class is accessed simultaneously by the user side thread and the
        ground truth update thread. It is therefore protected by a mutex
    """

    # Constants
    s_force_for_being_pressed   = 2
    s_max_force                 = 10

    # Static variables
    s_shared_scenario           = Scenario()

####################################### SPIKE API METHODS ########################################

    def __init__(self, port) :
        """
        Contructor

        :param port: the hub port to which the sensor is connected
        :type port:  string ('A','B','C','D','E' or 'F')
        """

        self.__mutex        = Lock()
        self.__port         = None

        self.__force        = 0

        self.s_shared_scenario.register(self, port)

    def wait_until_pressed(self) :
        """ Waits until the Force Sensor is pressed. """

        while self.get_force_newton() < self.s_force_for_being_pressed :
            sleep(0.01)

    def wait_until_released(self) :
        """ Waits until the Force Sensor is released. """

        while self.get_force_newton() >= self.s_force_for_being_pressed :
            sleep(0.01)

    def is_pressed(self) :
        """
        Tests whether the button on the sensor is pressed.

        :return: True if the sensor is pressed, False otherwise
        :rtype:  boolean
        """
        return self.get_force_newton() >= self.s_force_for_being_pressed

    def get_force_newton(self) :
        """
        Retrieves the measured force, in newtons.

        :return: the measured force, specified in newtons
        :rtype:  float
        """
        result = 0
        with self.__mutex :
            result = self.__force
        return result

    def get_force_percentage(self) :
        """
        Retrieves the measured force as a percentage of the maximum force.

        :return: the measured force, given as a percentage.
        :rtype:  integer [0,100]
        """
        return int(round(self.get_force_newton() * 100 / self.s_max_force))

######################################## SCENARIO METHODS ########################################

    def c_reset(self) :
        """
        Reset function

        .. warning:: This function is not part of the spike API. It is provided to update the
         component from scenario data and shall not be used by the end-user.
        """
        with self.__mutex :
            self.__force        = 0

    def c_read(self, force) :
        """
        Update the force from scenario data

        .. warning:: This function is not part of the spike API. It is provided to update the
         component from scenario data and shall not be used by the end-user.

        :param force: force in newton
        :type force:  integer
        """
        with self.__mutex :
            self.__force  = force

# pylint: disable=R0801
    @property
    def port(self) :
        """
        Sets the component connection port

        .. warning:: This function is not part of the spike API. It is provided to update the
         component from scenario data and shall not be used by the end-user.

        :param port: the component port
        :type port:  string
        """
        result = None
        with self.__mutex :
            result = self.__port
        return result

    @port.setter
    def port(self, port) :
        """ Sets the component connection port

        .. warning:: This function is not part of the spike API. It is provided to update the
         component from scenario data and shall not be used by the end-user.

        :param port: the component port
        :type port:  string
        """
        with self.__mutex :
            self.__port = port
# pylint: enable=R0801
