# -------------------------------------------------------
# Copyright (c) [2022] Nadege LEMPERIERE
# All rights reserved
# -------------------------------------------------------
""" Software component commands management """
# -------------------------------------------------------
# Nadège LEMPERIERE, @04 november 2022
# Latest revision: 04 november 2022
# -------------------------------------------------------

# Local includes
from spike.scenario.timer   import ScenarioTimer

class ScenarioCommands() :
    """ Class managing robot command and their impact on dynamics """

    s_shared_timer = ScenarioTimer()

    def __init__(self) :
        """ Constructor """
        self.__logs       = []
        self.__dynamics   = None
        self.__hub        = None

    def reset(self) :
        """ Commands reset function """
        self.__logs       = []

    def configure(self, dynamics, hub) :
        """
        Configuration function for command

        :param dynamics: robot dynamic data to update from command
        :type dynamics:  ScenarioDynamics
        :param dynamics: robot hub data to update from command
        :type dynamics:  ScenarioHub
        """
        self.__dynamics = dynamics
        self.__hub      = hub
        self.reset()

# pylint: disable=R0915
    def give(self, component, name, args) :
        """
        Register a new command being given to the hub

        :param component: the software component at the origin of the command
        :type component:  object (Button, ColorSensor,...)
        :param name:      command name
        :type name:       string
        :param args:      command parameters
        :type args:       dictionary

        :raises ValueError: Command not known

        :return:          command to perform
        :rtype:           generator function
        """
        result = None

        # Append command to logs
        log = {}
        log['name'] = name
        log['args'] = args
        log['time'] = self.s_shared_timer.time()
        self.__logs.append(log)

        if component is None :
            if name == 'push_button'      : result = self.__hub.push_button(args['side'])
            elif name == 'release_button' : result = self.__hub.release_button(args['side'])
            else : raise ValueError('Unknown Button command')
        else :
            cmp_type = str(type(component))
            if cmp_type == "<class 'spike.motor.Motor'>" :
                port = component.port
                if name == 'run_to_position' : result = self.__dynamics.run_to_position(
                    port, args['speed'], args['degrees'], args['direction'])
                elif name == 'run_to_degrees_counted':
                    result = self.__dynamics.run_to_degrees_counted(
                        port, args['speed'], args['degrees'])
                elif name == 'run_for_degrees' : result = self.__dynamics.run_for_degrees(
                    port, args['speed'], args['degrees'])
                elif name == 'run_for_rotations' : result = self.__dynamics.run_for_rotations(
                    port, args['speed'], args['rotations'])
                elif name == 'run_for_seconds' : result = self.__dynamics.run_for_seconds(
                    port, args['speed'], args['seconds'])
                elif name == 'start' : result = self.__dynamics.start(
                    port, args['speed'])
                elif name == 'start_at_power' : result = self.__dynamics.start_at_power(
                    port, args['power'])
                elif name == 'stop' : result = self.__dynamics.stop(port)
                elif name == 'set_degrees_counted' : result = self.__dynamics.set_degrees_counted(
                    port, args['degrees'])
                elif name == 'set_stall_detection' :
                    result = self.__motor_set_stall_detection(component, args)
                elif name == 'set_stop_action' :
                    result = self.__motor_set_stop_action(component, args)
                else : raise ValueError('Unknown Motor command')
            elif cmp_type == "<class 'spike.motorpair.MotorPair'>" :
                left = component.left.port
                right = component.right.port
                if name == 'start'            : result = self.__dynamics.start(
                    left, right, args['steering'], args['speed'])
                elif name == 'move'           : result = self.__dynamics.move(
                    left, right, args['amount'], args['steering'], args['speed'])
                elif name == 'stop'           : result = self.__dynamics.stop(
                    left, right)
                elif name == 'start_at_power' : result = self.__dynamics.start_at_power(
                    left, right, args['steering'], args['power'])
                elif name == 'start_tank'     : result = self.__dynamics.start_tank(
                    left, right, args['left_speed'], args['right_speed'])
                elif name == 'move_tank'      : result = self.__dynamics.move_tank(
                    left, right, args['amount'], args['left_speed'], args['right_speed'])
                elif name == 'start_tank_at_power' : result = self.__dynamics.start_tank_at_power(
                    left, right,args['left_power'], args['right_power'])
                elif name == 'set_stop_action' :
                    result = self.__motorpair_set_stop_action(component, args)
                else : raise ValueError('Unknown MotorPair command')
            elif cmp_type == "<class 'spike.colorsensor.ColorSensor'>" :
                if name == 'light_up' : result = self.__colorsensor_light_up(component, args)
                else :                  raise ValueError('Unknown ColorSensor command')
            elif cmp_type == "<class 'spike.forcesensor.ForceSensor'>" :
                pass
            elif cmp_type == "<class 'spike.distancesensor.DistanceSensor'>" :
                pass
            elif cmp_type == "<class 'spike.button.Button'>" :
                pass
            elif cmp_type == "<class 'spike.lightmatrix.LightMatrix'>" :
                if name == 'show_image'  :
                    result = self.__hub.lightmatrix_show_image(args['image'], args['brightness'])
                elif name == 'set_pixel' :
                    result = self.__hub.lightmatrix_set_pixel(
                        args['x'],args['y'],args['brightness'])
                elif name == 'write'     :
                    result = self.__hub.lightmatrix_write(args['text'])
                elif name == 'off'       :
                    result = self.__hub.lightmatrix_off()
                else : raise ValueError('Unknown LightMatrix command')
            elif cmp_type == "<class 'spike.motionsensor.MotionSensor'>" :
                pass
            elif cmp_type == "<class 'spike.speaker.Speaker'>" :
                if name == 'beep'         :
                    result = self.__hub.speaker_beep(args['note'],args['seconds'])
                elif name == 'start_beep' :
                    result = self.__hub.speaker_start_beep(args['note'])
                elif name == 'stop'       :
                    result = self.__hub.speaker_stop()
                elif name == 'set_volume' :
                    result = self.__hub.speaker_set_volume(args['volume'])
                else : raise ValueError('Unknown StatusLight command')
            elif cmp_type == "<class 'spike.statuslight.StatusLight'>" :
                if name == 'on'           : result = self.__hub.statuslight_on(args['color'])
                elif name == 'off'        : result = self.__hub.statuslight_off()
                else :               raise ValueError('Unknown StatusLight command')

        return result
#pylint enable=R0915

    def __colorsensor_light_up(self, component, args) :
        """ Process StatusLight light up commands """
        component.c_set_lights( args['light1'], args['light2'], args['light3'])
        yield False

    def __motorpair_set_stop_action(self, component, args) :
        """ Process MotorPair set stop action command """
        component.left.c_stop_action(args['action'])
        component.right.c_stop_action(args['action'])
        yield False

    def __motor_set_stall_detection(self, component, args) :
        component.c_set_stall_detection( args['stop_when_stalled'])
        yield False

    def __motor_set_stop_action(self, component, args) :
        component.c_set_stop_action( args['action'])
        yield False
