# -------------------------------------------------------
# Copyright (c) [2022] Nadege LEMPERIERE
# All rights reserved
# -------------------------------------------------------
""" Classes describing lego robot static structure """
# -------------------------------------------------------
# Nadège LEMPERIERE, @08 march 2022
# Latest revision: 08 march 2022
# -------------------------------------------------------

# System includes
from json                   import load
from os                     import path
from logging                import getLogger

# wpilib includes
from wpimath.geometry       import CoordinateSystem, CoordinateAxis, Rotation3d
from wpimath.geometry       import Pose3d, Transform3d, Translation3d

# numpy includes
from numpy                  import ndarray, array

# pyldraw includes
from ldraw.tools            import get_model
from ldraw.pieces           import Piece

# Local includes
from spike.scenario.parts   import ScenarioPart, ScenarioPartMotor, ScenarioPartWheel
from spike.scenario.parts   import ScenarioPartColorSensor, ScenarioPartForceSensor
from spike.scenario.parts   import ScenarioPartDistanceSensor, ScenarioPartHub

# pylint: disable=W0238, R0902, C0103
class ScenarioModel() :
    """ Class modelling robot static relative geometry """

    s_topics               = ['design','abaqus','components']
    s_parts_to_connect     = ['Motor', 'ColorSensor', 'DistanceSensor', 'ForceSensor']
    s_ports                = ['A','B','C','D','E','F']
    s_logger               = getLogger('model')

    def __init__(self) :
        """ Constructor """

        # Structure objects
        self.__pieces        = None
        self.__parts         = []
        self.__parts_by_type = {}
        self.__parts_by_port = {}
        self.__model         = None
        self.__front_left    = ScenarioPart()
        self.__front_right   = ScenarioPart()
        self.__back_left     = ScenarioPart()
        self.__back_right    = ScenarioPart()

        # Global data
        self.__altitude = 0

    def configure(self, filename) :
        """
        Configure robot

        :param filename: Robot configuration file path
        :type filename:  string

        :raises ValueError: Component not found for port, component type does not match ldraw type
         or 2 parts connected to the same hub port or missing attribute for component or missing
         robot design file or missing ldraw unit size or unknown topic in configuration file
        """

        # Load and check robot configuration
        self.s_logger.info('Loading configuration')
        conf = {}
        with open(filename,'r', encoding='UTF-8') as file :
            conf = load(file)
            file.close()
        self.__check_configuration(conf)

        # Open workbook and load sheets
        self.s_logger.info('Loading abaqus')
        ScenarioPartMotor.configure(path.dirname(filename) + '/' + conf['abaqus'], 'motor-command')
        ScenarioPartWheel.configure(path.dirname(filename) + '/' + conf['abaqus'], 'wheel-diameter')

        # Load parts from ldraw file
        self.s_logger.info('Loading ldraw model')
        parts, self.__model, self.__pieces = self.__read(
            path.dirname(filename) + '/' + conf['design']['filename'], \
            conf['design']['ldu'])
        parts = self.__convert_pose(parts, CoordinateSystem.NED())
        self.__front_left, self.__front_right, self.__back_left, self.__back_right = \
            self.__compute_shape(parts)
        parts, spins = self.__add_port_to_parts(conf, parts)
        self.__parts, self.__parts_by_type, self.__parts_by_port = \
            self.__organize_parts(parts, spins)

        # Compute the constants to be used for center tracking
        self.s_logger.info('Compute wheel center coordinates')
        translation = Translation3d()
        for wheel in self.__parts_by_type['Wheel'] :
            translation += wheel.pose.translation() * 1.0 / len(self.__parts_by_type['Wheel'])
        center_relative_pose = Pose3d(translation, Rotation3d())
        self.__altitude = center_relative_pose.translation().z

        self.s_logger.info('Compute other parts relative orientation from wheel center')
        for part in self.__parts :
            part.derive_relative(center_relative_pose)
        self.__front_left.derive_relative(center_relative_pose)
        self.__front_right.derive_relative(center_relative_pose)
        self.__back_left.derive_relative(center_relative_pose)
        self.__back_right.derive_relative(center_relative_pose)

    def altitude(self) :
        """
        Returns the robot wheels center altitude in NED local reference

        :return: robot altitude
        :rtype:  float (cm)
        """

        result = self.__altitude
        return result

    def corners(self):
        """
        Returns the model surrounding rectangle corners coordinates

        :return: front left, front right, back left and back right coordintates
        :rtype:  dict
        """
        result =  {
            'fl' : self.__front_left,
            'fr' : self.__front_right,
            'bl' : self.__back_left,
            'br' : self.__back_right
        }
        return result

    def ports(self) :
        """
        Returns the allocated ports with their part type

        :return: ports associated with their components
        :rtype:  dictionary
        """
        result = {}

        for part in self.__parts :
            if part.type in self.s_parts_to_connect :
                result[part.port] = part.type

        return result

    def by_port(self) :
        """
        Returns the robot parts indexed by port

        :return: robot parts
        :rtype:  dictionary
        """
        return self.__parts_by_port

    def by_type(self) :
        """
        Returns the robot parts indexed by type

        :return: robot parts
        :rtype:  dictionary
        """
        return self.__parts_by_type

    def all(self) :
        """
        Returns the robot active or sensive parts

        :return: robot parts
        :rtype:  list
        """
        return self.__parts

    def __check_configuration(self, conf) :
        """
        Check input json configuration

        :param conf: configuration file content
        :type conf:  dictionary

        :raises ValueError: missing attribute for component or missing robot design file
         or missing ldraw unit size or unknown topic in configuration file
        """

        for key, value in conf.items() :
            if key == 'components' :
                for comp in value :
                    if not 'port' in comp :
                        raise ValueError('Missing port for component')
                    if not comp['port'] in self.s_ports :
                        raise ValueError('Unknown port ' + value['port'])
                    if not 'type' in comp :
                        raise ValueError('Missing type for port ' + key + ' component')
                    if not 'id' in comp :
                        raise ValueError('Missing id for port ' + key + ' component')
                    if not 'index' in comp :
                        raise ValueError('Missing index for port ' + key + ' component')
            elif key == 'design' :
                if not 'filename' in value :
                    raise ValueError('Missing CAD filename')
                if not 'ldu' in value :
                    raise ValueError('Missing LDU value in centimeters')
            elif not key in self.s_topics :
                raise ValueError('Unknown topic ' + key + ' in robot configuration')


    def __read(self, filename, ldu=0.04) :
        """
        Build robot model from ldraw file

        :param filename: ldraw formatted filename path
        :type filename:  string
        :param ldu:      ldu (ldraw unit) size in centimeters, default 0.4 mm
        :type ldu:       float
        :return:         robot parts, robot model, ldraw parts
        :rtype:          list, list, dictionary
        """

        result = []

        model, pieces = get_model(filename)
        for obj in model.objects:
            if not isinstance(obj, Piece):
                continue

            part = ScenarioPart()
            part.identifier = obj.part
            part.color      = obj.colour
            rotation        = ndarray((3,3), buffer=array([
                round(obj.matrix.rows[0][0],5), round(obj.matrix.rows[0][1],5),
                round(obj.matrix.rows[0][2],5), round(obj.matrix.rows[1][0],5),
                round(obj.matrix.rows[1][1],5), round(obj.matrix.rows[1][2],5),
                round(obj.matrix.rows[2][0],5), round(obj.matrix.rows[2][1],5),
                round(obj.matrix.rows[2][2],5)
            ]))
            # The x axis of lego studio 2.0 does not match ldraw requirements, hence x -> -x
            part.pose = Pose3d(
                Translation3d(-obj.position.x * ldu, obj.position.y * ldu, -obj.position.z * ldu),
                Rotation3d(rotation))

            part.type = ''
            if part.identifier in ScenarioPartWheel.s_ids            : part.type = 'Wheel'
            elif part.identifier in ScenarioPartColorSensor.s_ids    : part.type = 'ColorSensor'
            elif part.identifier in ScenarioPartDistanceSensor.s_ids : part.type = 'DistanceSensor'
            elif part.identifier in ScenarioPartForceSensor.s_ids    : part.type = 'ForceSensor'
            elif part.identifier in ScenarioPartMotor.s_ids          : part.type = 'Motor'
            elif part.identifier in ScenarioPartHub.s_ids            : part.type = 'Hub'

            result.append(part)

        return result, model, pieces

    def __convert_pose(self, parts, system) :
        """
        Convert part pose in a new coordinates system

        :param parts:  robot parts with pose in ldraw reference
        :type parts:   list
        :param system: coordinate system to transform parts into
        :type system:  CoordinateSystem
        :return:       converted parts
        :rtype:        list
        """

        result = []

        ldraw_axis = CoordinateSystem(CoordinateAxis.E(), CoordinateAxis.D(), CoordinateAxis.N())
        for part in parts :
            # Rotation to go from ned rotated reference to ldraw straight
            pose = CoordinateSystem.convert( part.pose, ldraw_axis, system)
            # transformation from ldraw to ned
            transformation = Transform3d(
                Translation3d(),
                CoordinateSystem.convert(Rotation3d(), ldraw_axis, system) * (-1.0))
            # Rotation to go from ned straight to ned rotated reference
            pose = pose.transformBy(transformation)
            if part.type != '' :
                self.s_logger.debug(
                    'type : %s - Initial pose : %s - NED pose : %s',
                    part.type, str(part.pose), str(pose))
            part.pose = pose
            result.append(part)

        return result

    def __compute_shape(self, parts) :
        """
        Derive robot external shape from parts list

        :param parts: list of all robot parts
        :type parts:  list
        :return:      front left, front right, back left and back right corner of the robot
        :rtype:       tuple (front left, front right, back left, back right)
        """

        xfl = xfr = ybr = yfr = -1e8
        xbl = xbr = ybl = yfl = 1e8


        for part in parts :
            if part.pose.translation().X() > xfr : xfr = part.pose.translation().X()
            if part.pose.translation().X() > xfl : xfl = part.pose.translation().X()
            if part.pose.translation().X() < xbr : xbr = part.pose.translation().X()
            if part.pose.translation().X() < xbl : xbl = part.pose.translation().X()

            if part.pose.translation().Y() > yfr : yfr = part.pose.translation().Y()
            if part.pose.translation().Y() < yfl : yfl = part.pose.translation().Y()
            if part.pose.translation().Y() > ybr : ybr = part.pose.translation().Y()
            if part.pose.translation().Y() < ybl : ybl = part.pose.translation().Y()

        front_left  = ScenarioPart()
        front_right = ScenarioPart()
        back_left   = ScenarioPart()
        back_right  = ScenarioPart()
        front_left.pose = Pose3d(Translation3d(xfl,yfl,0),Rotation3d())
        front_right.pose = Pose3d(Translation3d(xfr,yfr,0),Rotation3d())
        back_left.pose = Pose3d(Translation3d(xbl,ybl,0),Rotation3d())
        back_right.pose = Pose3d(Translation3d(xbr,ybr,0),Rotation3d())

        return front_left, front_right, back_left, back_right

    def __add_port_to_parts(self, conf, parts) :
        """
        Add hub ports info to parts from the robot configuration file.
        Extract wheel spins info for further use

        :param conf:        robot configuration file content
        :type conf:         dictionary
        :param parts:       robot parts
        :type parts:        list

        :raises ValueError: Component not found for port, component type does not match ldraw type
         or 2 parts connected to the same hub port
        :return:            parts, wheel spins
        :rtype:             tuple (list, dictionary)

        """
        result = []
        spins = {}
        for comp in conf['components'] :

            selected_part = None
            i_part = 0
            for part in parts :
                if part.identifier == comp['id'] :
                    if comp['index'] == i_part :
                        selected_part = part
                    i_part += 1
            if selected_part is None and i_part == 0 :
                raise ValueError('Component not found in port ' + comp['port'])
            if selected_part is None and i_part != 0 :
                raise ValueError('Not enough components found in port ' + comp['port'])

            if selected_part.type != comp['type']:
                raise ValueError('Expected type does not match the part one')
            selected_part.port = comp['port']
            if 'spin' in comp :
                if not comp['port'] in spins :
                    spins[comp['port']] = []
                spins[comp['port']].append(comp['spin'])

            for other_part in parts :
                if  other_part.port == selected_part.port and \
                    other_part != selected_part and \
                    selected_part.type not in [None, 'Wheel'] and \
                    other_part.type not in [None, 'Wheel'] :
                    raise ValueError('2 parts with hub connexion on port ' + comp['port'])

            result.append(selected_part)

        # hub is not linked to a port, but we would like to retrieve it
        for part in parts :
            if part.type == 'Hub' :
                part.port = 'H'
                result.append(part)

        return result, spins


    def __organize_parts(self, parts, spins) :
        """
        Organize parts to be accessible by port or by type

        :param parts: list of parts to organize
        :type parts:  list
        :param spins: wheel spins already extracted from the configuration file
        :type spins:  dictionary
        :return:      extended parts, parts by type, parts by port
        :rtype:       tuple (list, dictionary, dictionary)

        :raises ValueError: Can not manage other than 2 wheels
        """

        all_parts = []
        result_by_type = {}
        result_by_port = {}

        for part in parts :

            typed_part = None
            if   part.type == 'Motor'           : typed_part = ScenarioPartMotor(part)
            elif part.type == 'ColorSensor'     : typed_part = ScenarioPartColorSensor(part)
            elif part.type == 'ForceSensor'     : typed_part = ScenarioPartForceSensor(part)
            elif part.type == 'DistanceSensor'  : typed_part = ScenarioPartDistanceSensor(part)
            elif part.type == 'Hub'             : typed_part = ScenarioPartHub(part)


            if typed_part is not None :
                if not part.type in result_by_type : result_by_type[part.type] = []
                if not part.port in result_by_port : result_by_port[part.port] = []

                result_by_type[part.type].append(typed_part)
                result_by_port[part.port].append(typed_part)
                all_parts.append(typed_part)

        # Process wheels
# pylint: disable=R1702
        wheels = {}
        for part in parts :
            if part.type == 'Wheel' :
                if part.port in result_by_port :
                    if not part.port in wheels : wheels[part.port] = []
                    for part2 in result_by_port[part.port] :
                        if part2.type == 'Motor' :
                            typed_part = ScenarioPartWheel(\
                                part, part2, spins[part.port][len(wheels[part.port])])
                            wheels[part.port].append(typed_part)
                            part2.wheel = typed_part

                            if not part.type in result_by_type : result_by_type[part.type] = []
                            if not part.port in result_by_port : result_by_port[part.port] = []
                            result_by_type[part.type].append(typed_part)
                            result_by_port[part.port].append(typed_part)
                            all_parts.append(typed_part)
# pylint: enable=R1702

        if 'Wheel' not in result_by_type or \
           len(result_by_type['Wheel']) != 2 :
            raise ValueError('Can not manage other than 2 wheels yet')

        result_by_type['Wheel'][0].set_side(result_by_type['Wheel'][1])
        result_by_type['Wheel'][1].set_side(result_by_type['Wheel'][0])

        return all_parts, result_by_type, result_by_port


# pylint: enable=W0238, R0902, C0103
