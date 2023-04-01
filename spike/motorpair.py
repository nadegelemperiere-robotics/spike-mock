# -------------------------------------------------------
# Copyright (c) [2022] Nadege LEMPERIERE
# All rights reserved
# -------------------------------------------------------
""" Motor pair mock API """
# -------------------------------------------------------
# Nadège LEMPERIERE,  @04 november 2022
# Latest revision: 04 november 2022
# -------------------------------------------------------

# System includes
from threading import Lock
from time      import sleep

# Local includes
from spike.scenario.scenario    import Scenario
from spike.scenario.timer       import ScenarioTimer

# pylint: disable=W0238, R0801
class MotorPair() :
    """ MotorPair mocking class

        Class is accessed simultaneously by the user side thread and the
        ground truth update thread. It is therefore protected by a mutex
    """

    # Constants
    s_cm_to_inches      = 0.39370079
    s_max_speed         = 100
    s_max_steering      = 100
    s_max_power         = 100
    s_motorpair_units   = [
        'cm',
        'in',
        'rotations',
        'degrees',
        'seconds',
    ]
    s_motor_stop_actions = [
        'hold',
        'coast',
        'brake'
    ]

    # Static variables
    s_shared_scenario  = Scenario()
    s_shared_timer     = ScenarioTimer()

# -------------- SPIKE MOTORPAIR FUNCTIONS ---------------

    def __init__(self, left_port, right_port) :
        """
        Contructor

        :param left_port:  The port on which the left motor is located
        :type left_port:   string ('A','B','C','D','E' or 'F')
        :param right_port: The port on which the right motor is located
        :type right_port:  string ('A','B','C','D','E' or 'F')
        """

        self.__mutex            = Lock()

        self.__stop_action      = 'brake'

        self.__default_speed    = 100
        self.__motor_rotation   = 17.6

        self.__left             = None
        self.__right            = None

        self.s_shared_scenario.register(self, left_port, right_port)

    def move(self, amount, unit='cm', steering=0, speed=None) :
        """
        Start both motors simultaneously to move a Driving Base.

        Steering = "0" makes the Driving Base go straight. Negative numbers make the Driving Base
        turn left. Positive numbers make the Driving Base turn right.

        The program will not continue until the specified value is reached.

        If the value of steering is equal to "-100" or "100," the Driving Base will perform a
        rotation on itself (i.e., "tank move") at the default speed of each motor.

        If the value of steering is outside of the allowed range, the value will be set to "-100"
        or "100," depending on whether the value is positive or negative.

        If speed is outside of the allowed range, the value will be set to "-100" or "100,"
        depending on whether the value is positive or negative.

        If the speed is negative, the Driving Base will move backward instead of forward.
        Likewise, if the "amount" is negative, the Driving Base will move backward instead of
        forward. If both the speed and the "amount" are negative, the Driving Base will move
        forward.

        When the specified unit is "cm" or "in," the "amount" of the unit parameter is equal to
        the horizontal distance that the Driving Base will travel before stopping. The relationship
        between the motor rotations and distance traveled can be adjusted by calling
        set_motor_rotation().

        When the "unit" is "rotations" or "degrees," the "amount" parameter value specifies how
        much the motor axle will turn before stopping.

        When the "unit" is "seconds," the "amount" parameter value specifies the duration that
        the motors will run before stopping.

        :param amount:   The quantity to move in relation to the specified unit of measurement.
        :type amount:    float
        :param unit:     The unit of measurement specified for the "amount" parameter.
        :type unit:      string (cm,in,rotations,degrees,seconds)
        :param speed:    The speed at which the Driving Base will move while performing a curve.
        :type speed:     int [-100,100]
        :param steering: The steering direction (-100 to 100). "0" makes the Driving Base move
         straight. Negative numbers make the Driving Base turn left. Positive numbers make the
         Driving Base turn right.
        :type steering:  int [-100,100]

        :raises TypeError: amount, left_speed or right_speed is not a number or unit is not a
         string.
        :raises ValueError: unit is not one of the allowed values.
        """


        if not isinstance(amount, (float, int)):
            raise TypeError('amount is not a number')
        if not isinstance(unit, str) :
            raise TypeError('unit is not a string')
        if not isinstance(steering, int) :
            raise TypeError('steering is not an integer')
        if not isinstance(speed, int) :
            raise TypeError('speed is not an integer')

        if unit not in self.s_motorpair_units :
            raise ValueError('unit is not one of the allowed values')

        measure = 0
        if unit == 'cm'         : measure = amount
        elif unit == 'inch'       : measure = amount * self.s_cm_to_inches
        elif unit == 'rotations'  : measure = self.__motor_rotation * amount
        elif unit == 'degrees'    : measure = self.__motor_rotation * amount / 360
        else :
            raise ValueError('unit is not one of the allowed values')

        if speed is None : speed = self.__default_speed
        if speed < -self.s_max_speed : speed = - self.s_max_speed
        if speed > self.s_max_speed : speed = self.s_max_speed
        if steering < -self.s_max_steering : steering = - self.s_max_steering
        if steering > self.s_max_steering : steering = self.s_max_steering

        command = self.s_shared_scenario.command(self,'move',{
            'amount'    : measure,
            'steering'  : steering,
            'speed'     : speed,
        })
        self.__process_command(command)

    def start(self, steering=0, speed=None) :
        """
        Start both motors simultaneously to move a Driving Base.

        Steering = "0" makes the Driving Base go straight. Negative numbers make the Driving Base
        turn left. Positive numbers make the Driving Base turn right.

        The program flow is not interrupted. This is most likely interrupted by sensor input and
        a condition.

        If the value of steering is equal to "-100" or "100," the Driving Base will perform a
        rotation on itself (i.e., "tank move") at the default speed of each motor.

        If the value of "steering" is outside of the allowed range, the value will be set to
        "-100" or "100," depending on whether the value is positive or negative.

        If speed is outside of the allowed range, the value will be set to "-100" or "100,"
        depending on whether the value is positive or negative.

        If the speed is negative, the Driving Base will move backward instead of forward.
        Likewise, if the "amount" is negative, the Driving Base will move backward instead of
        forward. If both the speed and the "amount" are negative, the Driving Base will move
        forward.

        :param speed: The speed at which the Driving Base will move while performing a curve.
        :type speed: int [-100,100]
        :param steering: The steering direction (-100 to 100). "0" makes the Driving Base move
         straight. Negative numbers make the Driving Base turn left. Positive numbers make the
         Driving Base turn right.
        :type steering: int [-100,100]

        :raises TypeError: steering or speed is not an integer
        """

# pylint: disable=R0801
        if not isinstance(steering, int) :
            raise TypeError('steering is not an integer')
        if not isinstance(speed, int) :
            raise TypeError('speed is not an integer')

        if speed is None : speed = self.__default_speed
        if speed < -self.s_max_speed : speed = - self.s_max_speed
        if speed > self.s_max_speed : speed = self.s_max_speed
        if steering < -self.s_max_steering : steering = - self.s_max_steering
        if steering > self.s_max_steering : steering = self.s_max_steering
# pylint: enable=R0801

        command = self.s_shared_scenario.command(self,'start',{
            'steering'  : steering,
            'speed'     : speed,
        })
        self.__process_command(command)

    def stop(self) :
        """
        Stops both motors simultaneously, which will stop a Driving Base.

        The motors will either actively hold their current position or coast
        freely depending on the option that’s been selected by set_stop_action().
        """
        command = self.s_shared_scenario.command(self,'stop',{})
        self.__process_command(command)

    def move_tank(self, amount, unit='cm', left_speed=None, right_speed=None) :
        """
        Moves the Driving Base using differential (tank) steering.

        The speed of each motor can be controlled independently for differential (tank)
        drive Driving Bases.

        When the specified unit is "cm" or "in," the "amount" of the unit parameter is equal
        to the horizontal distance that the Driving Base will travel before stopping. The
        relationship between the motor rotations and distance traveled can be adjusted by
        calling set_motor_rotation().

        When the "unit" is "rotations" or "degrees," the "amount" parameter value specifies
        how much the motor axle will turn before stopping.

        When the "unit" is "seconds," the "amount" parameter value specifies the duration
        that the motors will run before stopping.

        If left_speed or right_speed is outside of the allowed range, the value will be set
        to "-100" or "100" depending on whether the value is positive or negative.

        If one of the speeds (i.e., left_speed or right_speed) is negative, the negative-speed
        motor will run backward instead of forward. If the "amount" parameter value is negative,
        both motors will rotate backward instead of forward. If both of the speed values (i.e.,
        left_speed and right_speed) are negative and the "amount" parameter value is negative,
        both motors will rotate forward.

        The program will not continue until the specified value is reached.

        :param amount:     The quantity to move in relation to the specified unit of measurement.
        :type amount:      float
        :param unit:       The unit of measurement specified for the "amount" parameter.
        :type unit:        string (cm,in,rotations,degrees,seconds)
        :param left_speed: The speed of the left motor.
        :type left_speed: int [-100,100]
        :param right_speed: The speed of the right motor.
        :type right_speed: int [-100,100]

        :raises TypeError: amount, left_speed or right_speed is not a number or unit is not a
         string.
        :raises ValueError: unit is not one of the allowed values.
        """

        if not isinstance(amount, (float, int)):
            raise TypeError('amount is not a number')
        if not isinstance(unit, str) :
            raise TypeError('unit is not a string')
        if not isinstance(left_speed, int) :
            raise TypeError('left_speed is not an integer')
        if not isinstance(right_speed, int) :
            raise TypeError('right_speed is not an integer')

        if unit not in self.s_motorpair_units :
            raise ValueError('unit is not one of the allowed values')

        measure = 0
        if unit == 'cm'         : measure = amount
        elif unit == 'inch'       : measure = amount * self.s_cm_to_inches
        elif unit == 'rotations'  : measure = self.__motor_rotation * amount
        elif unit == 'degrees'    : measure = self.__motor_rotation * amount / 360
        else :
            raise ValueError('unit is not one of the allowed values')

        if left_speed is None : left_speed = self.__default_speed
        if left_speed < -self.s_max_speed : left_speed = - self.s_max_speed
        if left_speed > self.s_max_speed : left_speed = self.s_max_speed

        if right_speed is None : right_speed = self.__default_speed
        if right_speed < -self.s_max_speed : right_speed = - self.s_max_speed
        if right_speed > self.s_max_speed : right_speed = self.s_max_speed

        command = self.s_shared_scenario.command(self,'move_tank',{
            'amount'        : measure,
            'left_speed'    : left_speed,
            'right_speed'   : right_speed,
        })
        self.__process_command(command)

    def start_tank(self, left_speed=None, right_speed=None) :
        """
        Starts moving the Driving Base using differential (tank) steering.

        The speed of each motor can be controlled independently for differential (tank) drive
        Driving Bases.

        If left_speed or right_speed is outside of the allowed range, the value will be set to
        "-100" or "100" depending on whether the value is positive or negative.

        If the speed is negative, the motors will move backward instead of forward.

        The program flow is not interrupted. This is most likely interrupted by sensor input
        and a condition.

        :param left_speed: The speed of the left motor.
        :type left_speed: int [-100,100]
        :param right_speed: The speed of the right motor.
        :type right_speed: int [-100,100]

        :raises TypeError: left_speed or right_speed is not an integer
        """

        if not isinstance(left_speed, int) :
            raise TypeError('left_speed is not an integer')
        if not isinstance(right_speed, int) :
            raise TypeError('right_speed is not an integer')

        if left_speed is None : left_speed = self.__default_speed
        if left_speed < -self.s_max_speed : left_speed = - self.s_max_speed
        if left_speed > self.s_max_speed : left_speed = self.s_max_speed
        if right_speed is None : right_speed = self.__default_speed
        if right_speed < -self.s_max_speed : right_speed = - self.s_max_speed
        if right_speed > self.s_max_speed : right_speed = self.s_max_speed

        command = self.s_shared_scenario.command(self,'start_tank',{
            'left_speed'    : left_speed,
            'right_speed'   : right_speed,
        })
        self.__process_command(command)

    def start_at_power(self, power, steering=0) :
        """
        Starts moving the Driving Base without speed control.

        The motors can also be driven without speed control. This is useful when using your own
        control algorithm (e.g., a proportional line-follower).

        If the steering is outside of the allowed range, the value will be set to "-100" or "100"
        depending on whether the value is positive or negative.

        If the power is outside of the allowed range, the value will be set to "-100" or "100"
        depending on whether the value is positive or negative.

        If the power is negative, the Driving Base will move backward instead of forward.

        The program flow is not interrupted. This can most likely be interrupted by sensor input
        and a condition.

        :param power: The amount of power to send to the motors.
        :type power: int [-100,100]
        :param steering: The steering direction (-100 to 100). "0" makes the Driving Base move
         straight. Negative numbers make the Driving Base turn left. Positive numbers make the
         Driving Base turn right.
        :type steering: int [-100,100]

        :raises TypeError: steering or power is not an integer
        """

        if not isinstance(steering, int) :
            raise TypeError('steering is not an integer')
        if not isinstance(power, int) :
            raise TypeError('power is not an integer')

        if steering < -self.s_max_steering : steering = - self.s_max_steering
        if steering > self.s_max_steering : steering = self.s_max_steering
        if power < -self.s_max_power : power = - self.s_max_power
        if power > self.s_max_power : power = self.s_max_power

        command = self.s_shared_scenario.command(self,'start_at_power',{
            'power'    : power,
            'steering' : steering,
        })
        self.__process_command(command)

    def start_tank_at_power(self, left_power, right_power) :
        """
        Starts moving the Driving Base using differential (tank) steering without speed control.

        The motors can also be driven without speed control. This is useful when using your own
        control algorithm (e.g., a proportional line-follower).

        If the left_power or right_power is outside of the allowed range, the value will be
        rounded to "-100" or "100" depending on whether the value is positive or negative.

        If the power is a negative value, the corresponding motor will move backward instead
        of forward.

        The program flow is not interrupted. This can most likely be interrupted by sensor input
        and a condition.

        :param left_power: The power of the left motor.
        :type left_power: int [-100,100]
        :param right_power: The power of the right motor.
        :type right_power: int [-100,100]

        :raises TypeError: left_power or right_power is not an integer
        """

        if not isinstance(left_power, int) :
            raise TypeError('left_power is not an integer')
        if not isinstance(right_power, int) :
            raise TypeError('right_power is not an integer')

        if left_power < -self.s_max_power : left_power = - self.s_max_power
        if left_power > self.s_max_power : left_power = self.s_max_power
        if right_power < -self.s_max_power : right_power = - self.s_max_power
        if right_power > self.s_max_power : right_power = self.s_max_power

        command = self.s_shared_scenario.command(self,'start_tank_at_power',{
            'left_power'  : left_power,
            'right_power' : right_power,
        })
        self.__process_command(command)

    def get_default_speed(self) :
        """
        Retrieves the default motor speed.
        ---
        :return: The motors default speed
        :rtype: int [-100,100]
        """
        return self.__default_speed

    def set_motor_rotation(self, amount, unit='cm') :
        """
        Sets the ratio of one motor rotation to the distance traveled.

        If there are no gears used between the motors and the wheels of the Driving Base,
        the "amount" is the circumference of one wheel.

        Calling this method does not affect the Driving Base if it’s already running.
        It will only have an effect the next time one of the move or start methods is used.

        :param amount: The distance that the Driving Base moves when both motors move one
         rotation each, 17.6 default (5.6 diameter wheel)
        :type amount:  float
        :param unit:   The unit of measurement specified for the "amount" parameter.
        :type unit:    string (cm,in)

        :raises TypeError: amount is not a number or unit is not a string.
        :raises ValueError: unit is not one of the allowed values.
        """

        if not isinstance(amount, (float, int)) :
            raise TypeError('amount is not a number')
        if not isinstance(unit, str) :
            raise TypeError('unit is not a string')

        if unit not in ['cm', 'in'] :
            raise ValueError('unit is not one of the allowed values')
        if unit == 'inches' :
            amount = amount * self.s_cm_to_inches

        self.__motor_rotation = amount

    def set_default_speed(self, speed) :
        """
        Sets the default motor speed.

        If speed is outside of the allowed range, the value will be set to "-100" or "100"
        depending on whether the value is positive or negative.

        Setting the speed will not have any effect until one of the move or start methods is
        called, even if the Driving Base is already moving.

        :param speed: The default motor speed.
        :type speed:  int(-100,100)

        :raises TypeError: speed is not a number
        """

        if not isinstance(speed, int) :
            raise TypeError('speed is not a number')

        if speed > self.s_max_speed : speed = self.s_max_speed
        if speed < - self.s_max_speed : speed = - self.s_max_speed
        self.__default_speed = speed

    def set_stop_action(self, action) :
        """
        Sets the motor action that will be used when the Driving Base stops.

        If the action is "brake," the motors will stop quickly and be allowed to turn freely.

        If the action is "hold," the motors will actively hold their current position and cannot
        be turned manually.

        If the action is set to "coast," the motors will stop slowly and can be turned freely.

        Setting the "stop" action does not take immediate effect on the motors. The setting will
        be saved and used whenever stop() is called or when one of the move methods has completed
        without being interrupted.

        :param action: The desired action of the motors when the Driving Base stops.
        :type action:  string (coast, hold, brake)

        :raises TypeError: action is not a string
        :raises ValueError: action is not one of the allowed values
        """
        if not isinstance(action, str) :
            raise TypeError('action is not a string')

        if action not in self.s_motor_stop_actions :
            raise ValueError('action is not one of the allowed values')

        command = self.s_shared_scenario.command(self,'set_stop_action',{
            'action'    : action,
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
            self.__stop_action      = 'brake'

    def c_set_stop_action(self, action) :
        """
        Sets the action to be performed on stop

        .. warning:: This function is not part of the spike API. It is provided to update the
         component from scenario data and shall not be used by the end-user.

        :param action: The desired motor behavior when the motor stops.
        :type action:  string (coast, hold, brake)
        """
        with self.__mutex :
            self.__stop_action = action

    @property
    def left(self) :
        """
        Returns left motor

        .. warning:: This function is not part of the spike API. It is provided to update the
         component from scenario data and shall not be used by the end-user.

        :return: Left motor port, None if not set
        :rtype:  Motor
        """
        result = ''
        with self.__mutex :
            result = self.__left
        return result

    @left.setter
    def left(self, left):
        """
        Sets left motor

        .. warning:: This function is not part of the spike API. It is provided to update the
         component from scenario data and shall not be used by the end-user.

        :param left: Left motor
        :type left:  Motor
        """
        with self.__mutex :
            self.__left = left

    @property
    def right(self) :
        """
        Returns right port

        .. warning:: This function is not part of the spike API. It is provided to update the
         component from scenario data and shall not be used by the end-user.

        :return: Right motor, None if not set
        :rtype:  Motor
        """
        result = ''
        with self.__mutex :
            result = self.__right
        return result

    @right.setter
    def right(self, right):
        """
        Sets right port

        .. warning:: This function is not part of the spike API. It is provided to update the
         component from scenario data and shall not be used by the end-user.

        :param right: Right motor
        :type right:  Motor
        """
        with self.__mutex :
            self.__right = right

# pylint: enable=W0238, R0801
