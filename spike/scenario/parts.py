# -------------------------------------------------------
# Copyright (c) [2022] Nadege LEMPERIERE
# All rights reserved
# -------------------------------------------------------
""" Classes describing lego robot component parts
https://www.ldraw.org/article/218.html and their dynamic
data """
# -------------------------------------------------------
# Nadège LEMPERIERE, @08 march 2022
# Latest revision: 08 march 2022
# -------------------------------------------------------

# System includes
from math                   import copysign, fabs, cos, sin, pi
from logging                import getLogger

# wpilib includes
from wpimath.geometry       import Translation3d, Rotation3d, Pose3d

# Local includes
from spike.scenario.abaqus  import ScenarioAbaqus

# pylint: disable=R0902, C0103
class ScenarioPart() :
    """ Class gathering data on a robot part """
    s_logger        = getLogger('parts')

    def __init__(self, copy=None) :
        """ Constructor

        :param copy: part to copy if copy constructor, None (default) otherwise
        :type copy:  ScenarioPart

        """

        if copy is None :
            self.__type     = ''
            self.__id       = None
            self.__pose     = Pose3d(Translation3d(),Rotation3d())
            self.__relative = Pose3d(Translation3d(),Rotation3d())
            self.__color    = -1
            self.__port     = None
        else :
            self.__type     = copy.type
            self.__id       = copy.id
            self.__pose     = copy.pose
            self.__relative = copy.relative
            self.__color    = copy.color
            self.__port     = copy.port

    @property
    def type(self) :
        """ Part type getter

        :return: part type
        :rtype:  string
        """
        return self.__type
    @type.setter
    def type(self, value):
        """
        Part type setter

        :param value: part type
        :type value:  string
        """
        self.__type = value

    @property
    def id(self) :
        """ Part identifier getter

        :return: part ldraw identifier
        :rtype:  string
        """
        return self.__id
    @id.setter
    def id(self, value):
        """
        Part ldraw identifier setter

        :param value: part ldraw identifier
        :type value:  string
        """
        self.__id = value

    @property
    def pose(self) :
        """ Part 3d absolute pose getter

        :return: part absolute pose
        :rtype:  Pose3d
        """
        return self.__pose
    @pose.setter
    def pose(self, value):
        """
        Part 3d absolute pose setter

        :param value: part 3d pose
        :type value:  Pose3d
        """
        self.__pose = value

    @property
    def relative(self) :
        """ Part 3d relative pose getter

        :return: part 3d relative pose
        :rtype:  Pose3d
        """
        return self.__relative
    @relative.setter
    def relative(self, value):
        """
        Part 3d relative pose setter

        :param value: part 3d relative pose
        :type value:  Pose3d
        """
        self.__relative = value

    @property
    def port(self) :
        """ Part port getter

        :return: part port, None if the component is not connected
        :rtype:  string
        """
        return self.__port
    @port.setter
    def port(self, value):
        """
        Part port setter

        :param value: part port
        :type value:  string
        """
        self.__port = value

    @property
    def color(self) :
        """ Part color getter

        :return: part color
        :rtype:  string
        """
        return self.__color
    @color.setter
    def color(self, value):
        """ Part color setter

        :param value: part color
        :type value:  string
        """
        self.__color = value

    def __eq__(self, other):
        """ Part equality operator

        :param other: other part to compare
        :type other:  ScenarioPart
        """
        if not isinstance(other, ScenarioPart):
            return False
        return (self.id       == other.id and \
                self.port     == other.port and \
                self.relative == other.relative and \
                self.color    == other.color)

    def __str__(self) :
        """
        Log part content as string

        :return: part description
        :rtype:  string
        """
        result = ''
        result += ' type : ' + self.type
        if self.port is not None : result += ' port : ' + self.port
        result += ' pose : ' + str(self.pose)
        return result

    def export(self) :
        """
        Export part as end-user dict

        :return: part representation from the user perspective
        :rtype:  dictionary
        """
        result = {}
        result['type'] = self.type
        result['port'] = self.port
        result['pose'] = self.pose
        return result

    def derive_relative(self, center) :
        """
        Compute part pose relative to the robot center pose

        :param center: robot center relative pose
        :type center:  Pose3d
        """

        rotation = self.pose.rotation().rotateBy(center.rotation() * -1.0)
        translation = self.pose.translation() - center.translation()
        self.relative = Pose3d(
            translation,
            rotation
        )
        self.s_logger.debug(
            'type : %s - NED absolute pose : %s - Center relative pose : %s',
            self.type, str(self.pose), str(self.relative))

    def derive_pose(self, center) :
        """
        Compute part absolute pose from the robot center absolute pose

        :param center: robot center absolute pose
        :type center:  Pose3d
        """

        self.pose = Pose3d(
            center.translation() + self.relative.translation().rotateBy(center.rotation()),
            self.relative.rotation().rotateBy(center.rotation())
        )
        self.s_logger.debug(
            'type : %s - Center relative pose : %s - NED absolute pose : %s',
            self.type, str(self.relative), str(self.pose))
# pylint: enable=R0902, C0103

class ScenarioPartMotor(ScenarioPart) :
    """ Class defining motor dynamics part """

    # Static variables
    s_speed_abaqus  = ScenarioAbaqus()
    s_ids           = ['54696','54675']

    @staticmethod
    def configure(filename, sheet) :
        """
        Static method to load speed abaqus from file

        :param filename: workbook to read abaqus from
        :type filename:  string
        :param sheet:    workbook sheet to read abaqus from
        :type sheet:     string
        """
        ScenarioPartMotor.s_logger.info('loading speed abaqus')
        ScenarioPartMotor.s_speed_abaqus.read(filename, sheet)

    def __init__(self, part) :
        """
        Motor constructor

        :param part : part to set as motor
        :type part  : ScenarioPart object

        :raises ValueError: part is not a known motor
        """

        if part.id not in self.s_ids :
            raise ValueError('Part ' + str(part.id) + ' is not a known motor')

        super().__init__(part)
        self.__wheel     = None
        self.__speed     = 0
        self.__degrees   = 0
        self.type = 'Motor'

        # If the motor is oriented to the north, then clockwise rotation
        # leads to a forward displacement
        # To check the motor orientation, we check how x NED vector (motor initial orientation)
        # is converted by pose. We also check the rotor direction, using the y coordinate of
        # transformation from -z. Depending on the value of the result, we decide motor orientation
        self.__clockwise_direction  = 1.0
        y_for_z = cos(self.pose.rotation().X()) * sin(self.pose.rotation().Y()) * \
                  sin(self.pose.rotation().Z()) - \
                  sin(self.pose.rotation().X()) * cos(self.pose.rotation().Z())

        if y_for_z < 0 :
            self.__clockwise_direction = -1.0

        self.reset()

    def reset(self) :
        """ Part dynamic data reset function """
        self.s_logger.debug('Resetting motor on port %s', self.port)
        self.__speed   = 0
        self.__degrees = 0

    @property
    def speed(self) :
        """ Rotation speed getter

        :return: motor rotation speed
        :rtype:  float (rads-1)
        """
        return self.__speed

    @property
    def degrees(self) :
        """ degrees getter

        :return: motor displacement degrees
        :rtype:  float (radians)
        """
        return self.__degrees
    @degrees.setter
    def degrees(self, value) :
        """
        Part 3d absolute pose setter

        :param value: motor displacement degrees
        :type value:  float (radians)
        """
        self.__degrees = value

    @property
    def wheel(self):
        """
        Wheel getter

        :return: motor associated wheel, None if motor is not connected to a wheel
        :rtype:  ScenarioPartWheel
        """
        return self.__wheel
    @wheel.setter
    def wheel(self, wheel) :
        """
        Wheel setter

        :param wheel: motor associated wheel
        :type wheel:  ScenarioPartWheel
        """
        self.__wheel = wheel

    @property
    def clockwise(self) :
        """
        Returns the direction of the displacement induced by clockwise rotation

        :return: -1 if clockwise rotation means moving backwards, 1 otherwise
        :rtype:  integer
        """
        return self.__clockwise_direction

    def __str__(self) :
        """
        Log part content as string

        :return: part description
        :rtype:  string
        """
        result = super().__str__()
        if self.__clockwise_direction == 1 : result += ' clockwise '
        else : result += ' counterclockwise '
        result += ' speed : ' + str(self.speed * 180 / pi)
        result += ' degrees : ' + str(self.degrees * 180 / pi)
        return result

    def export(self) :
        """
        Export motor as end-user dict

        :return: dictionary representing the motor from the user perspective
        :rtype:  dictionary
        """
        result = super().export()
        result['clockwise'] = self.__clockwise_direction
        result['speed'] = self.speed * 180 / pi
        result['degrees'] = self.degrees * 180 / pi
        return result

    def command(self, command, direction='clockwise') :
        """
        Derive motor rotation speed from command

        :param command:   motor command
        :type command:    integer [-100,100]
        :param direction: motor rotation direction
        :type direction:  string (clockwise or counterclockwise)
        """
        speed = self.s_speed_abaqus.get('speed', int(round(fabs(command))))
        self.__speed = copysign(speed, command)
        if direction == 'counterclockwise' :
            self.__speed = -self.__speed

    def radius(self) :
        """
        Access wheel radius if motor is connected to a wheel

        :return: wheel radius (None if motor is not linked to a wheel)
        :rtype:  float
        """
        result = None
        if self.__wheel is not None :
            result = self.__wheel.radius
        return result

    def side(self) :
        """
        Access wheel side if motor is connected to a wheel

        :return: wheel side (None if motor is not linked to a wheel)
        :rtype:  str (left or right)
        """
        result = None
        if self.__wheel is not None :
            result = self.__wheel.side
        return result

    def is_pairable(self, other) :
        """
        Check if 2 motors are pairables

        :param other: other motor to pair
        :type other:  ScenarioPartMotor
        :return:      True if motors can be paired, False otherwise
        :rtype:       boolean
        """
        result = (self.id == other.id)
        return result

    def extrapolate(self, delta) :
        """
        Extrapolate motor angular displacement from time difference

        :param delta: time period in seconds
        :type delta:  float
        """
        self.__degrees += self.__speed * delta

class ScenarioPartWheel(ScenarioPart) :
    """ Class defining wheel dynamics """

    s_wheel_radius_abaqus  = ScenarioAbaqus()
    s_ids                  = ['39367PB01','49295C01','32020C01']
    s_sides                = ['left', 'right']

    @staticmethod
    def configure(filename, sheet) :
        """
        Static method to load speed abaqus from file

        :param filename: workbook to read abaqus from
        :type filename:  string
        :param sheet:    workbook sheet to read abaqus from
        :type sheet:     string
        """
        ScenarioPartWheel.s_logger.info('loading wheel radius abaqus')
        ScenarioPartWheel.s_wheel_radius_abaqus.read(filename, sheet)

    def __init__(self, part, motor, spin) :
        """
        Constructor

        :param part: part to set as sheel
        :type part:  ScenarioPart
        :param part: motor associated to the wheel
        :type part:  ScenarioPartMotor
        :param spin: 1 if the wheel rotates in the same direction as its motor
         (even number of gears), -1 otherwise (odd number of gears)

        :raises ValueError: part is not a known wheel
        """

        if part.id not in self.s_ids :
            raise ValueError('Part ' + str(part.id) + ' is not a known wheel')

        super().__init__(part)

        self.__motor       = motor
        self.type          = 'Wheel'
        self.__side        = None
        self.__radius      = self.s_wheel_radius_abaqus.get('diameter', self.id) * 0.5
        self.__motor.wheel = self

        # Depending on the way wheels are connected to the motor (number of gears)
        # The wheel may rotate in the same direction as motor, or the opposite direction
        self.__spin     = spin

    @property
    def side(self) :
        """
        Wheel side getter

        :return: wheel side on robot
        :rtype:  string (left, right)
        """
        return self.__side
    @side.setter
    def side(self, value) :
        """
        Wheel side setter

        :param value: wheel side on motor
        :type value:  string (left, right)
        """
        self.__side = value

    @property
    def radius(self) :
        """
        Wheel radius getter

        :return: wheel radius
        :rtype:  float (cm)
        """
        return self.__radius
    @radius.setter
    def radius(self, value) :
        """
        Wheel radius setter

        :param value: wheel side on motor
        :type value:  string (left, right)
        """
        self.__radius = value

    @property
    def speed(self) :
        """
        Wheel linear speed getter

        :return: wheel linear
        :rtype:  float (cms-1)
        """
        result = 0
        if self.__motor :
            result = self.__motor.speed * self.__radius * self.__motor.clockwise
        return result

    def set_side(self, other) :
        """
        Set wheel side on model

        :param other: other wheel to compare for left/right
        :type other:  ScenarioPartWheel
        """

        if self.pose.translation().y < other.pose.translation().y : self.__side = 'left'
        else : self.__side = 'right'

    def export(self) :
        """
        Export wheel as end-user dict

        :return: dictionary representing the wheel from the user perspective
        :rtype:  dictionary
        """
        result = super().export()
        result['spin'] = self.__spin
        result['radius'] = self.__radius
        result['side'] = self.__side
        return result

    def distance(self, wheel) :
        """
        Compute distance between 2 wheels

        :param wheel: other wheel to analyse
        :type wheel:  ScenarioPartWheel
        :return:      distance between the 2 wheels
        :rtype:       float (cm)
        """
        result = self.pose.translation().distance(
            wheel.pose.translation())

        return result

class ScenarioPartColorSensor(ScenarioPart) :
    """ Class color sensor dynamics part """

    # Static variables
    s_logger        = getLogger('parts')
    s_ids           = ['37308C01']

    def __init__(self, part) :
        """
        Color sensor constructor

        :param part: part to set as motor
        :type part:  ScenarioPart

        :raises ValueError: part is not a known color sensor
        """

        if part.id not in self.s_ids :
            raise ValueError('Part ' + str(part.id) + ' is not a known color sensor')

        super().__init__(part)

        self.type    = 'ColorSensor'

        self.__red   = 0
        self.__green = 0
        self.__blue  = 0

    def __str__(self) :
        """
        Log color sensor content as string

        :return: part description
        :rtype:  string
        """
        result = super().__str__()

        result += ' red : '   + str(self.__red)
        result += ' green : ' + str(self.__green)
        result += ' blue : '  + str(self.__blue)

        return result

    def export(self) :
        """
        Export wheel as end-user dict

        :return: dictionary representing the wheel from the user perspective
        :rtype:  dictionary
        """
        result = super().export()
        result['red'] = self.__red
        result['green'] = self.__green
        result['blue'] = self.__blue
        return result

    def read_color(self, mat) :
        """
        Read color at sensor position on mat

        :param mat:   mat model
        :type mat:    ScenarioGround
        """

        self.__red = self.__green = self.__blue = 0

        # Project the color sensor orientation on the mat
        north = self.pose.translation().X()
        east  = self.pose.translation().Y()
        down  = self.pose.translation().Z()

        vecn = cos(self.pose.rotation().Y()) * cos(self.pose.rotation().Z())
        vece = cos(self.pose.rotation().Y()) * sin(self.pose.rotation().Z())
        vecd = sin(self.pose.rotation().Y())

        if vecd > 0 :
            t_inter = -down / vecd
            north = north + t_inter * vecn
            east = east  + t_inter * vece

            color = mat.get_color(north, east)
            if color is not None:
                self.__red = color['red']
                self.__green = color['green']
                self.__blue = color['blue']

class ScenarioPartHub(ScenarioPart) :
    """ Class hub dynamics part """

    # Static variables
    s_logger        = getLogger('parts')
    s_ids           = ['BB1142C01']

    def __init__(self, part) :
        """
        Hub constructor

        :param part: part to set as hub
        :type part:  ScenarioPart

        :raises ValueError: part is not a known hub
        """

        if part.id not in self.s_ids :
            raise ValueError('Part ' + str(part.id) + ' is not a known hub')

        super().__init__(part)
        self.type    = 'Hub'

class ScenarioPartForceSensor(ScenarioPart) :
    """ Class force sensor dynamics part """

    # Static variables
    s_logger        = getLogger('parts')
    s_ids           = ['37312C01']

    def __init__(self, part) :
        """
        Force sensor constructor

        :param part: part to set as force sensor
        :type part:  ScenarioPart

        :raises ValueError: part is not a known force sensor
        """

        if part.id not in self.s_ids :
            raise ValueError('Part ' + str(part.id) + ' is not a known force sensor')

        super().__init__(part)
        self.type    = 'ForceSensor'

class ScenarioPartDistanceSensor(ScenarioPart) :
    """ Class distance sensor dynamics part """

    # Static variables
    s_logger        = getLogger('parts')
    s_ids           = ['37316C01']

    def __init__(self, part) :
        """
        Distance sensor constructor

        :param part: part to set as distance sensor
        :type part:  ScenarioPart

        :raises ValueError: part is not a known distance sensor
        """

        if part.id not in self.s_ids :
            raise ValueError('Part ' + str(part.id) + ' is not a known distance sensor')

        super().__init__(part)
        self.type    = 'DistanceSensor'
