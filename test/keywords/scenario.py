# -------------------------------------------------------
# Copyright (c) [2022] Nadege LEMPERIERE
# All rights reserved
# -------------------------------------------------------
# Keywords to create data for module test
# -------------------------------------------------------
# Nadège LEMPERIERE, @1 november 2022
# Latest revision: 1 november 2022
# -------------------------------------------------------

# System includes
from time import time, sleep as local_sleep # To avoid conflict with the Sleep keyword...

# Robotframework includes
from robot.libraries.BuiltIn import BuiltIn, _Misc
from robot.api import logger as logger
from robot.api.deco import keyword
ROBOT = False

# Package includes
from spike.scenario.scenario    import Scenario

@keyword('Create Scenario')
def create_scenario(configuration, robot, sheet) :

    scenario = Scenario()
    scenario.configure(configuration, robot, sheet)
    return scenario

@keyword('Start Scenario')
def start_scenario(scenario) :
    scenario.start()

@keyword('Play Scenario During Steps')
def play_scenario_during_steps(step) :

    result      = True
    scenario    = Scenario()
    for _ in range(int(step)) :
        scenario.step()

    return result

@keyword('Stop Scenario')
def stop_scenario(scenario) :
    scenario.stop()

@keyword('Reset Scenario')
def reset_scenario(scenario) :
    scenario.reset()

@keyword('Get Time Milliseconds')
def get_time_milliseconds() :
    return int(round(time() * 1000)) * 1.0 / 1000
