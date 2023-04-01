# -------------------------------------------------------
# Copyright (c) [2022] Nadege LEMPERIERE
# All rights reserved
# -------------------------------------------------------
""" Motor mock API """
# -------------------------------------------------------
# Nadège LEMPERIERE,  @04 november 2022
# Latest revision: 04 november 2022
# -------------------------------------------------------

# System includes
from threading import Lock
from time import sleep

# Local includes
from spike.scenario.scenario import Scenario
from spike.scenario.timer    import ScenarioTimer

# pylint: disable=R0902, R0904, W0238, R0801
class Motor() :
    """ Motor mocking class

        Class is accessed simultaneously by the user side thread and the
        ground truth update thread. It is therefore protected by a mutex
    """

    # Constants
    s_max_speed                 = 100
    s_max_steering              = 100
    s_max_power                 = 100
    s_min_position              = 0
    s_max_position              = 359

    s_motor_directions          = [
        'shortest path',
        'clockwise',
        'counterclockwise',
    ]
    s_motor_stop_actions        = [
        'coast',
        'hold',
        'brake',
    ]

    # Static variables
    s_shared_scenario              = Scenario()
    s_shared_timer                 = ScenarioTimer()

####################################### SPIKE API METHODS ########################################

    def __init__(self, port) :
        """
        Contructor

        :param port: the hub port to which the motor is connected
        :type port:  string ('A','B','C','D','E' or 'F')
        """

        self.__mutex                    = Lock()
        self.__port                     = None

        self.__degrees                  = 0
        self.__stop_action              = 'brake'
        self.__speed                    = 0
        self.__position                 = 0
        self.__degrees                  = 0

        self.__position                 = 0

        self.__was_interrupted          = False
        self.__was_stalled              = False
        self.__shall_stop_when_stalled  = False

        self.__delta_degrees            = 0
        self.__default_speed            = self.s_max_speed

        self.s_shared_scenario.register(self, port)

    def run_to_position(self, degrees, direction='shortest path', speed=None) :
        """
        Runs the motor to an absolute position.

        The sign of the speed will be ignored (i.e., absolute value), and the motor will
        always travel in the direction that’s been specified by the "direction" parameter.
        If the speed is greater than "100," it will be limited to "100."

        :param degrees:   the target position.
        :type degrees:    integer [0,359]
        :param direction: the direction to use to reach the target position.
        :type direction:  string ("Shortest path" could run in either direction,
         depending on the shortest distance to the target. "Clockwise" will make
         the motor run clockwise until it reaches the target position.
         "Counterclockwise" will make the motor run counterclockwise until it
         reaches the target position.)
        :param speed:     the motor's speed
        :type speed:      integer [0,100]. If no value is specified, it will use the
         default speed that’s been set by set_default_speed().

        :raises TypeError: degrees or speed is not an integer or direction is not a string.
        :raises ValueError: direction is not one of the allowed values or degrees is not
         within the range of 0-359 (both inclusive).
        """

        if not isinstance(degrees, int) :
            raise TypeError('degrees is not an integer')
        if not isinstance(direction, str) :
            raise TypeError('direction is not a string')
        if not isinstance(speed, int) :
            raise TypeError('speed is not an integer')

        if degrees < self.s_min_position or degrees > self.s_max_position :
            raise ValueError('degrees are not in the range 0-359')
        if direction not in self.s_motor_directions :
            raise ValueError('direction is none of the allowed values')

        if speed is None : speed = self.__default_speed
        if speed < -self.s_max_speed : speed = - self.s_max_speed
        if speed > self.s_max_speed : speed = self.s_max_speed

        command = self.s_shared_scenario.command(self,'run_to_position', \
            { 'speed' : speed,    'degrees' : degrees, 'direction' : direction }
        )
        self.__process_command(command)

    def run_to_degrees_counted(self, degrees, speed=None):
        """
        Runs the motor until the number of degrees counted is equal to the value that
        has been specified by the "degrees" parameter.

        The sign of the speed will be ignored (i.e., absolute value), and the motor will
        always travel in the direction that’s been specified by the "direction" parameter.
        If the speed is greater than "100," it will be limited to "100."

        :param degrees:   the target degrees counted.
        :type degrees:    integer
        :param speed:     the motor's speed
        :type speed:      integer [0,100]. If no value is specified, it will use the
         default speed that’s been set by set_default_speed().

        :raises TypeError: degrees or speed is not an integer.
        """

# pylint: enable=R0801
        if not isinstance(degrees, int) :
            raise TypeError('degrees is not an integer')
        if not isinstance(speed, int) :
            raise TypeError('speed is not an integer')

        if speed is None : speed = self.__default_speed
        if speed < -self.s_max_speed : speed = - self.s_max_speed
        if speed > self.s_max_speed : speed = self.s_max_speed
# pylint: enable=R0801

        command = self.s_shared_scenario.command(self,'run_to_degrees_counted',
            { 'speed' : speed, 'degrees' : degrees }
        )
        self.__process_command(command)

    def run_for_degrees(self, degrees, speed=None):
        """
        Runs the motor for a specified number of degrees.

        :param degrees:   the number of degrees that the motor should run.
        :type degrees:    integer
        :param speed:     the motor's speed
        :type speed:      integer [-100,100]. If no value is specified, it will use the
         default speed that’s been set by set_default_speed().

        :raises TypeError: degrees or speed is not an integer.
        """

        if not isinstance(degrees, int) :
            raise TypeError('degrees is not an integer')
        if not isinstance(speed, int) :
            raise TypeError('speed is not an integer')

        if speed is None : speed = self.__default_speed
        if speed < -self.s_max_speed : speed = - self.s_max_speed
        if speed > self.s_max_speed : speed = self.s_max_speed

        command = self.s_shared_scenario.command(self,'run_for_degrees',
            { 'speed' : speed,  'degrees' : degrees }
        )
        self.__process_command(command)

    def run_for_rotations(self, rotations, speed=None):
        """
        Runs the motor for a specified number of rotations.

        :param degrees: the number of rotations that the motor should run.
        :type degrees:  float
        :param speed:   the motor's speed
        :type speed:    int [-100,100]. If no value is specified, it will use the
         default speed that’s been set by set_default_speed().

        :raises TypeError: rotations is not a number or speed is not an integer.
        """

        if not isinstance(rotations, (float, int)) :
            raise TypeError('rotations is not a number')
        if not isinstance(speed, int) :
            raise TypeError('speed is not an integer')

        if speed is None : speed = self.__default_speed
        if speed < -self.s_max_speed : speed = - self.s_max_speed
        if speed > self.s_max_speed : speed = self.s_max_speed

        command = self.s_shared_scenario.command(self,'run_for_rotations',
            { 'speed' : speed, 'rotations' : rotations }
        )
        self.__process_command(command)

    def run_for_seconds(self, seconds, speed=None):
        """
        The number of seconds for which the motor should run.

        :param seconds: the number of rotations that the motor should run.
        :type seconds:  float
        :param speed:   the motor's speed
        :type speed:    int [-100,100]. If no value is specified, it will use the
         default speed that’s been set by set_default_speed().

        :raises TypeError: seconds is not a number or speed is not an integer.
        """

        if not isinstance(seconds, (float, int)) :
            raise TypeError('seconds is not a number')
        if not isinstance(speed, int) :
            raise TypeError('speed is not an integer')

        if speed is None : speed = self.__default_speed
        if speed < -self.s_max_speed : speed = - self.s_max_speed
        if speed > self.s_max_speed : speed = self.s_max_speed

        command = self.s_shared_scenario.command(self, 'run_for_seconds',
            { 'speed' : speed, 'seconds' : seconds }
        )
        self.__process_command(command)

    def start(self, speed=None) :
        """
        Starts running the motor at a specified speed.

        The motor will keep moving at this speed until you give it another motor
        command or when your program ends.

        :param speed:   the motor's speed
        :type speed:    integer [-100,100]. If no value is specified, it will use the
         default speed that’s been set by set_default_speed().

        :raises TypeError: speed is not an integer.
        """

        if not isinstance(speed, int) :
            raise TypeError('speed is not an integer')

        if speed is None : speed = self.__default_speed
        if speed < -self.s_max_speed : speed = - self.s_max_speed
        if speed > self.s_max_speed : speed = self.s_max_speed

        command = self.s_shared_scenario.command(self,'start',
            { 'speed' : speed }
        )
        self.__process_command(command)

    def stop(self) :
        """
        Stops the motor.

        What the motor does after it stops depends on the action that’s been
        set in set_stop_action(). The default value of set_stop_action() is "coast."
        """

        command = self.s_shared_scenario.command(self, 'stop',{})
        self.__process_command(command)

    def start_at_power(self, power) :
        """
        Starts running the motor at a specified power level.

        The motor will keep moving at this speed until you give it another motor
        command or when your program ends.

        :param power:   power of the motor
        :type power:    int [-100,100].

        :raises TypeError: power is not an integer.
        """

        if not isinstance(power, int) :
            raise TypeError('power is not an integer')

        if power < -self.s_max_power : power = - self.s_max_power
        if power > self.s_max_power : power = self.s_max_power

        command = self.s_shared_scenario.command(self,'start_at_power',{
            'power' : power,
        })
        self.__process_command(command)

    def get_speed(self) :
        """
        Retrieves the motor speed.

        :return: current motor speed
        :rtype:  int [-100,100]
        """
        result = None
        with self.__mutex :
            result = self.__speed
        return result

    def get_default_speed(self) :
        """
        Retrieves the motor default speed.

        :return: current motor default speed value
        :rtype:  int [-100,100]
        """
        result = None
        with self.__mutex :
            result = self.__default_speed
        return result

    def get_position(self) :
        """
        Retrieves the motor position. This is the clockwise angle between the moving
        marker and the zero-point marker on the motor.

        :return: the motor’s position.
        :rtype:  integer [0,359]
        """
        result = None
        with self.__mutex :
            result = self.__position
        return result

    def was_stalled(self) :
        """
        Tests whether the motor was stalled.

        :return: True if the motor has stalled since the last time was_stalled() was called,
         otherwise false.
        :rtype:  boolean
        """
        result = None
        with self.__mutex :
            result = self.__was_stalled
            self.__was_stalled = False
        return result

    def was_interrupted(self) :
        """
        Tests whether the motor was interrupted.

        :return: True if the motor was interrupted since the last time was_interrupted() was
         called, otherwise false.
        :rtype:  boolean
        """
        result = None
        with self.__mutex :
            result = self.__was_interrupted
            self.__was_interrupted = False
        return result

    def get_degrees_counted(self) :
        """
        Retrieves the number of degrees that have been counted by the motor.

        :return: Current counted degrees
        :rtype:  integer
        """
        result = None
        with self.__mutex :
            result = self.__degrees - self.__delta_degrees
        return result

    def set_default_speed(self, speed) :
        """
        Sets the default motor speed. This speed will be used when you omit
        the speed argument in one of the other methods, such as run_for_degrees.
        Setting the default speed does not affect any motors that are currently running.
        It will only have an effect when another motor method is called after this method.
        If the value of default_speed is outside of the allowed range, the default speed will
        be set to "-100" or "100" depending on whether the value is negative or positive.

        :param speed: the default speed value.
        :type speed:  integer [-100,100]

        :raises TypeError: default_speed is not an integer
        """

        if not isinstance(speed, int) :
            raise TypeError('speed is not an integer')

        if speed < -self.s_max_speed : speed = - self.s_max_speed
        if speed > self.s_max_speed : speed = self.s_max_speed
        self.__default_speed = speed

    def set_degrees_counted(self, degrees_counted) :
        """
        Sets the "number of degrees counted" to the desired value.

        :param degrees_counted: new degrees value
        :type degrees_counted:  integer

        :raises TypeError: degrees_counted is not an integer
        """

        if not isinstance(degrees_counted, int) :
            raise TypeError('degrees_counted is not an integer')

        with self.__mutex :
            self.__delta_degrees = self.__degrees - degrees_counted

        command = self.s_shared_scenario.command(self,'set_degrees_counted',{
            'degrees' : degrees_counted,
        })
        self.__process_command(command)

    def set_stall_detection(self, stop_when_stalled) :
        """
        Turns stall detection on or off.

        Stall detection senses when a motor has been blocked and can t move.
        If stall detection has been enabled and a motor is blocked, the motor will be
        powered off after two seconds and the current motor command will be interrupted.
        If stall detection has been disabled, the motor will keep trying to run and programs
        will "get stuck" until the motor is no longer blocked.

        Stall detection is enabled by default.

        :param stop_when_stalled: choose "true" to enable stall detection or "false" to disable it.
        :type stop_when_stalled:  boolean
        """
        if not isinstance(stop_when_stalled, bool) :
            raise TypeError('stop_when_stalled is not a boolean')

        command = self.s_shared_scenario.command(self,'set_stall_detection',{
            'stop_when_stalled' : stop_when_stalled,
        })
        self.__process_command(command)

# pylint: disable=R0801
    def set_stop_action(self, action) :
        """
        Sets the default behavior when a motor stops.

        :param action: the desired motor behavior when the motor stops.
        :type action:  string (coast,brake,hold)
        """
        if not isinstance(action, str) :
            raise TypeError('action is not a string')

        if not action in Motor.s_motor_stop_actions :
            raise ValueError('action is not in the list of allowed values')

        command = self.s_shared_scenario.command(self,'set_stop_action',{
            'action' : action,
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
        """ Reset function

        .. warning:: This function is not part of the spike API. It is provided to update the
         component from scenario data and shall not be used by the end-user.
        """
        with self.__mutex :
            self.__degrees                  = 0
            self.__stop_action              = 'brake'
            self.__speed                    = 0
            self.__position                 = 0
            self.__degrees                  = 0

            self.__position                 = 0

            self.__was_interrupted          = False
            self.__was_stalled              = False
            self.__shall_stop_when_stalled  = False

    def c_read(self, value) :
        """
        Update the motor from scenario data

        .. warning:: This function is not part of the spike API. It is provided to update the
         component from scenario data and shall not be used by the end-user.

        :param value: current motor degrees value
        :type value:  float
        """
        with self.__mutex :
            self.__degrees  = int(round(value))
            self.__position = (self.__degrees) % 360

    def c_set_stall_detection(self, stop_when_stalled):
        """
        Turns stall detection on or off.

        .. warning:: This function is not part of the spike API. It is provided to update the
         component from scenario data and shall not be used by the end-user.

        :param stop_when_stalled: True to enable stall detection or False to disable it.
        :type stop_when_stalled:  boolean
        """
        with self.__mutex :
            self.__shall_stop_when_stalled = stop_when_stalled

    def c_set_stop_action(self,action) :
        """
        Sets the default behavior when a motor stops.

        .. warning:: This function is not part of the spike API. It is provided to update the
         component from scenario data and shall not be used by the end-user.

        :param action: the desired motor behavior when the motor stops.
        :type action:  string (coast,brake,hold)
        """

        with self.__mutex :
            self.__stop_action = action

    @property
    def port(self) :
        """ Sets the component connection port

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
        """ Sets the component connection port

        .. warning:: This function is not part of the spike API. It is provided to update the
         component from scenario data and shall not be used by the end-user.

        :param port: the component port
        :type port:  string
        """
        with self.__mutex :
            self.__port = port

# pylint: enable=R0902, R0904, W0238, R0801
