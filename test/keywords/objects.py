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
from threading import Thread
from time import sleep as local_sleep # To avoid conflict with the Sleep keyword...
from math import fabs
from inspect import isclass

# Robotframework includes
from robot.libraries.BuiltIn import BuiltIn, _Misc
from robot.api import logger as logger
from robot.api.deco import keyword
ROBOT = False

# Package includes
from spike                      import PrimeHub, ColorSensor, DistanceSensor, ForceSensor, Motor, MotorPair
from spike.control              import Timer, wait_for_seconds, wait_until
from spike.button               import Button
from spike.lightmatrix          import LightMatrix
from spike.motionsensor         import MotionSensor
from spike.speaker              import Speaker
from spike.statuslight          import StatusLight

@keyword('Create Object')
def create_object(object, *args) :

    result = None
    if   object == 'Hub'              : result = PrimeHub()
    elif object == 'Button'           : result = Button(args[0])
    elif object == 'ColorSensor'      : result = ColorSensor(args[0])
    elif object == 'DistanceSensor'   : result = DistanceSensor(args[0])
    elif object == 'ForceSensor'      : result = ForceSensor(args[0])
    elif object == 'LightMatrix'      : result = LightMatrix()
    elif object == 'MotionSensor'     : result = MotionSensor()
    elif object == 'Motor'            : result = Motor(args[0])
    elif object == 'MotorPair'        : result = MotorPair(args[0],args[1])
    elif object == 'Speaker'          : result = Speaker()
    elif object == 'StatusLight'      : result = StatusLight()
    elif object == 'Timer'            : result = Timer()
    else : raise Exception('Unknown object ' + object)

    return result

@keyword('Should Have Members')
def should_have_members(object, members) :

    result = True

    content = dir(object)
    for member in members :
        if not member in content :
            raise Exception('Missing ' + member + ' in ' + str(type(object)))

    return result

@keyword('Next Generator')
def next_generator(generator) :
    return next(generator)

@keyword('Use Object Method')
def use_object_method(object, method, shall_return=False, none_value=-1, *parameters):

    result = None

    formatted_parameters = []
    for param in parameters :
        formatted_parameters.append(convert_complex_type(param))
    formatted_parameters = tuple(formatted_parameters)

    if len(parameters) == 0 :
        if shall_return :
            result = getattr(object, method)()
        else :
            getattr(object, method)()
    else :
        if shall_return :
            result = getattr(object, method)(*formatted_parameters)
        else :
            getattr(object, method)(*formatted_parameters)

    if result is None : result = none_value
    elif isinstance(result, bool) and result : result = 'True'
    elif isinstance(result, bool) and not result : result = 'False'

    return result

@keyword('Start Method In A Thread')
def start_method_in_a_thread(object, method, *parameters):

    def thread_function(object, method, parameters):
        try :
            getattr(object, method)(*parameters)
        except Exception as exc:
            print(str(exc))

    formatted_parameters = []
    for param in parameters :
        formatted_parameters.append(convert_complex_type(param))
    formatted_parameters = tuple(formatted_parameters)

    thread = Thread(target=thread_function, args=(object, method, formatted_parameters))
    thread.start()

    return thread

@keyword('Start Function In A Thread')
def start_function_in_a_thread(function, *parameters):

    def thread_function(function, parameters):
        possibles = globals().copy()
        possibles.update(locals())
        func = possibles.get(function)
        func(*parameters)

    formatted_parameters = []
    for param in parameters :
        formatted_parameters.append(convert_complex_type(param))
    formatted_parameters = tuple(formatted_parameters)

    thread = Thread(target=thread_function, args=(function, formatted_parameters))
    thread.start()

    return thread

@keyword('Is Thread Running')
def is_thread_running(thread):
    local_sleep(0.01)
    return thread.is_alive()


@keyword('Stop Thread')
def stop_thread(thread):
    thread.stop()

@keyword('Should Be Equal As Numbers With Precision')
def should_be_equal_as_numbers_with_precision(value, test, precision) :
    if fabs(float(value) - float(test)) <= float(precision) : return True
    else : raise ValueError('Numbers are not equal to the given precision')

@keyword('Should Be Equal As Angles With Precision')
def should_be_equal_as_angles_with_precision(value, test, precision, modulo = 360) :
    delta = float(value) - float(test)
    while delta < -modulo/2 : delta += modulo
    while delta > modulo/2 : delta -= modulo
    if fabs(delta) <= float(precision) : return True
    else : raise ValueError('Angles are not equal to the given precision')


def convert_complex_type(param) :

    result = None

    if isinstance(param, dict):
        result = {}
        for key, value in param.items() :
            result[key] = convert_basic_types(value)
    elif isinstance(param, list) :
        result = []
        for value in param :
            result.append(convert_basic_types(value))
    elif str(type(param))[1:6] == 'class' and not isinstance(param, str):
        result = param
    else : result = convert_basic_types(param)

    return result


def convert_basic_types(param) :

    result = None
    if param.isdecimal() : result = int(param)
    elif param.replace('-','').isdecimal() : result = int(param)
    elif param.replace('.','').replace('-','').isdecimal() : result = float(param)
    elif param == 'True' : result = True
    elif param == 'False' : result = False
    else : result = param

    return result