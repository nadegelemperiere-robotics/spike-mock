# -------------------------------------------------------
# Copyright (c) [2022] Nadege LEMPERIERE
# All rights reserved
# -------------------------------------------------------
""" Hub light matrix mock API """
# -------------------------------------------------------
# Nadège LEMPERIERE, @04 november 2022
# Latest revision: 04 november 2022
# -------------------------------------------------------

# System includes
from threading  import Lock
from time       import sleep

# Local includes
from spike.scenario.scenario import Scenario
from spike.scenario.timer    import ScenarioTimer

# pylint: disable=R0801
class LightMatrix() :
    """ Hub light matrix mocking class

        Class is accessed simultaneously by the user side thread and the
        ground truth update thread. It is therefore protected by a mutex
    """

    # Constants
    s_lightmatrix_images = [
        'ANGRY', 'ARROW_E','ARROW_N','ARROW_NE','ARROW_NW','ARROW_S','ARROW_SE','ARROW_SW',
        'ARROW_W','ASLEEP','BUTTERFLY', 'CHESSBOARD','CLOCK1','CLOCK10','CLOCK11','CLOCK12',
        'CLOCK2','CLOCK3','CLOCK4','CLOCK5','CLOCK6','CLOCK7','CLOCK8','CLOCK9','CONFUSED','COW',
        'DIAMOND','DIAMOND_SMALL','DUCK','FABULOUS','GHOST','GIRAFFE','GO_RIGHT','GO_LEFT','GO_UP',
        'GO_DOWN','HAPPY', 'HEART', 'HEART_SMALL','HOUSE','MEH','MUSIC_CROTCHET','MUSIC_QUAVER',
        'MUSIC_QUAVERS','NO','PACMAN','PITCHFORK','RABBIT','ROLLERSKATE','SAD','SILLY','SKULL',
        'SMILE','SNAKE','SQUARE','SQUARE_SMALL','STICKFIGURE','SURPRISED','SWORD','TARGET',
        'TORTOISE','TRIANGLE','TRIANGLE_LEFT','TSHIRT','UMBRELLA','XMAS','YES','A','B','C','D','E',
        'F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y', 'Z'
    ]

    # Static variables
    s_shared_scenario  = Scenario()
    s_shared_timer     = ScenarioTimer()

####################################### SPIKE API METHODS ########################################

# pylint: disable=W0102
    def __init__(self) :
        """ Contructor """
        self.__mutex        = Lock()

        self.__matrix = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

        self.s_shared_scenario.register(self)

# pylint: enable=W0102

    def show_image(self, image, brightness=100) :
        """
        Shows an image on the Light Matrix.

        :param image: the name of the image to display
        :type image:  string (ANGRY, ARROW_E, ARROW_N, ARROW_NE, ARROW_NW, ARROW_S, ARROW_SE,
         ARROW_SW, ARROW_W, ASLEEP, BUTTERFLY, CHESSBOARD, CLOCK1, CLOCK10, CLOCK11, CLOCK12,
         CLOCK2, CLOCK3, CLOCK4, CLOCK5, CLOCK6, CLOCK7, CLOCK8, CLOCK9, CONFUSED, COW, DIAMOND,
         DIAMOND_SMALL, DUCK, FABULOUS, GHOST, GIRAFFE, GO_RIGHT, GO_LEFT, GO_UP, GO_DOWN, HAPPY,
         HEART, HEART_SMALL, HOUSE, MEH, MUSIC_CROTCHET, MUSIC_QUAVER, MUSIC_QUAVERS, NO, PACMAN,
         PITCHFORK, RABBIT, ROLLERSKATE, SAD, SILLY, SKULL, SMILE, SNAKE, SQUARE, SQUARE_SMALL,
         STICKFIGURE, SURPRISED, SWORD, TARGET, TORTOISE, TRIANGLE, TRIANGLE_LEFT, TSHIRT, UMBRELLA,
         XMAS, YES)
        :param brightness:  brightness of the image
        :type brightness:   integer [0,100]

        :raises TypeError:  image is not a string or brightness is not an integer
        :raises ValueError: image is not one of the allowed values.
        """

        if not isinstance(image, str) :
            raise TypeError('image is not a string')
        if not isinstance(brightness, int) :
            raise TypeError('brightness is not an integer')
        if not image in self.s_lightmatrix_images :
            raise ValueError('image is not one of the allowed values')

        command = self.s_shared_scenario.command(self,'show_image',{
            'image' : image,
            'brightness' : brightness
        })
        self.__process_command(command)

# pylint: disable=C0103
    def set_pixel(self, x, y, brightness=100):
        """
        Sets the brightness of one pixel (one of the 25 LEDs) on the Light Matrix.

        :param x:          pixel position, counting from the left.
        :type x:           integer [0,4]
        :param y:          pixel position, counting from the top.
        :type y:           integer [0,4]
        :param brightness: brightness of the pixel
        :type brightness:  integer [0,100]

        :raises TypeError:  x, y or brightness is not an integer.
        :raises ValueError: x, y is not within the allowed range of 0-4.
        """

        if not isinstance(x, int) :
            raise TypeError('x is not an integer')
        if not isinstance(y, int) :
            raise TypeError('y is not an integer')
        if not isinstance(brightness, int) :
            raise TypeError('brightness is not an integer')

        if x < 0 or x > 4 :
            raise ValueError('x value is not in [0,4]')
        if y < 0 or y > 4 :
            raise ValueError('y value is not in [0,4]')

        command = self.s_shared_scenario.command(self,'set_pixel',{
            'x' : x,
            'y' : y,
            'brightness' : brightness
        })
        self.__process_command(command)

# pylint: enable=C0103

    def write(self, text) :
        """
        Displays text on the Light Matrix, one letter at a time, scrolling from right to left.
        Your program will not continue until all of the letters have been shown.

        :param text: text to display
        :type text:  string
        """

        command = self.s_shared_scenario.command(self,'write',{
            'text' : text,
        })
        self.__process_command(command)

    def off(self) :
        """ Turns off all of the pixels on the Light Matrix. """

        command = self.s_shared_scenario.command(self,'off',{})
        self.__process_command(command)

    def __process_command(self, command) :
        """
        Process command until over

        :param command: command to process
        :type command: generator function
        """

        shall_continue = next(command)
        while shall_continue :
            sleep(self.s_shared_timer.s_sleep_time)
            shall_continue = next(command)

######################################## SCENARIO METHODS ########################################

    def c_reset(self) :
        """
        Reset function

        .. warning:: This function is not part of the spike API. It is provided to update the
         component from scenario data and shall not be used by the end-user.
        """

        with self.__mutex :
            for i_line in range(0,5) :
                for i_column in range(0,5) :
                    self.__matrix[i_line * 5 + i_column] = 0

    def c_read(self, matrix):
        """
        Matrix lighting function

        .. warning:: This function is not part of the spike API. It is provided to update the
         component from scenario data and shall not be used by the end-user.

        :param matrix:     5x5 array containing each pixel state
        :type matrix:      list
        """

        with self.__mutex :
            for i_line in range(0,5) :
                for i_column in range(0,5) :
                    self.__matrix[i_line * 5 + i_column] = matrix[i_line * 5 + i_column]

    def c_get_matrix(self) :
        """
        Return matrix state

        .. warning:: This function is not part of the spike API. It is provided to update the
         component from scenario data and shall not be used by the end-user.

        :return: 5x5 array containing each pixel state
        :rtype:  list
        """
        result = []
        with self.__mutex :
            result = self.__matrix

        return result

# pylint: enable=R0801
