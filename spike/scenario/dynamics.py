# -------------------------------------------------------
# Copyright (c) [2022] Nadege LEMPERIERE
# All rights reserved
# -------------------------------------------------------
""" Robot dynamic state management """
# -------------------------------------------------------
# Nadège LEMPERIERE, @04 november 2022
# Latest revision: 04 november 2022
# -------------------------------------------------------

# System includes
from math       import fabs, pi, copysign
from threading  import Lock
from logging    import getLogger


# wpilib includes
from wpimath.geometry   import Translation3d, Rotation3d, Pose3d, Twist3d
from wpimath.kinematics import DifferentialDriveKinematics, DifferentialDriveWheelSpeeds
from wpimath.kinematics import ChassisSpeeds

# multipledispatch includes
from multipledispatch   import dispatch

# Local includes
from spike.scenario.timer   import ScenarioTimer
from spike.scenario.parts   import ScenarioPartWheel


# pylint: disable=R0902
class ScenarioDynamics() :
    """ Robot dynamics modelisation """

    s_shared_timer = ScenarioTimer()
    s_logger       = getLogger('dynamics')

    def __init__(self, model, mat = None) :
        """Constructor

        :param model: robot static structure model
        :type model:  ScenarioModel
        :param mat:   mat model
        :type mat:    ScenarioGround
        """

        # Dynamics modelling objects
        self.__kinematics    = None
        self.__wheel_speeds  = None
        self.__chassis_speed = None
        self.__initial_pose  = None

        # Current computation time
        self.__current_time  = -1
        self.__current_pose  = None

        # Get robot parts involved in dynamics
        self.__model         = model
        self.__mat           = mat
        self.__parts         = self.__model.all()
        self.__corners       = self.__model.corners()
        self.__wheels        = {}
        self.__motors        = {}
        self.__colors        = {}
        by_type = self.__model.by_type()
        if 'Motor' in by_type :
            for motor in by_type['Motor'] :
                self.__motors[motor.port] = motor
        if 'Wheel' in by_type :
            for wheel in by_type['Wheel'] :
                self.__wheels[wheel.side] = wheel
        if 'ColorSensor' in by_type :
            for sensor in by_type['ColorSensor'] :
                self.__colors[sensor.port] = sensor

        # Protection
        self.__mutex         = Lock()

    def reset(self) :
        """ Reset function """
        with self.__mutex :
            self.s_logger.debug('Resetting ScenarioDynamics')
            self.__current_time      = 0
            self.__wheel_speeds      = DifferentialDriveWheelSpeeds(0,0)
            self.__chassis_speed     = ChassisSpeeds(0,0,0)
            self.__current_pose      = self.__initial_pose
            if self.__current_pose is not None :
                for part in self.__parts :
                    part.derive_pose(self.__current_pose)
                for corner in self.__corners.values() :
                    corner.derive_pose(self.__current_pose)
            for motor in self.__motors.values() : motor.reset()

    def configure(self, coordinates = None) :
        """
        Configure dynamics

        :param coordinates: initial robot coordinates, default is None
        :type coordinates:  dictionary {'north', 'east', 'yaw'}
        """
        self.s_logger.info('Configuring ScenarioDynamics')

        self.__check_configuration(coordinates)

        # Initialize
        self.__kinematics = DifferentialDriveKinematics(
            self.__wheels['left'].distance(self.__wheels['right']))

        # Initialize robot coordinates
        self.__initial_pose = Pose3d()
        if coordinates is not None :
            self.__initial_pose = Pose3d(
                Translation3d( coordinates['north'], coordinates['east'], self.__model.altitude()),
                Rotation3d(0,0,coordinates['yaw'] / 180 * pi))

        self.reset()

    def __str__(self) :
        """
        string casting of dynamics object

        :return: string representing dynamic robot status
        :rtype:  string
        """

        result = ''

        result += 'GLOBAL : date : ' + str(self.__current_time)
        if self.__current_pose :
            result += ', x : ' + str(self.__current_pose.translation().x)
            result += ', y : ' + str(self.__current_pose.translation().y)
            result += ', direction : ' + str(self.__modulo_dir(self.__current_pose.rotation().z))
        i_part = 0
        for part in self.__parts :
            result += '\n'
            result += 'PART ' + str(i_part) + ' : '
            result += str(part)
            i_part += 1
        for pos, corner in self.__corners.items() :
            result += '\n'
            result += 'CORNER ' + str(pos) + ' : '
            result += str(corner)

        return result

    def current(self) :
        """ Current robot dynamic status accessor

        :return: current robot dynamics measurements
        :rtype:  dictionary
        """

        result = {}

        with self.__mutex :
            result['time'] = self.__current_time
            result['x'] = self.__current_pose.translation().x
            result['y'] = self.__current_pose.translation().y
            result['yaw'] = self.__modulo_dir(self.__current_pose.rotation().z)
            result['pitch'] = self.__modulo_dir(self.__current_pose.rotation().y)
            result['roll'] = self.__modulo_dir(self.__current_pose.rotation().x)
            result['parts'] = {}
            for part in self.__parts :
                if part.port not in result['parts'] : result['parts'][part.port] = {}
                if part.type not in result['parts'][part.port] :
                    result['parts'][part.port][part.type] = []
                result['parts'][part.port][part.type].append(part.export())
            result['corners'] = {}
            for loc, corner in self.__corners.items() :
                result['corners'][loc] = corner.export()

            self.s_logger.info(str(self))

        return result

    @dispatch(str, str, int, int)
    def start(self, left, right, steering, speed) :
        """
        Motor Pair start function

        :param left:        left motor port
        :type left:         string (A, B, C, D, E or F)
        :param right:       right motor port
        :type right:        string (A, B, C, D, E or F)
        :param steering:    steering
        :type steering:     integer [-100,100]
        :param speed:       speed to use
        :type speed:        integer [-100,100]
        """
        with self.__mutex :
            self.__check_pair(left, right)
            speeds = self.__compute_motor_speeds_from_steering(steering, speed)
            self.__motors[left].command(speeds['left'],'counterclockwise')
            self.__motors[right].command(speeds['right'],'clockwise')
            self.__update_kinematics()

        yield False

# pylint: disable=R0913, E1130
    @dispatch(str, str, (float, int), int, int)
    def move(self, left, right, amount, steering, speed) :
        """
        Motor Pair move function

        :param left:        left motor port
        :type left:         string (A, B, C, D, E or F)
        :param right:       right motor port
        :type right:        string (A, B, C, D, E or F)
        :param amount:      displacement to perform
        :type amount:       float (cm)
        :param steering:    steering
        :type steering:     integer [-100,100]
        :param speed:       speed to use
        :type speed:        integer [-100,100]
        """

        with self.__mutex :
            self.__check_pair(left, right)
            if amount < 0 : speed = -speed
            speeds = self.__compute_motor_speeds_from_steering(steering, speed)
            self.__motors[left].command(speeds['left'],'counterclockwise')
            self.__motors[right].command(speeds['right'],'clockwise')
            self.__update_kinematics()

        start = {}
        for motor in self.__motors.values() :
            if motor.side() in ScenarioPartWheel.s_sides :
                start[motor.side()] = motor.degrees

        famount = fabs(amount)
        dist = 0
        sum_degrees = 0
        for motor in self.__motors.values() :
            if motor.side() in ScenarioPartWheel.s_sides:
                sum_degrees += 1
                dist += fabs((motor.degrees - start[motor.side()]) * motor.radius())

        while dist < sum_degrees * famount - 10e-6 :
            yield True
            dist = 0
            for motor in self.__motors.values() :
                if motor.side() in ScenarioPartWheel.s_sides is not None:
                    dist += fabs((motor.degrees - start[motor.side()]) * motor.radius())
            self.s_logger.debug(
                'time %lf : distance is %lf for an amount of %lf ',
                self.__current_time, dist, sum_degrees * famount)

        self.__motors[left].command(0,'counterclockwise')
        self.__motors[right].command(0,'clockwise')
        self.__update_kinematics()

        yield False

# pylint: enable=R0913, E1130

    @dispatch(str, str)
    def stop(self, left, right) :
        """
        Motor Pair stop function

        :param left:        left motor port
        :type left:         string (A, B, C, D, E or F)
        :param right:       right motor port
        :type right:        string (A, B, C, D, E or F)
        """
        with self.__mutex :
            self.__check_pair(left, right)
            self.__motors[left].command(0,'counterclockwise')
            self.__motors[right].command(0,'clockwise')
            self.__update_kinematics()

        yield False

    @dispatch(str, str, int, int)
    def start_at_power(self, left, right, steering, power) :
        """
        Motor Pair start_at_power function

        :param left:        left motor port
        :type left:         string (A, B, C, D, E or F)
        :param right:       right motor port
        :type right:        string (A, B, C, D, E or F)
        :param steering:    steering
        :type steering:     integer [-100,100]
        :param power:       power to use
        :type power:        integer [-100,100]
        """

        with self.__mutex :
            self.__check_pair(left, right)
            speeds = self.__compute_motor_speeds_from_steering(steering, power)
            self.__motors[left].command(speeds['left'],'counterclockwise')
            self.__motors[right].command(speeds['right'],'clockwise')
            self.__update_kinematics()

        yield False

    @dispatch(str, str, int, int)
    def start_tank(self, left, right, left_speed, right_speed) :
        """
        Motor Pair start_tank function

        :param left:        left motor port
        :type left:         string (A, B, C, D, E or F)
        :param right:       right motor port
        :type right:        string (A, B, C, D, E or F)
        :param left_speed:  left speed
        :type left_speed:   integer [-100,100]
        :param right_speed: right speed
        :type right_speed:  integer [-100,100]
        """
        with self.__mutex :
            self.__check_pair(left, right)
            self.__motors[left].command(left_speed,'counterclockwise')
            self.__motors[right].command(right_speed,'clockwise')
            self.__update_kinematics()

        yield False

# pylint: disable=R0913, E1130
    @dispatch(str, str, (float, int), int, int)
    def move_tank(self, left, right, amount, left_speed, right_speed) :
        """
        Motor Pair move_tank function

        :param left:        left motor port
        :type left:         string (A, B, C, D, E or F)
        :param right:       right motor port
        :type right:        string (A, B, C, D, E or F)
        :param amount:      displacement to perform
        :type amount:       float (cm)
        :param left_speed:  left speed
        :type left_speed:   integer [-100,100]
        :param right_speed: right speed
        :type right_speed:  integer [-100,100]
        """

        with self.__mutex :
            self.__check_pair(left, right)
            if amount < 0 :
                left_speed = -left_speed
                right_speed = -right_speed
            self.__motors[left].command(left_speed,'counterclockwise')
            self.__motors[right].command(right_speed,'clockwise')
            self.__update_kinematics()

        start = {}
        for motor in self.__motors.values() :
            if motor.side() in ScenarioPartWheel.s_sides :
                start[motor.side()] = motor.degrees

        famount = fabs(amount)
        dist = 0
        for motor in self.__motors.values() :
            if motor.side() in ScenarioPartWheel.s_sides :
                dist += fabs((motor.degrees - start[motor.side()]) * motor.radius())

        while dist < 2 * famount - 10e-6:
            yield True
            dist = 0
            for motor in self.__motors.values() :
                if motor.side() in ScenarioPartWheel.s_sides :
                    dist += fabs((motor.degrees - start[motor.side()]) * motor.radius())
            self.s_logger.debug(
                'time %lf : distance is %lf for an amount of %lf ',
                self.__current_time, dist, 2 * amount)

        self.__motors[left].command(0,'counterclockwise')
        self.__motors[right].command(0,'clockwise')
        self.__update_kinematics()

        yield False

# pylint: enable=R0913, E1130

    @dispatch(str, str, int, int)
    def start_tank_at_power(self, left, right, left_power, right_power) :
        """
        Motor Pair start_tank_at_power function

        :param left:        left motor port
        :type left:         string (A, B, C, D, E or F)
        :param right:       right motor port
        :type right:        string (A, B, C, D, E or F)
        :param left_power:  left power
        :type left_power:   integer [-100,100]
        :param right_power: right power
        :type right_power:  integer [-100,100]
        """
        with self.__mutex :
            self.__check_pair(left, right)
            self.__motors[left].command(left_power,'counterclockwise')
            self.__motors[right].command(right_power,'clockwise')
            self.__update_kinematics()

        yield False

    def set_degrees_counted(self, port, degrees) :
        """
        Single motor set_degrees_counted function

        :param port:    motor port
        :type port:     string
        :param degrees: the number of degrees to set
        :type degrees:  integer

        :raise RuntimeError: The port is not associated to a motor
        """

        with self.__mutex :
            if not port in self.__motors :
                raise RuntimeError('Port ' + port + ' does not host a motor')
            self.__motors[port].degrees = degrees

    @dispatch(str, int, int, str)
    def run_to_position(self, port, speed, degrees, direction) :
        """ Single Motor run_to_position function

        :param port:      the motor port
        :type port:       string
        :param speed:     speed command to pilot the motor
        :type speed:      integer
        :param degrees:   the absolute angular position to reach
        :type degrees:    integer [0,359]
        :param direction: The direction to use to reach the target position
        :type direction:  string (clockwise, counterclockwise, shortest path)

        :raise RuntimeError: The port is not associated to a motor
        """
        delta = 0
        mspeed = 0

        with self.__mutex :
            if not port in self.__motors :
                raise RuntimeError('Port ' + port + ' does not host a motor')

            delta_degrees_clockwise = 0

            delta_degrees_clockwise = degrees - self.__motors[port].degrees / pi * 180
            while delta_degrees_clockwise < 0 : delta_degrees_clockwise += 360
            while delta_degrees_clockwise > 360 : delta_degrees_clockwise -= 360

            delta_degrees_counterclockwise = self.__motors[port].degrees / pi * 180 - degrees
            while delta_degrees_counterclockwise < 0 : delta_degrees_counterclockwise += 360
            while delta_degrees_counterclockwise > 360 : delta_degrees_counterclockwise -= 360

            if direction == 'clockwise' :
                delta = delta_degrees_clockwise
                mspeed = fabs(speed)
            elif direction == 'counterclockwise':
                delta = delta_degrees_counterclockwise
                mspeed = -fabs(speed)
            elif direction == 'shortest path' :
                if delta_degrees_clockwise < delta_degrees_counterclockwise :
                    delta = delta_degrees_clockwise
                    mspeed = fabs(speed)
                else :
                    delta = delta_degrees_counterclockwise
                    mspeed = -fabs(speed)

        self.s_logger.info('Launching run_for_degrees with port %s - speed %lf - degrees %lf',
                  port, mspeed, delta)
        return self.run_for_degrees(port, mspeed, delta)

    @dispatch(str, (float, int), (float, int))
    def run_to_degrees_counted(self, port, speed, degrees) :
        """
        Single Motor run_to_degrees_counted function

        :param port:    the motor port
        :type port:     string
        :param speed:   speed command to pilot the motor
        :type speed:    int
        :param degrees: the number of degrees to rotate
        :type degrees:  float

        :raise RuntimeError: The port is not associated to a motor
        """

        with self.__mutex :
            if not port in self.__motors :
                raise RuntimeError('Port ' + port + ' does not host a motor')

        mspeed = fabs(speed)
        delta = degrees - self.__motors[port].degrees / pi * 180

        self.s_logger.info('Launching run_for_degrees with port %s - speed %lf - degrees %lf',
                  port, mspeed, delta)
        return self.run_for_degrees(port, mspeed, delta)

    @dispatch(str, (float, int), (float, int))
    def run_for_rotations(self, port, speed, rotations) :
        """ Single Motor run_to_position function

        :param port: Motor port
        :type port:  str
        :param speed: Speed command to pilot the motor
        :type speed: int
        :param rotations: The number of rotations to perform
        :type rotations: float

        :raises ValueError: The port is not associated to a motor
        """

        return self.run_for_degrees(port,speed,rotations * 360)

    @dispatch(str, (float, int), (float, int))
    def run_for_degrees(self, port, speed, degrees) :
        """ Single Motor run_to_position function

        :param port:    motor port
        :type port:     string
        :param speed:   speed command to pilot the motor
        :type speed:    integer
        :param degrees: the number of degrees to rotate
        :type degrees:  float

        :raises RuntimeError: The port is not associated to a motor
        """
        with self.__mutex :
            if not port in self.__motors :
                raise RuntimeError('Port ' + port + ' does not host a motor')

            ldegrees = copysign(degrees / 180 * pi, speed * degrees)
            lspeed = copysign(speed, speed * degrees)
            target_degrees = self.__motors[port].degrees + ldegrees

            self.__motors[port].command(lspeed,'clockwise')
            self.__update_kinematics()

        sgn = copysign(1, lspeed)
        while sgn * self.__motors[port].degrees < sgn * target_degrees  - 10e-6:
            yield True



        self.__motors[port].command(0,'clockwise')
        self.__update_kinematics()

        yield False

    @dispatch(str, (float, int), (float, int))
    def run_for_seconds(self, port, speed, seconds) :
        """ Single Motor run_to_position function

        :param port:    motor port
        :type port:     str
        :param speed:   speed command to pilot the motor
        :type speed:    int
        :param seconds: the number of seconds the rotation shall last
        :type seconds:  float

        :raises RuntimeError: The port is not associated to a motor
        """

        with self.__mutex :
            if not port in self.__motors :
                raise RuntimeError('Port ' + port + ' does not host a motor')

            self.__motors[port].command(speed,'clockwise')
            self.__update_kinematics()

        time_init = self.s_shared_timer.time()
        while (self.s_shared_timer.time() - time_init) < seconds  - 10e-6:
            yield True

        self.__motors[port].command(0,'clockwise')
        self.__update_kinematics()

        yield False

# pylint: disable=E0102
    @dispatch(str, int)
    def start(self, port, speed) :
        """ Single motor starting function

        :param port:  port of the motor to start
        :type port:   string
        :param speed: speed command to pilot the motor
        :type speed:  integer

        :raises RuntimeError: The port is not associated to a motor
        """
        with self.__mutex :
            if not port in self.__motors :
                raise RuntimeError('Port ' + port + ' does not host a motor')
            self.__motors[port].command(speed,'clockwise')
            self.__update_kinematics()

        yield False

    @dispatch(str, int)
    def start_at_power(self, port, power) :
        """ Single motor starting function

        :param port:  port of the motor to start
        :type port:   string
        :param power: power command to pilot the motor
        :type power:  integer

        :raises RuntimeError: The port is not associated to a motor
        """
        with self.__mutex :
            if not port in self.__motors :
                raise RuntimeError('Port ' + port + ' does not host a motor')
            self.__motors[port].command(power,'clockwise')
            self.__update_kinematics()

        yield False

    @dispatch(str)
    def stop(self, port) :
        """ Single motor stopping function

        :param port: port of the motor to stop
        :type port:  string

        :raises RuntimeError: The port is not associated to a motor
        """

        with self.__mutex :
            if not port in self.__motors :
                raise RuntimeError('Port ' + port + ' does not host a motor')
            self.__motors[port].command(0,'clockwise')
            self.__update_kinematics()

        yield False
# pylint: enable=E0102

    def extrapolate(self, time) :
        """
        Extrapolate robot status at a given date

        :param time: extrapolation date
        :type time:  float (seconds)
        """

        if self.__current_time != -1 :
            delta_time = time - self.__current_time
        else :
            delta_time = 0

        with self.__mutex :
            twist = Twist3d(
                self.__chassis_speed.vx * delta_time,
                self.__chassis_speed.vy * delta_time,
                0,
                0,
                0,
                -self.__chassis_speed.omega * delta_time)
            self.__current_pose = self.__current_pose.exp(twist)

            for part in self.__parts :
                part.derive_pose(self.__current_pose)
            for corner in self.__corners.values() :
                corner.derive_pose(self.__current_pose)
            for motor in self.__motors.values() :
                motor.extrapolate(delta_time)
            for sensor in self.__colors.values() :
                if self.__mat is not None:
                    sensor.read_color(self.__mat)

            self.__current_time = time

    def __compute_motor_speeds_from_steering(self, steering, speed) :
        """
        Compute left and right motors command from steering and speed
        The behavior of this function, with a discontinuities between 99% and 100%
        as been validated by experiment using spike motors

        :param steering: the direction and quantity to steer the Driving Base.
        :type steering:  integer [-100,100]
        :param steering: the speed at which the Driving Base will move while performing a curve.
        :type steering:  integer [-100,100]
        :return:         motor left and right command
        :rtype:          dictionary
        """

        result = { 'left' : 0, 'right' : 0 }

        if steering < 0 : result['left'] = round(int(speed * ( 100 + steering) / 100))
        else            : result['left'] = round(int(speed))
        if steering > 0 : result['right'] = round(int(speed * ( 100 - steering) / 100))
        else            : result['right'] = round(int(speed))

        if steering == 100 :
            result['left'] = speed
            result['right'] = -speed
        elif steering == -100:
            result['left'] = -speed
            result['right'] = speed

        return result

    def __update_kinematics(self):
        """ Update robot global kinematics from motor speeds """

        self.__wheel_speeds = DifferentialDriveWheelSpeeds(
            self.__wheels['left'].speed, self.__wheels['right'].speed)
        self.__chassis_speed = self.__kinematics.toChassisSpeeds(self.__wheel_speeds)
        self.s_logger.info(' wheels speed : %s - chassis speed : %s',
                           str(self.__wheel_speeds), str(self.__chassis_speed))
    def __check_pair(self, left, right) :
        """
        Check if left and right ports connects pairable motors

        :param left:  left motor port
        :type left:   string
        :param right: right motor port
        :type right:  string
        :return:      True if motors are pairable, False otherwise
        :type right:  boolean

        :raises RuntimeError: No motor in input ports or motor can not be paired
        """

        if not left in self.__motors :
            raise RuntimeError('No motor in port ' + left)
        if not right in self.__motors :
            raise RuntimeError('No motor in port ' + right)
        if not self.__motors[left].is_pairable(self.__motors[right]) :
            raise RuntimeError('RuntimeError: The motors could not be paired')

    def __check_configuration(self, coordinates) :
        """
        Check input json configuration

        :param conf: configuration file content
        :type conf:  dictionary

        :raises ValueError: Missing north, east or yaw coordinates
        """
        if coordinates is not None :
            if not 'north' in coordinates :
                raise ValueError('Missing north component in coordinates')
            if not 'east' in coordinates :
                raise ValueError('Missing east component in coordinates')
            if not 'yaw' in coordinates :
                raise ValueError('Missing yaw component in coordinates')

    def __modulo_dir(self, angle):
        """ Degrees to radians transformation

        :param input: angle
        :type input:  float (radians)
        :return:      angle
        :rtype:       float (degrees) [-180,180]
        """
        result = angle * 180 / pi
        while result < -180 : result += 360
        while result > 180  : result -= 360
        return result



# pylint: enable=R0902
