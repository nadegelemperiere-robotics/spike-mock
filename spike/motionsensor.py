# -------------------------------------------------------
# Copyright (c) [2022] Nadege LEMPERIERE
# All rights reserved
# -------------------------------------------------------
""" Hub motion sensor mock API """
# -------------------------------------------------------
# Nadège LEMPERIERE, @04 november 2022
# Latest revision: 04 november 2022
# -------------------------------------------------------

# System includes
from time import sleep
from threading import Lock

# Local includes
from spike.scenario.scenario import Scenario

# pylint: disable=R0902,W0238
class MotionSensor() :
    """ Motion sensor mocking class

        Class is accessed simultaneously by the user side thread and the
        ground truth update thread. It is therefore protected by a mutex
    """

    # Constants
    s_gestures = [
        'shaken',
        'tapped',
        'doubletapped',
        'falling',
    ]

    # Static variables
    s_shared_scenario = Scenario()

####################################### SPIKE API METHODS ########################################

    def __init__(self) :
        """ Contructor """

        self.__mutex             = Lock()

        self.__yaw               = 0
        self.__pitch             = 0
        self.__roll              = 0
        self.__gesture           = ''

        self.__last_gesture      = ''
        self.__was_gesture       = {}
        for gesture in self.s_gestures :
            self.__was_gesture[gesture] = False
        self.__was_gesture['none'] = True

        self.__wait_gesture = None
        self.__zero_yaw_angle = 0

        self.s_shared_scenario.register(self)

    def get_roll_angle(self) :
        """
        Retrieves the Hub’s roll angle.
        Roll is the rotation around the front-back (longitudinal) axis.

        :return: the roll angle, specified in degrees.
        :rtype:  integer [-180,180]
        """
        result = None
        with self.__mutex :
            result = self.__roll
        return result

    def get_pitch_angle(self) :
        """
        Retrieves the Hub’s pitch angle.
        Pitch is the rotation around the left-right (transverse) axis.

        :return: the pitch angle, specified in degrees.
        :rtype:  integer [-180,180]
        """
        result = None
        with self.__mutex :
            result = self.__pitch
        return result

    def get_yaw_angle(self) :
        """
        Retrieves the Hub’s yaw angle.
        Yaw is the rotation around the front-back (vertical) axis

        :return: the yaw angle, specified in degrees.
        :rtype:  integer [-180,180]
        """
        result = None
        with self.__mutex :
            result = self.__yaw - self.__zero_yaw_angle
            while result < -180 : result += 360
            while result > 180 : result -= 360
        return result

    def reset_yaw_angle(self) :
        """ Sets the yaw angle to "0." """
        self.__zero_yaw_angle = self.__yaw

    def get_gesture(self) :
        """
        Retrieves the most recently-detected gesture.

        :return: last gesture
        :rtype:  string
        """
        result = None
        with self.__mutex :
            result = self.__last_gesture
        return result

    def was_gesture(self, gesture) :
        """
        Tests whether a gesture has occurred since the last time was_gesture()
        was used, or since the beginning of the program (for the first use).

        :param gesture: the name of the gesture.
        :type gesture:  string ("shaken","tapped","double-tapped","falling","none")

        :raises ValueError: gesture is not one of the allowed values.
        :raises TypeError:  gesture is not a string

        :return: True if the gesture has occurred since the last time was_gesture() was called,
         otherwise False.
        :rtype:  boolean
        """

        result = None
        if not isinstance(gesture,str) :
            raise TypeError('gesture is not a string')
        if gesture not in self.s_gestures :
            if gesture != 'none' :
                raise ValueError('gesture is not one of the allowed values')

        with self.__mutex :
            result = self.__was_gesture[gesture]
            for ges in self.s_gestures :
                self.__was_gesture[ges] = False
            self.__was_gesture['none'] = True

        return result

    def get_orientation(self) :
        """
        Retrieves the Hub's current orientation.

        :return: the hub current orientation
        :rtype:  string ('front','back','up','down','leftside','rightside')
        """

        pitch = self.get_pitch_angle()
        yaw = self.get_yaw_angle()

        # random value : to be confirmed by test
        result = ''
        if pitch > 10                   : result = 'up'
        elif pitch < -10                : result = 'down'
        elif -45 < yaw  <= 45           : result = 'front'
        elif 45 < yaw <= 135            : result = 'rightside'
        elif -135 < yaw <= -45          : result = 'leftside'
        elif yaw > 135 or yaw <= -135   : result = 'back'

        return result

    def wait_for_new_gesture(self) :
        """ Waits until a new gesture happens. """

        initial_gesture = self.get_gesture()
        while initial_gesture == self.get_gesture() :
            sleep(0.01)

    def wait_for_new_orientation(self) :
        """
        Waits until the Hub’s orientation changes.

        The first time this method is called, it will immediately return the current value.
        After that, calling this method will block the program until the Hub’s orientation
        has changed since the previous time this method was called.

        :return: the hub new orientation
        :rtype:  string ('front','back','up','down','leftside','rightside')
        """

        result = self.get_orientation()
        if self.__wait_gesture is None:
            self.__wait_gesture = result

        else :
            while self.__wait_gesture == result :
                sleep(0.01)
                result = self.get_orientation()
            self.__wait_gesture = None

        return result

######################################## SCENARIO METHODS ########################################

    def c_reset(self) :
        """
        Reset function

        .. warning:: This function is not part of the spike API. It is provided to update the
         component from scenario data and shall not be used by the end-user.
        """
        with self.__mutex :
            self.__yaw               = 0
            self.__pitch             = 0
            self.__roll              = 0
            self.__gesture           = ''

            self.__last_gesture      = ''
            self.__was_gesture       = {}
            for gesture in self.s_gestures :
                self.__was_gesture[gesture] = False
            self.__was_gesture['none'] = True

            self.__wait_gesture = None

    def c_read(self, yaw, pitch, roll, gesture) :
        """
        Update the current orientation from scenario data

        .. warning:: This function is not part of the spike API. It is provided to update the
         component from scenario data and shall not be used by the end-user.

        :param yaw:     the yaw angle, specified in degrees.
        :type yaw:      integer [-180,180]
        :param pitch:   the pitch angle, specified in degrees.
        :type pitch:    integer [-180,180]
        :param roll:    the roll angle, specified in degrees.
        :type roll:     integer [-180,180]
        :param gesture: the name of the gesture.
        :type gesture:  string ("shaken","tapped","double-tapped","falling","none")

        :raises ValueError: Invalid gesture
        """
        with self.__mutex :
            self.__yaw      = int(round(yaw))
            self.__roll     = int(round(roll))
            self.__pitch    = int(round(pitch))

            if gesture in self.s_gestures :
                self.__gesture = gesture
                self.__last_gesture  = gesture
                self.__was_gesture[gesture] = True
                self.__was_gesture['none'] = False
            elif gesture is None:
                self.__gesture = ''
            else :
                raise ValueError('Invalid gesture : ' + gesture)

# pylint: enable=R0902,W0238
