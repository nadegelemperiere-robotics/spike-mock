# -------------------------------------------------------
# Copyright (c) [2022] Nadege LEMPERIERE
# All rights reserved
# -------------------------------------------------------
""" Hub status light mock API """
# -------------------------------------------------------
# Nadège LEMPERIERE, @04 november 2022
# Latest revision: 04 november 2022
# -------------------------------------------------------

# System includes
from threading import Lock
from time      import sleep

# Local includes
from spike.scenario.scenario import Scenario
from spike.scenario.timer    import ScenarioTimer

# pylint: disable=R0801
class StatusLight() :
    """ Hub status light mocking class

        Class is accessed simultaneously by the user side thread and the
        ground truth update thread. It is therefore protected by a mutex
    """

    # Constants
    s_status_light_colors = [
        'azure','black','blue','cyan','green','orange','pink','red','violet','yellow','white',
    ]

    # Static variables
    s_shared_scenario  = Scenario()
    s_shared_timer     = ScenarioTimer()

####################################### SPIKE API METHODS ########################################

    def __init__(self) :
        """ Contructor """

        self.__mutex   = Lock()

        self.__color   = 'white'
        self.__is_on   = False

        self.s_shared_scenario.register(self)

# pylint: disable=C0103
    def on(self, color='white') :
        """
        Sets the color of the light


        :param color: the light color
        :type color:  string

        :raises TypeError: color is not a string
        :raises ValueError: color is not one of the allowed values
        """

        if not isinstance(color, str) :
            raise TypeError('color is not a string')
        if color not in self.s_status_light_colors :
            raise ValueError('color is not one of the allowed values')

        command = self.s_shared_scenario.command(self,'on',{
            'color'    : color,
        })
        self.__process_command(command)

# pylint: enable=C0103

    def off(self) :
        """ Turns off the light"""

        command = self.s_shared_scenario.command(self,'off',{})
        self.__process_command(command)

    def __process_command(self, command) :
        """
        Process command until over

        :param command: command to process
        :type command: generator function
        """

        shall_continue = next(command)
        while shall_continue :
            sleep(self.s_shared_timer.s_sleep_time)
            shall_continue = next(command)

######################################## SCENARIO METHODS ########################################

    def c_reset(self) :
        """ Reset function

        .. warning:: This function is not part of the spike API. It is provided to update the
         component from scenario data and shall not be used by the end-user. """
        with self.__mutex :
            self.__color   = 'white'
            self.__is_on   = False

    def c_read(self, is_on, color) :
        """ Switch on function

        .. warning:: This function is not part of the spike API. It is provided to update the
         component from scenario data and shall not be used by the end-user.

        :param is_on: The light status
        :type is_on:  boolean
        :param color: The light color
        :type color:  string
        """
        with self.__mutex :
            self.__color = color
            self.__is_on = is_on

    def c_get_color(self) :
        """
        Returns current color

        .. warning:: This function is not part of the spike API. It is provided to update the
         component from scenario data and shall not be used by the end-user.

        :return: the light current color
        :rtype:  string
        """
        with self.__mutex :
            result = self.__color
        return result

    def c_get_status(self) :
        """
        Returns current status

        .. warning:: This function is not part of the spike API. It is provided to update the
         component from scenario data and shall not be used by the end-user.

        :return: True if light is on, false otherwise
        :rtype:  string
        """
        result = ''
        with self.__mutex :
            result = self.__is_on
        return result

# pylint: enable=R0801
