# -------------------------------------------------------
# Copyright (c) [2022] Nadege LEMPERIERE
# All rights reserved
# -------------------------------------------------------
""" Hub mock API """
# -------------------------------------------------------
# Each mission differ, but at some points requires to go there,
# and then move back
# -------------------------------------------------------
# Nadège LEMPERIERE, @19 october 2022
# Latest revision: 19 october 2022
# -------------------------------------------------------

# Local includes
from spike.button       import Button
from spike.speaker      import Speaker
from spike.lightmatrix  import LightMatrix
from spike.statuslight  import StatusLight
from spike.motionsensor import MotionSensor

# Constants
hub_ports = ['A', 'B', 'C', 'D', 'E', 'F']

# pylint: disable=R0902
class PrimeHub() :
    """ Hub mocking class """

    def __init__(self) :
        """ Contructor """

        self.left_button    = Button('left')
        self.right_button   = Button('right')
        self.speaker        = Speaker()
        self.light_matrix   = LightMatrix()
        self.status_light   = StatusLight()
        self.motion_sensor  = MotionSensor()

# pylint: enable=R0902
