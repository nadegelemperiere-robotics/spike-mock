# -------------------------------------------------------
# Copyright (c) [2022] Nadege LEMPERIERE
# All rights reserved
# -------------------------------------------------------
""" Hub speaker mock API """
# -------------------------------------------------------
# Nadège LEMPERIERE, @04 november 2022
# Latest revision: 04 november 2022
# -------------------------------------------------------

# System includes
from threading import Lock
from time      import sleep

# Local includes
from spike.scenario.scenario import Scenario
from spike.scenario.timer  import ScenarioTimer

# pylint: disable=W0238, R0801
class Speaker() :
    """ Hub speaker mocking class

        Class is accessed simultaneously by the user side thread and the
        ground truth update thread. It is therefore protected by a mutex
    """

    # Constants
    s_max_volume        = 100
    s_min_note          = 44
    s_max_note          = 123

    # Static variables
    s_shared_scenario  = Scenario()
    s_shared_timer     = ScenarioTimer()

####################################### SPIKE API METHODS ########################################

# pylint: disable=W0102
    def __init__(self) :
        """ Contructor"""

        self.__mutex      = Lock()

        self.__is_beeping = False
        self.__note       = 0
        self.__volume     = 0

        self.s_shared_scenario.register(self)

# pylint: enable=W0102

    def beep(self, note=60, seconds=0.2) :
        """
        Plays a beep on the Hub.

        :param note: The MIDI note number
        :type note: float
        :param seconds: Beep duration in seconds
        :type seconds: float

        :raises TypeError: note is not a number or seconds is not a number.
        :raises ValueError: note is not within the allowed range of 44-123
        """

        if not isinstance(note, (float, int)):
            raise TypeError('note is not a number')
        if not isinstance(seconds, float) and not isinstance(seconds, int):
            raise TypeError('seconds is not a number')

        if note < self.s_min_note or note > self.s_max_note :
            raise ValueError('note is not within the allowed range of 44-123')

        command = self.s_shared_scenario.command(self,'beep',{
            'note'    : note,
            'seconds' : seconds,
        })
        self.__process_command(command)

    def start_beep(self, note=60) :
        """
        Starts playing a beep.

        The beep will play indefinitely until stop() or another beep method is called.

        :param note: The MIDI note number
        :type note: float

        :raises TypeError: note is not a number.
        :raises ValueError: note is not within the allowed range of 44-123
        """

        if not isinstance(note, (float, int)):
            raise TypeError('note is not a number')

        if note < self.s_min_note or note > self.s_max_note :
            raise ValueError('note is not within the allowed range of 44-123')

        command = self.s_shared_scenario.command(self,'start_beep',{
            'note'    : note,
        })
        self.__process_command(command)

    def stop(self) :
        """ Stops any sound that is playing. """
        command = self.s_shared_scenario.command(self,'stop',{})
        self.__process_command(command)

    def get_volume(self) :
        """
        Retrieves the value of the speaker volume.

        This only retrieves the volume of the Hub, not the programming app.

        :return: The speaker volume
        :rtype:  int [0,100]
        """
        result = 0
        with self.__mutex :
            result = self.__volume
        return result

    def set_volume(self, volume) :
        """
        Sets the speaker volume.
        If the assigned volume is out of range, the nearest volume (i.e., 0 or 100) will be used
        instead. This only sets the volume of the Hub, not the programming app.

        :param volume: The new volume percentage.
        :type volume:  int [0,100]

        :raises TypeError: volume is not a number.
        """

        if not isinstance(volume, int):
            raise TypeError('volume is not an integer')

        lvolume = min(max(0,volume),self.s_max_volume)

        command = self.s_shared_scenario.command(self,'set_volume',{
            'volume'    : lvolume,
        })
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
        """
        Reset function

        .. warning:: This function is not part of the spike API. It is provided to update the
         component from scenario data and shall not be used by the end-user.
        """
        with self.__mutex :
            self.__is_beeping = False
            self.__note       = 0
            self.__volume     = 0

    def c_beep(self, note=60, seconds=0.2) :
        """
        Plays a beep on the Hub.

        .. warning:: This function is not part of the spike API. It is provided to update the
         component from scenario data and shall not be used by the end-user.

        :param note: The MIDI note number
        :type note: float
        :param seconds: Beep duration in seconds
        :type seconds: float
        """
        self.c_start_beep(note)

        current_time = self.s_shared_timer.time()
        while self.s_shared_timer.time() - current_time < seconds :
            sleep(0.01)

        self.c_stop()

    def c_start_beep(self, note=60) :
        """
        Plays a beep on the Hub.

        .. warning:: This function is not part of the spike API. It is provided to update the
         component from scenario data and shall not be used by the end-user.

        :param note: The MIDI note number
        :type note: float

        """
        with self.__mutex :
            self.__is_beeping = True
            self.__note       = note

    def c_stop(self) :
        """
        Stops the beep

        .. warning:: This function is not part of the spike API. It is provided to update the
         component from scenario data and shall not be used by the end-user.
        """
        with self.__mutex :
            self.__is_beeping = False
            self.__note       = 0

    def c_set_volume(self, volume) :
        """
        Sets the speaker volume.

        .. warning:: This function is not part of the spike API. It is provided to update the
         component from scenario data and shall not be used by the end-user.

        :param volume: The new volume percentage.
        :type volume:  int [0,100]
        """
        self.__volume = volume
# pylint: enable=W0238, R0801
