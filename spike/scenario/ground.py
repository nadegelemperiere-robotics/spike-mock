# -------------------------------------------------------
# Copyright (c) [2022] Nadege LEMPERIERE
# All rights reserved
# -------------------------------------------------------
""" Scenario ground management """
# -------------------------------------------------------
# Nadège LEMPERIERE, @04 november 2022
# Latest revision: 04 november 2022
# -------------------------------------------------------

# System includes
from logging    import getLogger

# Pillow includes
from PIL        import Image

# pylint: disable=C0103
class ScenarioGround() :
    """ Scene mat modelling """

    s_logger       = getLogger('ground')

    def __init__(self) :
        """ Constructor """
        # Dynamics modelling objects
        self.__mat    = None
        self.__height = 0
        self.__width  = 0
        self.__scale  = 0

    def configure(self, conf, path) :
        """
        Configure dynamics

        :param conf: ground configuration
        :type conf:  dictionary
        :param path: configuration file path
        :type path:  string
        """
        self.__check_configuration(conf)

        self.__scale = conf['scale']

        with Image.open(path + '/' + conf['image']) as img:
            self.__mat = img.convert("RGB").load()

            # self.__mat = Image.new("RGB", img.size, (255, 255, 255))
            # self.__mat.paste(img, mask=img.split()[3])
            self.__width, self.__height = img.size

# pylint: disable=R0914
    def get_color(self, north, east) :
        """
        Get color from position on mat

        :param north: north coordinate in centimeters
        :type north:  float
        :param east:  east coordinate in centimeters
        :type east:   float
        """

        result = {
            'red'   : 0,
            'green' : 0,
            'blue'  : 0
        }
        y = self.__height - north / self.__scale
        x = east / self.__scale

        if self.__mat is not None and \
           0 <= y < self.__height and \
           0 <= x < self.__width :

            x0 = int(x)
            x1 = x0 + 1
            if x1 >= self.__width : x1 = x0

            y0 = int(y)
            y1 = int(y) + 1
            if y1 >= self.__height : y1 = y0

            r00,g00,b00 = self.__mat[x0,y0]
            r10,g10,b10 = self.__mat[x1,y0]
            r01,g01,b01 = self.__mat[x0,y1]
            r11,g11,b11 = self.__mat[x1,y1]

            result['red']   = r00 * (x1 - x) * (y1 - y) + r10 * (x - x0) * (y1 - y) + \
                              r01 * (x1 - x) * (y - y0) + r11 * (x - x0) * (y - y0)
            result['green'] = g00 * (x1 - x) * (y1 - y) + g10 * (x - x0) * (y1 - y) + \
                              g01 * (x1 - x) * (y - y0) + g11 * (x - x0) * (y - y0)
            result['blue']  = b00 * (x1 - x) * (y1 - y) + b10 * (x - x0) * (y1 - y) + \
                              b01 * (x1 - x) * (y - y0) + b11 * (x - x0) * (y - y0)

        return result

# pylint: enable=R0914

    def __check_configuration(self, conf) :
        """
        Check input json configuration

        :param conf: configuration file content
        :type conf:  dictionary

        :raises ValueError: missing image or scale information
        """

        if not 'image' in conf :
            raise ValueError('Missing image for ground')
        if not 'scale' in conf :
            raise ValueError('Missing scale for ground')

# pylint enable=C0103
