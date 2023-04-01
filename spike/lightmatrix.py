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
    s_lightmatrix_images = {
        'ANGRY':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], \
        'ARROW_E':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], \
        'ARROW_N':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], \
        'ARROW_NE':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], \
        'ARROW_NW':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], \
        'ARROW_S':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], \
        'ARROW_SE':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], \
        'ARROW_SW':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], \
        'ARROW_W':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], \
        'ASLEEP':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], \
        'BUTTERFLY':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], \
        'CHESSBOARD':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], \
        'CLOCK1':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], \
        'CLOCK10':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], \
        'CLOCK11':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], \
        'CLOCK12':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], \
        'CLOCK2':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], \
        'CLOCK3':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], \
        'CLOCK4':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], \
        'CLOCK5':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], \
        'CLOCK6':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], \
        'CLOCK7':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], \
        'CLOCK8':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], \
        'CLOCK9':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], \
        'CONFUSED':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], \
        'COW':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], \
        'DIAMOND':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], \
        'DIAMOND_SMALL':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], \
        'DUCK':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], \
        'FABULOUS':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], \
        'GHOST':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], \
        'GIRAFFE':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], \
        'GO_RIGHT':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], \
        'GO_LEFT':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], \
        'GO_UP':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], \
        'GO_DOWN':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], \
        'HAPPY':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], \
        'HEART': [0,1,0,1,0,1,1,1,1,1,1,1,1,1,1,0,1,1,1,0,0,0,1,0,0], \
        'HEART_SMALL':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], \
        'HOUSE':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], \
        'MEH':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], \
        'MUSIC_CROTCHET':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], \
        'MUSIC_QUAVER':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], \
        'MUSIC_QUAVERS':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],\
        'NO':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], \
        'PACMAN':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], \
        'PITCHFORK':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], \
        'RABBIT':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], \
        'ROLLERSKATE':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], \
        'SAD':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], \
        'SILLY':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], \
        'SKULL':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], \
        'SMILE':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], \
        'SNAKE':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], \
        'SQUARE':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], \
        'SQUARE_SMALL':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], \
        'STICKFIGURE':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], \
        'SURPRISED':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], \
        'SWORD':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], \
        'TARGET':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], \
        'TORTOISE':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], \
        'TRIANGLE':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], \
        'TRIANGLE_LEFT':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], \
        'TSHIRT':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], \
        'UMBRELLA':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], \
        'XMAS':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], \
        'YES':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], \
        'A':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], \
        'B':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], \
        'C':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], \
        'D':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], \
        'E':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], \
        'F':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], \
        'G':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], \
        'H':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], \
        'I':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], \
        'J':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], \
        'K':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], \
        'L':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], \
        'M':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], \
        'N':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], \
        'O':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], \
        'P':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], \
        'Q':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], \
        'R':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], \
        'S':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], \
        'T':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], \
        'U':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], \
        'V':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], \
        'W':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], \
        'X':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], \
        'Y':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], \
        'Z':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], \
    }

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

# pylint: disable=C0103
    def c_set_pixel(self, x, y, brightness=100):
        """
        Pixel lighting function

        .. warning:: This function is not part of the spike API. It is provided to update the
         component from scenario data and shall not be used by the end-user.

        :param x:          pixel position, counting from the left.
        :type x:           integer [0,4]
        :param y:          pixel position, counting from the top.
        :type y:           integer [0,4]
        :param brightness: brightness of the pixel
        :type brightness:  integer [0,100]
        """

        if x < 0 or x > 4 :
            raise ValueError('x value is not in [0,4]')
        if y < 0 or y > 4 :
            raise ValueError('y value is not in [0,4]')

        with self.__mutex :
            self.__matrix[x + 5 * y] = brightness
# pylint: enable=C0103

    def c_show_image(self, image, brightness=100) :
        """
        Image displaying function

        .. warning:: This function is not part of the spike API. It is provided to update the
         component from scenario data and shall not be used by the end-user.

        :param image: the name of the image to display
        :type image:  string (ANGRY, ARROW_E, ARROW_N, ARROW_NE, ARROW_NW, ARROW_S, ARROW_SE,
         ARROW_SW, ARROW_W, ASLEEP, BUTTERFLY, CHESSBOARD, CLOCK1, CLOCK10, CLOCK11, CLOCK12,
         CLOCK2, CLOCK3, CLOCK4, CLOCK5, CLOCK6, CLOCK7, CLOCK8, CLOCK9, CONFUSED, COW, DIAMOND,
         DIAMOND_SMALL, DUCK, FABULOUS, GHOST, GIRAFFE, GO_RIGHT, GO_LEFT, GO_UP, GO_DOWN, HAPPY,
         HEART, HEART_SMALL, HOUSE, MEH, MUSIC_CROTCHET, MUSIC_QUAVER, MUSIC_QUAVERS, NO, PACMAN,
         PITCHFORK, RABBIT, ROLLERSKATE, SAD, SILLY, SKULL, SMILE, SNAKE, SQUARE, SQUARE_SMALL,
         STICKFIGURE, SURPRISED, SWORD, TARGET, TORTOISE, TRIANGLE, TRIANGLE_LEFT, TSHIRT, UMBRELLA,
         XMAS, YES)
        :param brightness: brightness of the image
        :type brightness:  integer [0,100]
        """

        with self.__mutex :
            self.__matrix = self.s_lightmatrix_images[image]
            for i_pixel in range(0,25) :
                if self.__matrix[i_pixel] != 0 :
                    self.__matrix[i_pixel] = brightness

    def c_write(self, text) :
        """
        Text writing function (letters are displayed one by one)

        .. warning:: This function is not part of the spike API. It is provided to update the
         component from scenario data and shall not be used by the end-user.

        :param text: text to display
        :type text:  string
        """

        with self.__mutex :
            for letter in text :
                self.__matrix = self.s_lightmatrix_images[str(letter).upper()]
                sleep(0.01)

    def c_off(self) :
        """
        Shut down all the pixel of the light matrix

        .. warning:: This function is not part of the spike API. It is provided to update the
         component from scenario data and shall not be used by the end-user.
        """

        with self.__mutex :
            for i_line in range(0,5) :
                for i_column in range(0,5) :
                    self.__matrix[i_line * 5 + i_column] = 0

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
