# -------------------------------------------------------
# Copyright (c) [2022] Nadege LEMPERIERE
# All rights reserved
# -------------------------------------------------------
# Keywords to create data for module test
# -------------------------------------------------------
# Nadège LEMPERIERE, @1 november 2022
# Latest revision: 1 november 2022
# -------------------------------------------------------

# Robotframework includes
from robot.libraries.BuiltIn import BuiltIn, _Misc
from robot.api import logger as logger
from robot.api.deco import keyword
ROBOT = False

# Package includes
from spike.scenario.data            import ScenarioData

@keyword('Load Data')
def load_data(filename, sheet) :

    data = ScenarioData()
    data.configure(filename, sheet)

    return data
