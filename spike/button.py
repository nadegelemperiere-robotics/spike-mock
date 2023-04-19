# -------------------------------------------------------
# Copyright (c) [2022] Nadege LEMPERIERE
# All rights reserved
# -------------------------------------------------------
""" Hub button mock API """
# -------------------------------------------------------
# Nadège LEMPERIERE, @04 november 2022
# Latest revision: 04 november 2022
# -------------------------------------------------------

# Standard includes
from time import sleep
from threading import Lock

# Local includes
from spike.scenario.scenario import Scenario

class Button() :
    """ Hub button mocking class.

        Class is accessed simultaneously by the user side thread and the
        ground truth update thread. It is therefore protected by a mutex
    """

    # Constants
    s_sides        = ['left', 'right']

    # Static variables
    s_shared_scenario = Scenario()

####################################### SPIKE API METHODS ########################################

    def __init__(self, side) :
        """
        Contructor

        :param side: button side (left or right)
        :type side:  string
        """

        self.__mutex        = Lock()

        self.__is_pressed   = False
        self.__was_pressed  = False
        self.__side         = ""
        self.s_shared_scenario.register(self, side)

    def wait_until_pressed(self) :
        """ Wait until the button is pressed"""
        while not self.is_pressed() : sleep(0.01)

    def wait_until_released(self) :
        """ Wait until the button is released"""
        while self.is_pressed() :   sleep(0.01)

    def was_pressed(self) :
        """
        Tests to see whether the button has been pressed since the last time this method called.
        Once this method returns "true," the button must be released and pressed again before it
        will return "true" again.

        :return: True if the button was pressed, false otherwise
        :rtype:  boolean
        """

        result = None
        with self.__mutex :
            result = self.__was_pressed
            self.__was_pressed = False

        return result

    def is_pressed(self) :
        """
        Tests whether the button is pressed.

        :return: True if the button is pressed, otherwise false
        :rtype:  boolean
        """

        result = None
        with self.__mutex :
            result = self.__is_pressed
        return result

######################################## SCENARIO METHODS ########################################

    def c_reset(self) :
        """
        Reset function

        .. warning:: This function is not part of the spike API. It is provided to update the
         component from scenario data and shall not be used by the end-user.

        """
        with self.__mutex :
            self.__is_pressed   = False
            self.__was_pressed  = False

    def c_read(self, is_pressed) :
        """
        Button status setting function

        .. warning:: This function is not part of the spike API. It is provided to update the
         component from scenario data and shall not be used by the end-user.

        :param is_pressed: True if button is pressed, false otherwise
        :type is_pressed:  boolean
        """
        with self.__mutex :
            self.__is_pressed = is_pressed
            if not self.__was_pressed :
                self.__was_pressed = self.__is_pressed

    @property
    def side(self) :
        """ Get the component side

        .. warning:: This function is not part of the spike API. It is provided to update the
         component from scenario data and shall not be used by the end-user.

        :return: the component side
        :rtype:  string
        """
        result = None
        with self.__mutex :
            result = self.__side
        return result

    @side.setter
    def side(self, side) :
        """ Sets the component side

        .. warning:: This function is not part of the spike API. It is provided to update the
         component from scenario data and shall not be used by the end-user.

        :param port: the component side
        :type port:  string
        """
        with self.__mutex :
            self.__side = side
