# -------------------------------------------------------
# Copyright (c) [2022] Nadege LEMPERIERE
# All rights reserved
# -------------------------------------------------------
""" Robot prime hub state management """
# -------------------------------------------------------
# Nadège LEMPERIERE, @04 november 2022
# Latest revision: 04 november 2022
# -------------------------------------------------------

# System includes
from threading  import Lock
from logging    import getLogger

# Local includes
from spike.scenario.timer   import ScenarioTimer


# pylint: disable=R0902
class ScenarioHub() :
    """ Robot hub status """

    s_shared_timer = ScenarioTimer()
    s_logger       = getLogger('hub')

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
        'HAPPY':[1,1,0,1,1,1,1,0,1,1,0,0,0,0,0,1,0,0,0,1,0,1,1,1,0], \
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

    def __init__(self) :
        """ Constructor """

        # LightMatrix modelling
        self.__matrix               = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

        # Status light
        self.__status_color         = 'white'
        self.__status_is_on         = False

        # Button
        self.__left_is_pressed      = False
        self.__right_is_pressed     = False

        # Speaker
        self.__is_speaker_beeping   = False
        self.__speaker_note         = 0
        self.__speaker_volume       = 0

        # Protection
        self.__mutex         = Lock()

    def reset(self) :
        """ Reset function """
        with self.__mutex :
            self.__matrix               = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
            self.__status_color         = 'white'
            self.__status_is_on         = False
            self.__left_is_pressed      = False
            self.__right_is_pressed     = False
            self.__is_speaker_beeping   = False
            self.__speaker_note         = 0
            self.__speaker_volume       = 0

    def __str__(self) :
        """
        string casting of dynamics object

        :return: string representing dynamic robot status
        :rtype:  string
        """

        result = ''

        result += 'lightmatrix : '
        for pixel in self.__matrix :
            result += str(pixel) + ' ,'
        if self.__left_is_pressed :
            result += ' button left is pressed'
        else :
            result += ' button left is not pressed'
        if self.__right_is_pressed :
            result += ', button right is pressed'
        else :
            result += ', button right is not pressed'
        if self.__status_is_on :
            result += ', status light is on with color ' + self.__status_color
        else :
            result += ', status light is off'
        if self.__is_speaker_beeping :
            result += ', speaker is beeping with note ' + str(self.__speaker_note) + \
                ' and volume ' + str(self.__speaker_volume)
        else :
            result += ', speaker is not beeping'

        return result

    def current(self) :
        """ Current robot dynamic status accessor

        :return: current robot dynamics measurements
        :rtype:  dictionary
        """

        result = {}

        with self.__mutex :
            result['buttons'] = []
            result['buttons'].append({'side':'left', 'pressed':self.__left_is_pressed})
            result['buttons'].append({'side':'right', 'pressed':self.__right_is_pressed})
            result['lightmatrix'] = self.__matrix
            result['statuslight'] = {
                'color' : self.__status_color,
                'status' : self.__status_is_on
            }
            result['speaker'] = {
                'volume' : self.__speaker_volume,
                'note' : self.__speaker_note,
                'beeping' : self.__is_speaker_beeping
            }

        return result

    def push_button(self,side) :
        """
        Push a button on the hub

        :param side: button side
        :type side:  string

        :raises ValueError: unknown button side
        """
        if side == 'left'    : self.__left_is_pressed = True
        elif side == 'right' : self.__right_is_pressed = True
        else : raise ValueError('Unknown button side')

    def release_button(self,side) :
        """
        Push a button on the hub

        :param side: button side
        :type side:  string

        :raises ValueError: unknown button side
        """
        if side == 'left'    : self.__left_is_pressed = False
        elif side == 'right' : self.__right_is_pressed = False
        else : raise ValueError('Unknown button side')


    def statuslight_on(self, color) :
        """
        Light status light generator function

        :param color: status light color
        :type color: string ('azure','black','blue','cyan','green',
            'orange','pink','red','violet','yellow','white')
        """
        with self.__mutex:
            self.__status_is_on = True
            self.__status_color = color
        yield False

    def statuslight_off(self) :
        """
        Light status off generator function
        """
        with self.__mutex :
            self.__status_is_on = False
        yield False

    def lightmatrix_show_image(self, image, brightness) :
        """
        Change light matrix displayed image

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

        """

        with self.__mutex :
            for i_pixel in range(0,25) :
                if self.s_lightmatrix_images[image][i_pixel] != 0 :
                    self.__matrix[i_pixel] = brightness
                else :
                    self.__matrix[i_pixel] = 0

        yield False

# pylint: disable=C0103
    def lightmatrix_set_pixel(self, x, y, brightness) :
        """
        Process LightMatrix set pixel command
        :param x:          pixel position, counting from the left.
        :type x:           integer [0,4]
        :param y:          pixel position, counting from the top.
        :type y:           integer [0,4]
        :param brightness: brightness of the pixel
        :type brightness:  integer [0,100]
        """

        with self.__mutex :
            self.__matrix[x + 5 * y] = brightness
        yield False
# pylint: enable=C0103

    def lightmatrix_write(self, text) :
        """ Process LightMatrix write command """
        with self.__mutex :
            for letter in text :
                self.__matrix = self.s_lightmatrix_images[str(letter).upper()]
                yield True

        yield False

    def lightmatrix_off(self) :
        """ Process LightMatrix off command """
        with self.__mutex :
            for i_line in range(0,5) :
                for i_column in range(0,5) :
                    self.__matrix[i_line * 5 + i_column] = 0

        yield False

    def speaker_beep(self, note, seconds) :
        """
        Process StatusLight beep command

        :param note: The MIDI note number
        :type note: float
        :param seconds: Beep duration in seconds
        :type seconds: float
        """
        with self.__mutex :
            self.__speaker_note = note
            self.__is_speaker_beeping = True

        time_init = self.s_shared_timer.time()
        while (self.s_shared_timer.time() - time_init) < seconds - 10e-6:
            yield True

        with self.__mutex :
            self.__is_speaker_beeping = False
        yield False

    def speaker_start_beep(self, note) :
        """
        Process StatusLight start beep command

        :param note: The MIDI note number
        :type note: float
        """
        with self.__mutex :
            self.__speaker_note = note
            self.__is_speaker_beeping = True
        yield False

    def speaker_stop(self) :
        """ Process StatusLight stop command """
        with self.__mutex :
            self.__is_speaker_beeping = False

        yield False

    def speaker_set_volume(self, volume) :
        """
        Process StatusLight set_volume command

        :param volume: The new volume percentage.
        :type volume:  int [0,100]
        """
        with self.__mutex :
            self.__speaker_volume = volume

        yield False
