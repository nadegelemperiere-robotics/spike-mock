# -------------------------------------------------------
# Copyright (c) [2022] Nadege LEMPERIERE
# All rights reserved
# -------------------------------------------------------
""" Software component registration management """
# -------------------------------------------------------
# Nadège LEMPERIERE, @04 november 2022
# Latest revision: 04 november 2022
# -------------------------------------------------------

# Local includes
from logging        import getLogger

# System includes
from threading      import  Lock

# pylint: disable=R0902
class ScenarioComponents() :
    """ Class managing all registered software components
     and their update along time """

    s_logger = getLogger('components')

    def __init__(self) :
        """ Constructor """
        self.__mutex = Lock()

        self.__motors           = {}
        self.__color_sensors    = {}
        self.__force_sensors    = {}
        self.__distance_sensors = {}
        self.__buttons          = {}
        self.__light_matrix     = None
        self.__speaker          = None
        self.__status_light     = None
        self.__motion_sensor    = None
        self.__ports            = {}

    def reset(self) :
        """ reset method """
        with self.__mutex :
            self.__motors           = {}
            self.__color_sensors    = {}
            self.__force_sensors    = {}
            self.__distance_sensors = {}
            self.__buttons          = {}
            self.__light_matrix     = None
            self.__speaker          = None
            self.__status_light     = None
            self.__motion_sensor    = None

    def configure(self, model) :
        """
        Configure components from robot ground truth

        :param model: robot static description
        :type model:  ScenarioModel
        """
        self.__ports = model.ports()

    def register(self, component, port1, port2) :
        """
        Register a software component associated with the robot

        :param component: the software component initiated
        :type component:  object (Button, ColorSensor,...)
        :param port1:     first port to check
        :type port1:      string
        :param port2:     second port to check
        :type port2:      string

        :raises ValueError: unknown component type
        """

        # register component according to their type
        cmp_type = str(type(component))

        with self.__mutex :

            if cmp_type == "<class 'spike.motor.Motor'>" :
                self.__register_motor(component, port1, port2)
            elif cmp_type == "<class 'spike.motorpair.MotorPair'>" :
                self.__register_motorpair(component, port1, port2)
            elif cmp_type == "<class 'spike.colorsensor.ColorSensor'>" :
                self.__register_colorsensor(component, port1, port2)
            elif cmp_type == "<class 'spike.forcesensor.ForceSensor'>" :
                self.__register_forcesensor(component, port1, port2)
            elif cmp_type == "<class 'spike.distancesensor.DistanceSensor'>" :
                self.__register_distancesensor(component, port1, port2)
            elif cmp_type == "<class 'spike.button.Button'>" :
                self.__register_button(component, port1, port2)
            elif cmp_type == "<class 'spike.lightmatrix.LightMatrix'>" :
                self.__register_lightmatrix(component, port1, port2)
            elif cmp_type == "<class 'spike.motionsensor.MotionSensor'>" :
                self.__register_motion_sensor(component, port1, port2)
            elif cmp_type == "<class 'spike.speaker.Speaker'>" :
                self.__register_speaker(component, port1, port2)
            elif cmp_type == "<class 'spike.statuslight.StatusLight'>" :
                self.__register_statuslight(component, port1, port2)
            elif cmp_type == "<class 'spike.control.Timer'>" :
                self.__register_timer(port1, port2)
            else :
                raise ValueError('Unknwon component type : ' + cmp_type)

    def update_from_data(self, time, data, hub) :
        """
        Update component from synthetic data

        :param time: current time
        :type time:  float
        :param data: data to use to update components states
        :type data:  ScenarioData
        :param hub:      hub dynamic state
        :type hub:       ScenarioHub
        """
        self.s_logger.debug('Updating from data')
        current_hub = hub.current()
        with self.__mutex :
            if self.__motion_sensor is not None :
                self.__motion_sensor.c_read(
                    data.extrapolate('yaw', time),
                    data.extrapolate('pitch', time),
                    data.extrapolate('roll', time),
                    data.extrapolate('gesture', time))
            for name,button in self.__buttons.items() :
                button.c_read(
                    data.extrapolate(name + '_is_pressed', time))
            for name,motor in self.__motors.items() :
                if name not in ['pair', 'left', 'right'] :
                    motor.c_read(
                        data.extrapolate(name + '_degrees', time))
            for name,distance in self.__distance_sensors.items() :
                distance.c_read(
                    data.extrapolate(name + '_distance', time))
            for name,color in self.__color_sensors.items() :
                color.c_read(
                    data.extrapolate(name + '_red', time),
                    data.extrapolate(name + '_green', time),
                    data.extrapolate(name + '_blue', time),
                    data.extrapolate(name + '_ambiant', time),
                    data.extrapolate(name + '_reflected', time))
            for name,force in self.__force_sensors.items() :
                force.c_read(
                    data.extrapolate(name + '_force', time))
            if self.__light_matrix :
                self.__light_matrix.c_read(current_hub['lightmatrix'])
            if self.__status_light :
                self.__status_light.c_read(
                    current_hub['statuslight']['status'],current_hub['statuslight']['color'])
            if self.__speaker :
                self.__speaker.c_read(
                    current_hub['speaker']['beeping'],
                    current_hub['speaker']['note'],
                    current_hub['speaker']['volume'])

# pylint: disable=R0914
    def update_from_mecanics(self, time, dynamics, hub) :
        """
        Update component from robot dynamic data

        :param time:     current time
        :type time:      float
        :param dynamics: robot dynamic state
        :type dynamics:  ScenarioDynamics
        :param hub:      hub dynamic state
        :type hub:       ScenarioHub
        """

        self.s_logger.debug('Updating from dynamics information')
        dynamics.extrapolate(time)
        current_dyn = dynamics.current()
        current_hub = hub.current()

        with self.__mutex :
            if self.__motion_sensor is not None :
                self.__motion_sensor.c_read(
                    current_dyn['yaw'], current_dyn['pitch'], current_dyn['roll'], None)
            for port, motor in self.__motors.items() :
                if port != 'pair' :
                    degrees = current_dyn['parts'][motor.port]['Motor'][0]['degrees']
                    motor.c_read(degrees)
            for port, sensor in self.__color_sensors.items() :
                if port in current_dyn['parts'] :
                    if 'ColorSensor' in current_dyn['parts'][sensor.port] :
                        part = current_dyn['parts'][sensor.port]['ColorSensor'][0]
                        red = part['red'] * 1024 / 255
                        gre = part['green'] * 1024 / 255
                        blu = part['blue'] * 1024 / 255
                        sensor.c_read(red, gre, blu ,0,1024)
            if self.__light_matrix :
                self.__light_matrix.c_read(current_hub['lightmatrix'])
            for name,button in self.__buttons.items() :
                for curbutton in current_hub['buttons'] :
                    if name == curbutton['side'] :
                        button.c_read(curbutton['pressed'])
            if self.__status_light :
                self.__status_light.c_read(
                    current_hub['statuslight']['status'],current_hub['statuslight']['color'])
            if self.__speaker :
                self.__speaker.c_read(
                    current_hub['speaker']['beeping'],
                    current_hub['speaker']['note'],
                    current_hub['speaker']['volume'])
# pylint: enable=R0914

    def __register_motor(self, component, port1, port2) :
        """
        Check if motor software component can be allocated
        Atomic operation

        :param component: the software component initiated
        :type component:  Motor
        :param port1:     first port to check
        :type port1:      string
        :param port2:     second port to check
        :type port2:      string

        :raises ValueError: Missing port or too many ports provided or unexisting port
         or port does not host a Motor or Motor already created on port
        """

        if port1 is None :
            raise ValueError('No port provided for motor')
        if port2 is not None :
            raise ValueError('More than one port provided for motor')
        if not port1 in self.__ports :
            raise ValueError('Port ' + port1 + ' not used on robot')
        if self.__ports[port1] != 'Motor' :
            raise ValueError('Port ' + port1 + ' does not host a motor')
        if port1 in self.__motors :
            raise ValueError('Motor already created on port ' + port1)

        component.port = port1
        self.__motors[port1] = component

    def __register_motorpair(self, component, port1, port2=None) :
        """
        Check if motorpair software component can be allocated
        Atomic operation

        :param component: the software component initiated
        :type component:  MotorPair
        :param port1:     first port to check
        :type port1:      string
        :param port2:     second port to check
        :type port2:      string

        :raises ValueError: Single motors not created on port or motorpair
         already created
        """

        if not port1 in self.__motors :
            raise ValueError('Motor not created on port ' + port1)
        if not port2 in self.__motors :
            raise ValueError('Motor not created on port ' + port2)
        if 'pair' in self.__motors or \
           'left' in self.__motors or \
           'right' in self.__motors :
            raise ValueError('Motorpair already created')

        component.left  = self.__motors[port1]
        component.right = self.__motors[port2]
        self.__motors['pair'] = component

    def __register_colorsensor(self, component, port1, port2) :
        """
        Check if color sensor software component can be allocated
        Atomic operation

        :param component: the software component initiated
        :type component:  ColorSensor
        :param port1:     first port to check
        :type port1:      string
        :param port2:     second port to check
        :type port2:      string

        :raises ValueError: Missing port or too many ports provided or unexisting port
         or port does not host a ColorSensor or ColorSensor already created on port
        """

        if port1 is None :
            raise ValueError('No port provided for color sensor')
        if port2 is not None :
            raise ValueError('More than one port provided for color sensor')
        if not port1 in self.__ports :
            raise ValueError('Port ' + port1 + ' not used on robot')
        if self.__ports[port1] != 'ColorSensor' :
            raise ValueError('Port ' + port1 + ' does not host a color sensor')
        if port1 in self.__color_sensors :
            raise ValueError('Color sensor already created on port ' + port1)

        component.port = port1
        self.__color_sensors[port1] = component

    def __register_forcesensor(self, component, port1, port2) :
        """
        Check if force sensor software component can be allocated
        Atomic operation

        :param component: the software component initiated
        :type component:  ForceSensor
        :param port1:     first port to check
        :type port1:      string
        :param port2:     second port to check
        :type port2:      string

        :raises ValueError: Missing port or too many ports provided or unexisting port
         or port does not host a ForceSensor or ForceSensor already created on port
        """

        if port1 is None :
            raise ValueError('No port provided for force sensor')
        if port2 is not None :
            raise ValueError('More than one port provided for force sensor')
        if not port1 in self.__ports :
            raise ValueError('Port ' + port1 + ' not used on robot')
        if self.__ports[port1] != 'ForceSensor' :
            raise ValueError('Port ' + port1 + ' does not host a force sensor')
        if port1 in self.__force_sensors :
            raise ValueError('Force sensor already created on port ' + port1)

        component.port = port1
        self.__force_sensors[port1] = component

    def __register_distancesensor(self, component, port1, port2) :
        """
        Check if distance sensor software component can be allocated
        Atomic operation

        :param component: the software component initiated
        :type component:  DistanceSensor
        :param port1:     first port to check
        :type port1:      string
        :param port2:     second port to check
        :type port2:      string

        :raises ValueError: Missing port or too many ports provided or unexisting port
         or port does not host a DistanceSensor or DistanceSensor already created on port
        """

        if port1 is None :
            raise ValueError('No port provided for distance sensor')
        if port2 is not None :
            raise ValueError('More than one port provided for distance sensor')
        if not port1 in self.__ports :
            raise ValueError('Port ' + port1 + ' not used on robot')
        if self.__ports[port1] != 'DistanceSensor' :
            raise ValueError('Port ' + port1 + ' does not host a distance sensor')
        if port1 in self.__distance_sensors :
            raise ValueError('Distance sensor already created on port ' + port1)

        component.port = port1
        self.__distance_sensors[port1] = component

    def __register_button(self, component, port1, port2) :
        """
        Check if button software component can be allocated
        Atomic operation

        :param component: the software component initiated
        :type component:  Button
        :param port1:     first port to check
        :type port1:      string
        :param port2:     second port to check
        :type port2:      string

        :raises ValueError: Missing side or too many sides provided or unknown side
         or Button already created on side
        """
        if port1 is None :
            raise ValueError('No side provided for button')
        if port2 is not None :
            raise ValueError('More than one side provided for button')
        if not port1 in ['left','right'] :
            raise ValueError('Unknown side for button')
        if port1 in self.__buttons :
            raise ValueError('Button already created on side ' + port1)

        component.side = port1
        self.__buttons[port1] = component

    def __register_lightmatrix(self, component, port1, port2) :
        """
        Check if light matrix software component can be allocated
        LightMatrix is part of the hub and not connected to a hub port
        Atomic operation

        :param component: the software component initiated
        :type component:  LightMatrix
        :param port1:     first port to check
        :type port1:      string
        :param port2:     second port to check
        :type port2:      string

        :raises ValueError: port provided or LightMatrix already created
        """

        if port1 is not None :
            raise ValueError('No port can be specified for light matrix')
        if port2 is not None :
            raise ValueError('No port can be specified for light matrix')
        if self.__light_matrix is not None :
            raise ValueError('Light matrix already created')

        self.__light_matrix = component

    def __register_motion_sensor(self, component, port1, port2) :
        """
        Check if motion sensor software component can be allocated
        MotionSensor is part of the hub and not connected to a hub port
        Atomic operation

        :param component: the software component initiated
        :type component:  MotionSensor
        :param port1:     first port to check
        :type port1:      string
        :param port2:     second port to check
        :type port2:      string

        :raises ValueError: port provided or MotionSensor already created
        """

        if port1 is not None :
            raise ValueError('No port can be specified for motion sensor')
        if port2 is not None :
            raise ValueError('No port can be specified for motion sensor')
        if self.__motion_sensor is not None :
            raise ValueError('Motion sensor already created')

        self.__motion_sensor = component

    def __register_speaker(self, component, port1, port2=None) :
        """
        Check if speaker software component can be allocated
        Speaker is part of the hub and not connected to a hub port
        Atomic operation

        :param component: the software component initiated
        :type component:  Speaker
        :param port1:     first port to check
        :type port1:      string
        :param port2:     second port to check
        :type port2:      string

        :raises ValueError: port provided or Speaker already created
        """

        if port1 is not None :
            raise ValueError('No port can be specified for speaker')
        if port2 is not None :
            raise ValueError('No port can be specified for speaker')
        if self.__speaker is not None :
            raise ValueError('Speaker already created')

        self.__speaker = component

    def __register_statuslight(self, component, port1, port2=None) :
        """
        Check if status light software component can be allocated
        StatusLight is part of the hub and not connected to a hub port
        Atomic operation

        :param component: the software component initiated
        :type component:  StatusLight
        :param port1:     first port to check
        :type port1:      string
        :param port2:     second port to check
        :type port2:      string

        :raises ValueError: port provided or StatusLight already created
        """

        if port1 is not None :
            raise ValueError('No port can be specified for status light')
        if port2 is not None :
            raise ValueError('No port can be specified for status light')
        if self.__status_light is not None :
            raise ValueError('Status light already created')

        self.__status_light = component

    def __register_timer(self, port1, port2=None) :
        """
        Check if timer software component can be allocated
        Timer can always be created and is not associated to a hub port
        Atomic operation

        :param component: the software component initiated
        :type component:  MotionSensor
        :param port1:     first port to check
        :type port1:      string
        :param port2:     second port to check
        :type port2:      string

        :raises ValueError: port provided
        """

        if port1 is not None :
            raise ValueError('No port can be specified for timer')
        if port2 is not None :
            raise ValueError('No port can be specified for timer')

# pylint: enable=R0902
