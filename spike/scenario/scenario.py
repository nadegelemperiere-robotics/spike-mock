# -------------------------------------------------------
# Copyright (c) [2022] Nadege LEMPERIERE
# All rights reserved
# -------------------------------------------------------
""" Simulation scenario management API """
# -------------------------------------------------------
# Nadège LEMPERIERE, @04 november 2022
# Latest revision: 04 november 2022
# -------------------------------------------------------

# System includes
from json                   import load
from os                     import path
from threading              import Thread
from time                   import sleep
from logging                import config, Logger

# Local includes
from spike.scenario.data            import ScenarioData
from spike.scenario.timer           import ScenarioTimer
from spike.scenario.commands        import ScenarioCommands
from spike.scenario.components      import ScenarioComponents
from spike.scenario.model           import ScenarioModel
from spike.scenario.dynamics        import ScenarioDynamics
from spike.scenario.ground          import ScenarioGround
from spike.scenario.hub             import ScenarioHub

# pylint: disable=W0201, R0902, W0231
# Singleton structure makes it that __init__ is called for each copy of the singleton
# To avoid having it reinitialize the shared object, init is done once when calling
# __new__

class ScenarioThreadData() :
    """ Shared data for robot update thread """

    s_shared_timer = ScenarioTimer()
    s_data_modes = ['read', 'compute']
    s_time_modes = ['realtime', 'controlled']
    s_logger = Logger('scenario')

    def __init__(self) :
        """ Constructor """

        self.__model            = ScenarioModel()
        self.__mat              = ScenarioGround()
        self.__dynamics         = ScenarioDynamics(self.__model, self.__mat)
        self.__components       = ScenarioComponents()
        self.__data             = ScenarioData()
        self.__mode             = 'compute'
        self.__commands         = ScenarioCommands()
        self.__hub              = ScenarioHub()
        self.__is_step_ongoing  = False
        self.__is_started       = False
        self.restart()
        self.reinitialize()

    def restart(self) :
        """ Restart function : reset robot position and time"""
        self.s_shared_timer.reset()
        self.__dynamics.reset()
        self.__hub.reset()

    def reinitialize(self) :
        """ Reinitialize function """
        self.s_logger.debug('Resetting ScenarioThreadData')
        self.__shall_continue  = True
        self.__is_step_ongoing = False
        self.__is_started      = False
        self.__components.reset()

# pylint: disable=R0913
    def configure_from_values(self, scenario, robot, mode, period, north, east, yaw, logger=None) :
        """ Loading configuration from external data - compute mode only

        :param mode:     scenario time mode
        :type scenario:  string
        :param period:   scenario period in seconds
        :type period:    float
        :param north:    scenario starting north coordinate in centimeters
        :type north:     float
        :param east:     scenario starting east coordinate in centimeters
        :type east:      float
        :param yaw:      scenario starting yaw angle in degrees
        :type yaw:       float
        :param logger:   logging configuration file path
        :type logger:    string
        """
         # Configure logging
        if logger is not None : config.fileConfig(logger)

        # opening file and check configuration
        conf = {}
        with open(scenario,'r', encoding='UTF-8') as file :
            conf = load(file)
            file.close()
        conf = self.__merge_configuration(conf, mode, period, north, east, yaw)
        self.__mode = conf['data']['mode']

        # Configure ground
        if 'ground' in conf :
            self.__mat.configure(conf['ground'],path.dirname(scenario))

        # Configure robot
        self.__model.configure(robot)
        self.__dynamics = ScenarioDynamics(self.__model, self.__mat)
        self.__dynamics.configure(conf['data']['coordinates'])

        # Configure scenario
        self.__commands.configure(self.__dynamics, self.__hub)
        self.__components.configure(self.__model)
        self.s_shared_timer.configure(conf['time'])
# pylint: enable=R0913

    def configure_from_files(self, scenario, robot, sheet = None, logger = None) :
        """
        Configuration function

        :param scenario: scenario configuration file path
        :type scenario:  string
        :param robot:    robot configuration file path
        :type robot:     string
        :param sheet:    name of the sheet to use for component data feeding
        :type sheet:     string
        :param logger:   logging configuration file path
        :type logger:    string

        :raises ValueError: missing information, initial coordinates or workbook sheet
         or unknown data mode
        """

        # Configure logging
        if logger is not None : config.fileConfig(logger)

        # opening file and check configuration
        conf = {}
        with open(scenario,'r', encoding='UTF-8') as file :
            conf = load(file)
            file.close()
        self.__check_configuration(conf, sheet)
        self.__mode = conf['data']['mode']

        # Configure ground
        if 'ground' in conf :
            self.__mat.configure(conf['ground'],path.dirname(scenario))

        # Configure robot
        self.__model.configure(robot)
        if self.__mode == 'compute' :
            self.__dynamics = ScenarioDynamics(self.__model, self.__mat)
            self.__dynamics.configure(conf['data']['coordinates'])
        elif self.__mode == 'read' :
            self.__data.configure(path.dirname(scenario) + '/' + conf['data']['filename'], sheet)

        # Configure scenario
        self.__commands.configure(self.__dynamics, self.__hub)
        self.__components.configure(self.__model)
        self.s_shared_timer.configure(conf['time'])

    def register_component(self, component, port1, port2) :
        """
        Register a software component associated with the robot

        :param component: the software component initiated
        :type component:  object (Button, ColorSensor,...)
        :param port1:     first port to check
        :type port1:      string
        :param port2:     second port to check
        :type port2:      string
        """
        self.__components.register(component, port1, port2)

    def is_started(self) :
        """ Check if the processing is started

        :return: True if the processing is started, False otherwise
        :rtype:  boolean
        """
        return self.__is_started

    def step(self) :
        """ Step into time """
        self.s_shared_timer.step()
        self.__is_step_ongoing = True
        while self.__is_step_ongoing:
            print('sleeping')
            sleep(self.s_shared_timer.s_sleep_time)

    def command(self, component, name, args) :
        """
        Add new command to process

        :param component: the software component at the origin of the command
        :type component:  object (Button, ColorSensor,...)
        :param name:      command name
        :type name:       string
        :param args:      command parameters
        :type args:       dictionary

        :return:          command to perform
        :rtype:           generator function
        """
        return self.__commands.give(component, name, args)

    def get_status(self) :
        """ Return current robot status

        :return: the current robot status processed by the thread
        :rtype:  dictionary
        """

        self.s_logger.debug('Retrieving current scenario status')

        result = self.__dynamics.current()
        result['hub'] = self.__hub.current()

        return result

    def get_mat(self) :
        """ Return current robot status

        :return: the mat image with robot located on it
        :rtype:  PIL Image
        """
        status = self.__dynamics.current()
        corners = {}
        for pos, corner in status['corners'].items() :
            corners[pos] = {
                'north': corner['pose'].translation().X(),
                'east' : corner['pose'].translation().Y()
            }
        return self.__mat.get_scene(corners, status['x'], status['y'], status['yaw'])

    def set_shall_continue(self, value):
        """
        Shall continue setting function - Atomic function

        :param value: True if thread processing shall continue, false otherwise
        :type value:  boolean
        """
        self.__shall_continue = value

    def shall_continue(self) :
        """
        Shall continue accessor function - Atomic function

        :return: True if thread processing shall continue, false otherwise
        :rtype:  boolean
        """
        result = False
        result = self.__shall_continue

        return result

    def run(self) :
        """ Thread data processing function """
        try :


            while self.shall_continue():

                self.__is_started = True

                # Get current time
                time = self.s_shared_timer.time()

                # Check that a step has been processed from the beginning before stepping
                processing_step = self.__is_step_ongoing

                # Manage update from measurements
                if self.__mode == 'read' :
                    self.__components.update_from_data(time, self.__data, self.__hub)
                elif self.__mode == 'compute' :
                    self.__components.update_from_mecanics(time, self.__dynamics, self.__hub)
                    self.__dynamics.extrapolate(time)

                # command = self.process_command(self.__dynamics)
                # shall_continue = next(command)

                if processing_step : self.__is_step_ongoing = False
                self.s_shared_timer.sleep()

# pylint: disable=W0703
        except Exception as exc:
            self.s_logger.error('Caught error in scenario thread : %s',str(exc))
            self.set_shall_continue(False)
# pylint: enable=W0703

        self.__shall_continue   = True
        self.__is_step_ongoing  = False
        self.__is_started       = False
        self.s_logger.info('Scenario is over')

    def __check_configuration(self, conf, sheet) :
        """
        Check input json configuration

        :param conf:  configuration file content
        :type conf:   dictionary
        :param sheet: workbook sheet to use for synthetic data
        :type sheet:  string

        :raises ValueError: missing information, initial coordinates or workbook sheet
         or unknown data mode
        """

        if not 'time' in conf :
            raise ValueError('Missing time information in scenario configuration')
        if not 'data' in conf :
            raise ValueError('Missing data information in scenario configuration')
        if not 'mode' in conf['data'] :
            raise ValueError('Missing mode information in scenario data configuration')

        mode = conf['data']['mode']
        if not mode in self.s_data_modes :
            raise ValueError('Unknown data mode ' + mode)

        if mode == 'read' :
            if not 'filename' in conf['data']:
                raise ValueError('Missing data file in data configuration')
            if sheet is None :
                raise ValueError('Need sheet information to read data from workbook')
        elif mode == "compute" :
            if not 'coordinates' in conf['data'] :
                raise ValueError('Missing initial coordinates information in data configuration')

# pylint: disable=R0913
    def __merge_configuration(self, conf, mode, period, north, east, yaw) :
        """
        Check input configuration

        :param conf:     configuration file content
        :type conf:      dictionary
        :param period:   scenario period in seconds
        :type period:    float
        :param north:    scenario starting north coordinate in centimeters
        :type north:     float
        :param east:     scenario starting east coordinate in centimeters
        :type east:      float
        :param yaw:      scenario starting yaw angle in degrees
        :type yaw:       float

        :raises ValueError: missing information, initial coordinates or workbook sheet
         or unknown data mode
        """

        result = conf

        if not 'time' in conf :
            raise ValueError('Missing time information in scenario configuration')
        if not 'data' in conf :
            raise ValueError('Missing data information in scenario configuration')
        if not mode in self.s_time_modes:
            raise ValueError('Time mode ' + mode + ' not in allowed values')

        conf['data']['mode'] = 'computed'
        conf['data']['coordinates'] = {
            'north' : north,
            'east' : east,
            'yaw' : yaw
        }
        conf['time']['mode']   = mode
        conf['time']['period'] = period

        return result
# pylint: enable=R0913

class Scenario() :
    """ Singleton class managing the robot status """

    s_instance = None
    s_logger   = Logger('scenario')

    # pylint: disable=W0102
    def __new__(cls):
        """ Class new function

        :param cls: class reference
        :type cls:  object
        """

        if Scenario.s_instance is None :
            Scenario.s_instance = super().__new__(cls)
            Scenario.s_instance.s_init()
        return Scenario.s_instance

    def s_init(self) :
        """ Constructor for singleton / only called once """

        self.__processing_data      = ScenarioThreadData()
        self.__processing_thread    = None

    def __init__(self) :
        """ Contructor for each instantiation / do nothing """

# pylint: disable=R0913
    def configure_from_values(self, scenario, robot, mode, period, north, east, yaw, logger) :
        """ Loading configuration from file

        :param mode:     scenario time mode
        :type scenario:  string
        :param period:   scenario period in seconds
        :type period:    float
        :param north:    scenario starting north coordinate in centimeters
        :type north:     float
        :param east:     scenario starting east coordinate in centimeters
        :type east:      float
        :param yaw:      scenario starting yaw angle in degrees
        :type yaw:       float
        :param logger:   logger configuration file
        :type logger:    string
        """
        self.__processing_data.configure_from_values(
            scenario, robot, mode, period, north, east, yaw, logger)
# pylint: enable=R0913

    def configure_from_files(self, scenario, robot, sheet = None, logger=None) :
        """ Loading configuration from file

        :param scenario: path of json file to read scenario data from
        :type scenario:  string
        :param robot:    path of json file describing robot configuration
        :type robot:     string
        :param sheet:    sheet to read scenario data from
        :type sheet:     string
        :param logger:   logger configuration file
        :type logger:    string
        """
        self.__processing_data.configure_from_files(
            scenario, robot, sheet, logger)

    def register(self, component, port1=None, port2=None) :
        """
        Register a software component associated with the robot

        :param component: the software component initiated
        :type component:  object (Button, ColorSensor,...)
        :param port1:     first port to check
        :type port1:      string
        :param port2:     second port to check
        :type port2:      string
        """
        self.__processing_data.register_component(component, port1, port2)

    def start(self) :
        """ Robot starting function """
        self.__processing_thread    = Thread( target = self.__processing_data.run)
        self.__processing_thread.start()
        while not self.__processing_data.is_started() :
            sleep(ScenarioTimer.s_sleep_time)

    def step(self) :
        """ Step into time from a period set by configuation"""
        self.__processing_data.step()

    def command(self, component, name, args ) :
        """
        Process new robot command

        :param component: the software component at the origin of the command
        :type component:  object (Button, ColorSensor,...)
        :param name:      command name
        :type name:       string
        :param args:      command parameters
        :type args:       dictionary

        :return:          command to perform
        :rtype:           generator function
        """
        return self.__processing_data.command(
            component, name, args
        )

    def stop(self) :
        """ End scenario """

        self.__processing_data.set_shall_continue(False)
        while   self.__processing_thread is not None and \
                self.__processing_thread.is_alive() : pass

    def push_button(self, side) :
        """
        Push hub button

        :param side: Side of the button to push
        :type side: string
        """
        self.__processing_data.command(None, 'push_button',{'side':side })

    def release_button(self, side) :
        """
        Release hub button

        :param side: Side of the button to push
        :type side: string
        """
        self.__processing_data.command(None, 'release_button',{'side':side })

    def reinitialize(self) :
        """ Reinitialize scenario """
        if self.__processing_thread and self.__processing_thread.is_alive() :
            self.stop()
        self.__processing_data.reinitialize()

    def restart(self) :
        """ Restart scenario """
        if self.__processing_thread and self.__processing_thread.is_alive() :
            self.stop()
        self.__processing_data.restart()

    def status(self) :
        """
        Return robot current status

        :return: robot real status
        :rtype:  dictionary
        """
        return self.__processing_data.get_status()

    def mat(self) :
        """
        Return mat current image

        :return: mat image with robot located on it
        :rtype:  PIL Image
        """
        return self.__processing_data.get_mat()



# pylint: enable=W0201, R0902, W0231
