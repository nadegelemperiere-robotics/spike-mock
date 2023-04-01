# -------------------------------------------------------
# Copyright (c) [2022] Nadege LEMPERIERE
# All rights reserved
# -------------------------------------------------------
""" High resolution timer with a milliseconds resolution
emulating spike timer interfaces on standard python """
# -------------------------------------------------------
# Nadège LEMPERIERE, @04 november 2022
# Latest revision: 04 november 2022
# -------------------------------------------------------

# System includes
from time import sleep

# Local includes
from spike.scenario.scenario import Scenario
from spike.scenario.timer import ScenarioTimer

# pylint: disable=C0103
def equal_to(a, b) :
    """
    Default function for wait_until function
    :meta private:
    """
    return a == b
# pylint: enable=C0103

class Timer() :
    """ Timer mocking class """

    # Static variables
    s_shared_scenario = Scenario()
    s_shared_timer = ScenarioTimer()

    def __init__(self) :
        """ Contructor """
        self.__reference_time    = -1
        self.s_shared_scenario.register(self)

    def now(self) :
        """
        Retrieves the "right now" time of the Timer.

        :return: the current time, specified in seconds.
        :rtype:  integer
        """

        return self.s_shared_timer.time() - self.__reference_time

    def reset(self) :
        """ Sets the Timer to "0." """
        self.__reference_time = self.s_shared_timer.time()

def wait_for_seconds(seconds) :
    """
    Waits for a specified number of seconds before continuing the program.

    :param seconds: time to wait in seconds
    :type seconds:  float

    :raises TypeError:  seconds is not a number
    :raises ValueError: seconds is not at least 0
    """

    if not isinstance(seconds, (float, int)):
        raise TypeError('seconds is not a number')
    if seconds < 0 :
        raise ValueError('seconds is not at least 0')

    timer = ScenarioTimer()

    reference_time  = timer.time()
    while (timer.time() - reference_time) < seconds :
        sleep(0.01)

def wait_until(get_value_function, operator_function=equal_to, target_value=True) :
    """
    Waits until the condition is true before continuing with the program.

    :param get_value_function: a function that returns the current value to be compared
     to the target value.
    :type get_value_function:  callable
    :param operator_function:  a function that compares two arguments. The first argument will
     be the result of get_value_function(), and the second argument will be target_value.
     The function will compare both values and return the result.
    :type operator_function:   callable
    :param target_value:       any object that can be compared by operator_function.
    :type target_value:        any type

    :raises TypeError: get_value_function or operator_function is not callable or operator_function
     does not compare two arguments.
    """

    if not callable(get_value_function) :
        raise TypeError('get_value_function is not callable')
    if not callable(operator_function) :
        raise TypeError('operator_function is not callable')

    current = get_value_function()
    while not operator_function(current, target_value) :
        sleep(0.01)
