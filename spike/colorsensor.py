# -------------------------------------------------------
# Copyright (c) [2022] Nadege LEMPERIERE
# All rights reserved
# -------------------------------------------------------
""" Color sensor mock API """
# -------------------------------------------------------
# Nadège LEMPERIERE, @04 november 2022
# Latest revision: 04 november 2022
# -------------------------------------------------------

# System includes
from time       import sleep
from threading  import Lock

# Webcolors includes
from webcolors import CSS3_HEX_TO_NAMES, hex_to_rgb

# Local includes
from spike.scenario.scenario import Scenario
from spike.scenario.timer    import ScenarioTimer

# pylint: disable=R0902, R0801
class ColorSensor() :
    """ Color sensor mocking class

        Class is accessed simultaneously by the user side thread and the
        ground truth update thread. It is therefore protected by a mutex
    """

    # Constants
    s_css3_to_spike_colormap = {
        'black'                 : 'black',
        'dimgray'               : 'black',
        'gray'                  : 'black',
        'darkgray'              : 'black',
        'darkslategray'         : 'black',
        'slategray'             : 'black',
        'silver'                : 'black',
        'lavender'              : 'violet',
        'thistle'               : 'violet',
        'plum'                  : 'violet',
        'violet'                : 'violet',
        'orchid'                : 'violet',
        'fuschia'               : 'violet',
        'magenta'               : 'violet',
        'mediumorchid'          : 'violet',
        'mediumpurple'          : 'violet',
        'blueviolet'            : 'violet',
        'darkviolet'            : 'violet',
        'darkorchid'            : 'violet',
        'darkmagenta'           : 'violet',
        'purple'                : 'violet',
        'indigo'                : 'violet',
        'powderblue'            : 'blue',
        'lightblue'             : 'blue',
        'lightskyblue'          : 'blue',
        'skyblue'               : 'blue',
        'deepskyblue'           : 'blue',
        'lightsteelblue'        : 'blue',
        'dodgerblue'            : 'blue',
        'cornflowerblue'        : 'blue',
        'steelblue'             : 'blue',
        'slateblue'             : 'blue',
        'mediumslateblue'       : 'blue',
        'darkslateblue'         : 'blue',
        'royalblue'             : 'blue',
        'mediumblue'            : 'blue',
        'darkblue'              : 'blue',
        'midnightblue'          : 'blue',
        'navy'                  : 'blue',
        'blue'                  : 'blue',
        'mediumaquamarine'      : 'cyan',
        'lightseagreen'         : 'cyan',
        'lightcyan'             : 'cyan',
        'aqua'                  : 'cyan',
        'aquamarine'            : 'cyan',
        'paleturquoise'         : 'cyan',
        'mediumturquoise'       : 'cyan',
        'turquoise'             : 'cyan',
        'darkturquoise'         : 'cyan',
        'cadetblue'             : 'cyan',
        'darkcyan'              : 'cyan',
        'teal'                  : 'cyan',
        'lime'                  : 'green',
        'green'                 : 'green',
        'darkseagreen'          : 'green',
        'limegreen'             : 'green',
        'greenyellow'           : 'green',
        'chartreuse'            : 'green',
        'lawngreen'             : 'green',
        'palegreen'             : 'green',
        'lightgreen'            : 'green',
        'mediumspringgreen'     : 'green',
        'springgreen'           : 'green',
        'mediumseagreen'        : 'green',
        'seagreen'              : 'green',
        'forestgreen'           : 'green',
        'darkgreen'             : 'green',
        'yellowgreen'           : 'green',
        'olivedrab'             : 'green',
        'olive'                 : 'green',
        'yellow'                : 'yellow',
        'darkkhaki'             : 'yellow',
        'lightyellow'           : 'yellow',
        'lemonchiffon'          : 'yellow',
        'lightgoldenrodyellow'  : 'yellow',
        'papayawhip'            : 'yellow',
        'moccasin'              : 'yellow',
        'peachpuff'             : 'yellow',
        'palegoldenrod'         : 'yellow',
        'khaki'                 : 'yellow',
        'gold'                  : 'yellow',
        'goldenrod'             : 'yellow',
        'orange'                : 'yellow',
        'peru'                  : 'yellow',
        'tan'                   : 'yellow',
        'burlywood'             : 'yellow',
        'saddlebrown'           : 'red',
        'sienna'                : 'red',
        'chocolate'             : 'red',
        'coral'                 : 'red',
        'tomato'                : 'red',
        'orangered'             : 'red',
        'red'                   : 'red',
        'pink'                  : 'red',
        'lightpink'             : 'red',
        'hotpink'               : 'red',
        'deeppink'              : 'red',
        'palevioletred'         : 'red',
        'mediumvioletred'       : 'red',
        'maroon'                : 'red',
        'darkred'               : 'red',
        'brown'                 : 'red',
        'firebrick'             : 'red',
        'crimson'               : 'red',
        'lightsalmon'           : 'red',
        'salmon'                : 'red',
        'darksalmon'            : 'red',
        'lightcoral'            : 'red',
        'indianred'             : 'red',
        'lightslategray'        : 'white',
        'white'                 : 'white',
        'snow'                  : 'white',
        'honeydew'              : 'white',
        'mintcream'             : 'white',
        'aliceblue'             : 'white',
        'ghostwhite'            : 'white',
        'whitesmoke'            : 'white',
        'seashell'              : 'white',
        'beige'                 : 'white',
        'oldlace'               : 'white',
        'floralwhite'           : 'white',
        'lightgray'             : 'white',
        'ivory'                 : 'white',
        'antiquewhite'          : 'white',
        'linen'                 : 'white',
        'lavenderblush'         : 'white',
        'mistyrose'             : 'white',
        'navajowhite'           : 'white',
    }
    s_allowed_colors = {
        'black','violet','blue','cyan','green','yellow','red','white'
    }

    # Static variables
    s_shared_scenario        = Scenario()
    s_shared_timer           = ScenarioTimer()

####################################### SPIKE API METHODS ########################################

    def __init__(self, port) :
        """
        Contructor

        :param port: the hub port to which the sensor is connected
        :type port:  string ('A','B','C','D','E' or 'F')
        """

        self.__mutex            = Lock()
        self.__port             = None

        self.__red              = 0
        self.__green            = 0
        self.__blue             = 0
        self.__light_ratio      = 0
        self.__reflected        = 0
        self.__ambiant          = 0
        self.__light1           = 100
        self.__light2           = 100
        self.__light3           = 100
        self.__light_ratio      = 1
        self.__previous_color   = ''

        self.s_shared_scenario.register(self, port)

    def get_color(self) :
        """
        Retrieves the detected color of a surface

        :return: name of the color sensed
        :rtype:  string
        """
        result = None

        with self.__mutex :
            selected_color = None
            distance_min = 255*255*10
            for color_hex, color_name in CSS3_HEX_TO_NAMES.items() :
                rgb = hex_to_rgb(color_hex)
                rmean = 0.5 * (rgb[0] + self.__red / 1024 * 255)
                dred = (rgb[0] - self.__red / 1024 * 255)
                dgreen = (rgb[1] - self.__green / 1024 * 255)
                dblue = (rgb[2] - self.__blue / 1024 * 255)
                distance = (2 + rmean / 256) * dred * dred + \
                            4 * dgreen * dgreen + \
                            ( 2 - (255 - rmean) / 256) * dblue * dblue
                if distance < distance_min :
                    distance_min = distance
                    selected_color = color_name
            result = selected_color

            if result in self.s_css3_to_spike_colormap :
                result = self.s_css3_to_spike_colormap[result]

            if result not in self.s_allowed_colors : result = None

        return result

    def get_ambiant_light(self) :
        """
        Retrieves the intensity of the ambient light.

        This causes the Color Sensor to change modes, which can affect your program in unexpected
        ways. For example, the Color Sensor can't read colors when it's in ambient light mode.

        :return: The ambient light intensity.
        :rtype: int [0,100]
        """
        result = 0
        with self.__mutex :
            result = int(round(self.__ambiant))
        return result

    def get_reflected_light(self) :
        """
        Retrieves the intensity of the reflected light.

        :return: The reflected light intensity
        :rtype: int [0,100]
        """
        result = 0
        with self.__mutex :
            result = int(round(self.__reflected * self.__light_ratio))
        return result

    def get_rgb_intensity(self) :
        """
        Retrieves the overall color intensity, and intensity of red, green, and blue

        :return: red, green, blue and overall intensity
        :rtype:  tuple ([0,1024],[0,1024],[0,1024],[0,1024])
        """

        result = 0
        with self.__mutex :
            result = (  self.__red , \
                        self.__green , \
                        self.__blue , \
                        (self.__red + self.__green + self.__blue) / 3)
        return result

    def get_red(self) :
        """
        Retrieves the color intensity of red.

        :return: red intensity
        :rtype:  integer [0,1024]
        """
        result = 0
        with self.__mutex :
            result = int(round(self.__red * self.__light_ratio))
        return result

    def get_green(self) :
        """
        Retrieves the color intensity of green.

        :return: green intensity
        :rtype:  integer [0,1024]
        """
        result = 0
        with self.__mutex :
            result = int(round(self.__green * self.__light_ratio))

        return result

    def get_blue(self) :
        """
        Retrieves the color intensity of blue.

        :return: blue intensity
        :rtype:  integer [0,1024]
        """
        result = 0
        with self.__mutex :
            result = int(round(self.__blue * self.__light_ratio))
        return result

    def wait_until_color(self, color) :
        """
        Waits until the Color Sensor detects the specified color.

        :param color: the name of the color
        :type color:  string ("black","violet","blue","cyan","green","yellow","red","white")
        """

        while self.get_color() != color :
            sleep(self.s_shared_timer.s_sleep_time)

    def wait_for_new_color(self) :
        """
        Waits until the Color Sensor detects a new color.

        The first time this method is called, it immediately returns the detected color.
        After that, it waits until the Color Sensor detects a color that’s different from
        the color that was detected the last time this method was used.

        :return: the name of the new color
        :rtype:  string ("black","violet","blue","cyan","green","yellow","red","white")
        """

        result = ''

        if self.__previous_color == '' :
            self.__previous_color = self.get_color()
            result = self.__previous_color
        else :
            while self.get_color() == self.__previous_color :
                sleep(self.s_shared_timer.s_sleep_time)
            result = self.get_color()
            self.__previous_color = ''

        return result

    def light_up_all(self, brightness=100) :
        """
        Lights up all of the lights on the Color Sensor at the specified brightness.

        This causes the Color Sensor to change modes, which can affect your program in unexpected
        ways. For example, the Color Sensor can't read colors when it's in light up mode.

        :param brightness: the desired brightness of the lights on the Color Sensor, default = 100
        :type brightness:  integer ([0,100%] - "0" is off, and "100" is full brightness.)

        :raises TypeError: brightness is not an integer
        """

        if not isinstance(brightness,int) :
            raise TypeError('brightness is not an integer')

        command = self.s_shared_scenario.command(self,'light_up',{
            'light1' : brightness,
            'light2' : brightness,
            'light3' : brightness
        })
        self.__process_command(command)

    def light_up(self, light_1, light_2, light_3) :
        """
        Sets the brightness of the individual lights on the Color Sensor.
        This causes the Color Sensor to change modes, which can affect your program in unexpected
        ways. For example, the Color Sensor can't read colors when it's in light up mode.

        :param light_1: the desired brightness of light 1.
        :type light_1:  integer ([0,100%] - "0" is off, and "100" is full brightness.)
        :param light_2: the desired brightness of light 2.
        :type light_2:  integer ([0,100%] - "0" is off, and "100" is full brightness.)
        :param light_3: the desired brightness of light 3.
        :type light_3:  integer ([0,100%] - "0" is off, and "100" is full brightness.)

        :raises TypeError: light_1, light_2, or light_3 is not an integer.
        """

        if not isinstance(light_1,int) :
            raise TypeError('light_1 is not an integer')
        if not isinstance(light_2,int) :
            raise TypeError('light_2 is not an integer')
        if not isinstance(light_3,int) :
            raise TypeError('light_3 is not an integer')

        command = self.s_shared_scenario.command(self,'light_up',{
            'light1' : light_1,
            'light2' : light_2,
            'light3' : light_3
        })
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
            self.__red          = 0
            self.__green        = 0
            self.__blue         = 0
            self.__light_ratio  = 0
            self.__reflected    = 0
            self.__ambiant      = 0
            self.__light1       = 100
            self.__light2       = 100
            self.__light3       = 100
            self.__light_ratio  = 1

# pylint: disable=R0913
    def c_read(self, red, green, blue, ambiant, reflected) :
        """
        Reads color from external source

        .. warning:: This function is not part of the spike API. It is provided to update the
         component from scenario data and shall not be used by the end-user.

        :param red:       red intensity
        :type red:        integer [0,1024]
        :param green:     green intensity
        :type green:      integer [0,1024]
        :param blue:      blue intensity
        :type blue:       integer [0,1024]
        :param ambiant:   ambiant intensity
        :type ambiant:    integer [0,1024]
        :param reflected: reflected intensity
        :type reflected:  integer [0,1024]
        """
        with self.__mutex :
            self.__red       = red
            self.__green     = green
            self.__blue      = blue
            self.__ambiant   = ambiant
            self.__reflected = reflected
# pylint: enable=R0913

    def c_set_lights(self, light1, light2, light3) :
        """
        Lights intensity setter

        .. warning:: This function is not part of the spike API. It is provided to update the
         component from scenario data and shall not be used by the end-user.

        :param light1: light1 brightness
        :type light1:  integer [0,100]
        :param light2: light2 brightness
        :type light2:  integer [0,100]
        :param light3: light3 brightness
        :type light3:  integer [0,100]
        """

        with self.__mutex :
            self.__light1 = light1
            self.__light2 = light2
            self.__light3 = light3
            self.__light_ratio = (self.__light1 + self.__light2 + self.__light3) / 300

    @property
    def port(self) :
        """ Gets the component connection port

        .. warning:: This function is not part of the spike API. It is provided to update the
         component from scenario data and shall not be used by the end-user.

        :return: the component port
        :rtype:  string
        """
        result = None
        with self.__mutex :
            result = self.__port
        return result

    @port.setter
    def port(self, port) :
        """ Sets the component connection port

        .. warning:: This function is not part of the spike API. It is provided to update the
         component from scenario data and shall not be used by the end-user.

        :param port: the component port
        :type port:  string
        """
        with self.__mutex :
            self.__port = port
# pylint: enable=R0902, R0801
