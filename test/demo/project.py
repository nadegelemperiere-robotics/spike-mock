
from spike import PrimeHub, LightMatrix, Button, StatusLight, ForceSensor, MotionSensor, Speaker, ColorSensor, App, DistanceSensor, Motor, MotorPair
from spike.control import wait_for_seconds, wait_until, Timer
from math import *

def my_spike_project():


    hub = PrimeHub()

    hub.light_matrix.show_image('HAPPY')
    left = Motor('E')
    right = Motor('F')
    pair = MotorPair('E','F')
    pair.start(steering=99,speed=50)