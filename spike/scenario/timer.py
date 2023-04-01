# -------------------------------------------------------
# Copyright (c) [2022] Nadege LEMPERIERE
# All rights reserved
# -------------------------------------------------------
""" Generic timer singleton representing world time """
# -------------------------------------------------------
# Nadège LEMPERIERE, @04 november 2022
# Latest revision: 04 november 2022
# -------------------------------------------------------

# System includes
from time       import time, sleep
from threading  import Lock
from logging    import getLogger

# pylint: disable=W0201, W0231
# Singleton structure makes it that __init__ is called for each copy of the singleton
# To avoid having it reinitialize the shared object, init is done once when calling
# __new__
class ScenarioTimer() :
    """ Singleton providing world clock to all timers """

    s_instance = None
    s_sleep_time = 0.01
    """ Scenario measurements update frequency --- Compliant with spike sensors frequency 100Hz """
    s_logger = getLogger('time')

# pylint: disable=W0102
    def __new__(cls):
        """ Class new function

        :param cls: class reference
        :type cls:  object
        """

        if ScenarioTimer.s_instance is None :
            ScenarioTimer.s_instance = super().__new__(cls)
            ScenarioTimer.s_instance.s_init()
        return ScenarioTimer.s_instance

    def s_init(self) :
        """ Constructor for singleton / only called once """
        self.__time             = 0
        self.__reference_time   = 0
        self.__mutex            = Lock()
        self.__configuration    = {}

    def __init__(self) :
        """ Contructor for each instantiation / do nothing """

    def reset(self) :
        """ World clock reset function """
        with self.__mutex :
            self.s_logger.info('Resetting timer')
            self.__reference_time = time()
            self.__time = 0

    def configure(self, configuration) :
        """
        Configure world clock

        :param configuration: configuration values
        :type configuration:  dictionary (mode + parameters)
        """
        with self.__mutex :
            self.s_logger.info('Configuring timer')
            self.__configuration = configuration
            self.__reference_time = time()
            self.__time = 0
            self.s_logger.info('World clock configuration : %s',str(self.__configuration))

    def sleep(self) :
        """
        Pause scenario according to time mode
        In controlled mode, the scenario shall sleep longer than the main thread to make sure
        no step is missed on the main thread part.
        In relatime mode, the scenario shall sleep less than the main thread to make sure
        the measurements are updated at each main thread call.
        """

        if self.__configuration['mode'] == 'controlled' :
            sleep(self.s_sleep_time * 2)
        else :
            sleep(self.s_sleep_time * 0.5)

    def step(self) :
        """ Function that steps into time - controlled scenario only """
        if self.__configuration['mode'] == 'controlled' :
            with self.__mutex :
                self.__time += self.__configuration['period']
            self.s_logger.info('stepping %lf to %lf', self.__configuration['period'], self.__time)

    def time(self) :
        """
        Clock time return function

        :return: current time in the world
        :rtype:  float (seconds)
        """
        result = 0
        with self.__mutex :
            if self.__configuration['mode'] == 'controlled' :
                result = self.__time
            elif self.__configuration['mode'] == 'realtime' :
                result = time() - self.__reference_time

        self.s_logger.info('Current world time: %lf', result)

        return result

# pylint: enable=W0102, W0201, W0231
