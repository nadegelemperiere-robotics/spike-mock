# -------------------------------------------------------
# Copyright (c) [2022] Nadege LEMPERIERE
# All rights reserved
# -------------------------------------------------------
""" Distance sensor mock API """
# -------------------------------------------------------
# Nadège LEMPERIERE, @04 november 2022
# Latest revision: 04 november 2022
# -------------------------------------------------------

# System includes
from time       import sleep
from threading  import Lock

# Local includes
from spike.scenario.scenario import Scenario
from spike.scenario.timer    import ScenarioTimer

# pylint: disable=W0238
class DistanceSensor() :
    """ Distance sensor mocking class

        Class is accessed simultaneously by the user side thread and the
        ground truth update thread. It is therefore protected by a mutex
    """

    # Constants
    s_cm_to_inches              = 0.39370079
    s_max_distance              = 200
    s_max_distance_short_range  = 50

    # Static variables
    s_shared_scenario           = Scenario()
    s_shared_timer              = ScenarioTimer()

####################################### SPIKE API METHODS ########################################

    def __init__(self, port) :
        """
        Contructor

        :param port: the hub port to which the sensor is connected
        :type port:  string ('A','B','C','D','E' or 'F')
        """

        self.__mutex         = Lock()
        self.__port          = None

        self.__right_top     = 100
        self.__left_top      = 100
        self.__right_bottom  = 100
        self.__left_bottom   = 100
        self.__distance      = 0

        self.s_shared_scenario.register(self, port)

    def get_distance_cm(self, short_range=False) :
        """
        Retrieves the measured distance in centimeters.

        :param short_range: whether or not to use short range mode. Short range
         mode increases accuracy, but it can only detect nearby objects.
        :type short_range:  boolean

        :raises TypeError: short_range is not a boolean

        :return: The measured distance or "none" if the distance can't be measured.
        :rtype:  float
        """

        result = None

        if not isinstance(short_range, bool) :
            raise TypeError('short_range is not a boolean')
        distance = self.__get_distance()
        if distance < self.s_max_distance and not short_range :
            result = distance
        elif distance < self.s_max_distance_short_range and short_range :
            result = distance

        return result

    def get_distance_inches(self, short_range=False) :
        """
        Retrieves the measured distance in inches.

        :param short_range: whether or not to use short range mode. Short range
         mode increases accuracy, but it can only detect nearby objects.
        :type short_range:  boolean

        :raises TypeError: short_range is not a boolean

        :return: The measured distance or "none" if the distance can't be measured.
        :rtype: float
        """

        result = self.get_distance_cm(short_range)
        if result is not None : result = round(result * self.s_cm_to_inches)

        return result

    def get_distance_percentage(self, short_range=False) :
        """
        Retrieves the measured distance as a percentage.

        :param short_range: whether or not to use short range mode. Short range
         mode increases accuracy, but it can only detect nearby objects.
        :type short_range:  boolean

        :raises TypeError: short_range is not a boolean

        :return: The measured distance or "none" if the distance can't be measured.
        :rtype: integer [0,100]
        """

        result = self.get_distance_cm(short_range)
        if result is not None : result = int(result / self.s_max_distance * 100)

        return result

    def wait_for_distance_farther_than(self,distance, unit='cm', short_range=False) :
        """
        Waits until the measured distance is greater than the specified distance.

        :param distance:    the target distance to be detected from the sensor to an object.
        :type distance:     float
        :param unit:        the unit in which the distance is measured.
        :type unit:         string (cm, in, %)
        :param short_range: whether or not to use short range mode. Short range mode increases
         accuracy, but it can only detect nearby objects.
        :type short_range:  boolean

        :raise TypeError:  distance is not a number or unit is not a string or short_range is not
         a boolean.
        :raise ValueError: unit is not one of the allowed values.
        """

        if not isinstance(distance,(float, int)) :
            raise TypeError('distance is not a number')
        if not isinstance(unit,str) :
            raise TypeError('unit is not a string')

        measure = self.s_max_distance
        if unit == 'cm'       : measure = self.get_distance_cm(short_range)
        elif unit == 'inch'   : measure = self.get_distance_inches(short_range)
        elif unit == '%'      : measure = self.get_distance_percentage(short_range)
        else : raise ValueError('unit is not one of the allowed values.')
        if measure is None  : measure = 100000
        while measure < distance :
            sleep(0.01)
            measure = self.s_max_distance
            if unit == 'cm'     : measure = self.get_distance_cm(short_range)
            if unit == 'inch'   : measure = self.get_distance_inches(short_range)
            if unit == '%'      : measure = self.get_distance_percentage(short_range)
            if measure is None  : measure = 100000

    def wait_for_distance_closer_than(self,distance, unit='cm', short_range=False) :
        """
        Waits until the measured distance is less than the specified distance.

        :param distance:    the target distance to be detected from the sensor to an object.
        :type distance:     float
        :param unit:        the unit in which the distance is measured.
        :type unit:         string (cm, in, %)
        :param short_range: whether or not to use short range mode. Short range mode increases
         accuracy, but it can only detect nearby objects.
        :type short_range:  boolean

        :raise TypeError:  distance is not a number or unit is not a string or short_range is not
         a boolean.
        :raise ValueError: unit is not one of the allowed values.
        """

        if not isinstance(distance,(float, int)) :
            raise TypeError('distance is not a number')
        if not isinstance(unit,str) :
            raise TypeError('unit is not a string')

        measure = None
        if unit == 'cm'     : measure = self.get_distance_cm(short_range)
        if unit == 'inch'   : measure = self.get_distance_inches(short_range)
        if unit == '%'      : measure = self.get_distance_percentage(short_range)
        if measure is None  : measure = 100000
        while measure > distance :
            sleep(0.01)
            measure = None
            if unit == 'cm'     : measure = self.get_distance_cm(short_range)
            if unit == 'inch'   : measure = self.get_distance_inches(short_range)
            if unit == '%'      : measure = self.get_distance_percentage(short_range)
            if measure is None  : measure = 100000

    def light_up_all(self, brightness=100) :
        """
        Lights up all of the lights on the Distance Sensor at the specified brightness.

        :param brightness: the specified brightness of all of the lights.
        :type brightness:  integer [0,100]

        :raise TypeError: brightness is not an integer
        """

        if not isinstance(brightness,int) :
            raise TypeError('brightness is not an integer')

        command = self.s_shared_scenario.command(self,'light_up_all',{
            'brightness'    : brightness
        })
        self.__process_command(command)

    def light_up(self, right_top, left_top, right_bottom, left_bottom) :
        """
        Sets the brightness of the individual lights on the Distance Sensor.

        :param right_top:    the brightness of the light that’s above the right part
         of the Distance Sensor.
        :type right_top:     integer [0,100]
        :param left_top:     the brightness of the light that’s above the left part of the
         Distance Sensor.
        :type left_top:      integer [0,100]
        :param right_bottom: the brightness of the light that’s below the right part of the
         Distance Sensor.
        :type right_bottom: integer [0,100]
        :param left_bottom: the brightness of the light that’s below the left part of the
         Distance Sensor.
        :type left_bottom:  integer [0,100]

        :raise TypeError: brightness is not an integer
        """

        if not isinstance(right_top, int) :
            raise TypeError('right_top is not an integer')
        if not isinstance(left_top, int) :
            raise TypeError('left_top is not an integer')
        if not isinstance(right_bottom, int) :
            raise TypeError('right_bottom is not an integer')
        if not isinstance(left_bottom, int) :
            raise TypeError('left_bottom is not an integer')

        command = self.s_shared_scenario.command(self,'light_up',{
            'right_top'    : right_top,
            'left_top'     : left_top,
            'right_bottom' : right_bottom,
            'left_bottom'  : left_bottom,
        })
        self.__process_command(command)

    def __get_distance(self) :
        """
        Returns current distance in cm

        :return: distance in centimeters
        :rtype:  float
        """
        result = 0
        with self.__mutex :
            result = self.__distance

        return result

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
        """
        Reset function

        .. warning:: This function is not part of the spike API. It is provided to update the
         component from scenario data and shall not be used by the end-user.
        """
        with self.__mutex :
            self.__right_top     = 100
            self.__left_top      = 100
            self.__right_bottom  = 100
            self.__left_bottom   = 100
            self.__distance      = 0

    def c_read(self, distance) :
        """
        Update the distance from scenario data

        .. warning:: This function is not part of the spike API. It is provided to update the
         component from scenario data and shall not be used by the end-user.

        :param distance: distance in centimeters
        :type distance:  float
        """
        with self.__mutex :
            self.__distance  = distance

    def c_set_lights(self, right_top, left_top, right_bottom, left_bottom) :
        """
        Light distance sensor LEDs

        .. warning:: This function is not part of the spike API. It is provided to update the
         component from scenario data and shall not be used by the end-user.

        :param right_top:    the brightness of the light that’s above the right part of the
         Distance Sensor.
        :type right_top:     integer [0,100]
        :param left_top:     the brightness of the light that’s above the left part of the
         Distance Sensor.
        :type left_top:      integer [0,100]
        :param right_bottom: the brightness of the light that’s below the right part of the
         Distance Sensor.
        :type right_bottom:  integer [0,100]
        :param left_bottom:  the brightness of the light that’s below the left part of the
         Distance Sensor.
        :type left_bottom:   integer [0,100]
        """
        with self.__mutex :
            self.__left_bottom  = left_bottom
            self.__right_bottom = right_bottom
            self.__left_top     = left_top
            self.__right_top    = right_top

# pylint: disable=R0801
    @property
    def port(self) :
        """
        Gets the component connection port

        .. warning:: This function is not part of the spike API. It is provided to update the
         component from scenario data and shall not be used by the end-user.

        :return: the component port
        :rtype:  string
        """
        result = None
        with self.__mutex :
            result = self.__port
        return result

    @port.setter
    def port(self, port) :
        """
        Sets the component connection port

        .. warning:: This function is not part of the spike API. It is provided to update the
         component from scenario data and shall not be used by the end-user.

        :param port: the component port
        :type port:  string
        """
        with self.__mutex :
            self.__port = port
# pylint: enable=W0238, R0801
