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
from logging                import getLogger
from base64                 import b64decode
from io                     import BytesIO

# Pillow includes
from PIL                    import Image, ImageDraw, ImageFont

# Local includes
from spike.scenario.font    import ROBOTO_CONDENSED

# pylint: disable=C0103
class ScenarioGround() :
    """ Scene mat modelling """

    s_logger       = getLogger('ground')
    s_font_ttf     = ROBOTO_CONDENSED

    def __init__(self) :
        """ Constructor """
        self.__mat    = None
        self.__img    = None
        self.__height = 0
        self.__width  = 0
        self.__scale  = 1

    def __del__(self) :
        """ Destroy ground image """
        if self.__mat is not None :
            self.__img.close()

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

        with Image.open(path + '/' + conf['image']) as self.__img:
            self.__mat = self.__img.convert("RGBA").load()
            self.__width, self.__height = self.__img.size

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

            r00,g00,b00,_ = self.__mat[x0,y0]
            r10,g10,b10,_ = self.__mat[x1,y0]
            r01,g01,b01,_ = self.__mat[x0,y1]
            r11,g11,b11,_ = self.__mat[x1,y1]

            result['red']   = r00 * (x1 - x) * (y1 - y) + r10 * (x - x0) * (y1 - y) + \
                              r01 * (x1 - x) * (y - y0) + r11 * (x - x0) * (y - y0)
            result['green'] = g00 * (x1 - x) * (y1 - y) + g10 * (x - x0) * (y1 - y) + \
                              g01 * (x1 - x) * (y - y0) + g11 * (x - x0) * (y - y0)
            result['blue']  = b00 * (x1 - x) * (y1 - y) + b10 * (x - x0) * (y1 - y) + \
                              b01 * (x1 - x) * (y - y0) + b11 * (x - x0) * (y - y0)

        return result

    def get_scene(self, corners, north, east, yaw) :
        """
        Get scene image with robot on it

        :param corners: Corners 3d poses
        :type corners:  dict
        :param north:   Movement center north coordinate
        :type north:    float
        :param east:    Movement center east coordinate
        :type east:     float
        :param yaw:     Movement center yaw coordinate
        :type yaw:      float

        :return: ground image with robot on it
        :rtype:  PIL Image
        """

        result = None

        if self.__img :
            result = self.__img.copy().convert('RGBA')

            yfl = self.__height - corners['fl']['north'] / self.__scale
            xfl = corners['fl']['east']  / self.__scale
            yfr = self.__height - corners['fr']['north'] / self.__scale
            xfr = corners['fr']['east']  / self.__scale
            ybl = self.__height - corners['bl']['north'] / self.__scale
            xbl = corners['bl']['east']  / self.__scale
            ybr = self.__height - corners['br']['north'] / self.__scale
            xbr = corners['br']['east']  / self.__scale

            yfl = max(min(yfl, self.__height - 1),0)
            yfr = max(min(yfr, self.__height - 1),0)
            ybl = max(min(ybl, self.__height - 1),0)
            ybr = max(min(ybr, self.__height - 1),0)
            xfl = max(min(xfl, self.__width  - 1),0)
            xfr = max(min(xfr, self.__width  - 1),0)
            xbl = max(min(xbl, self.__width  - 1),0)
            xbr = max(min(xbr, self.__width  - 1),0)

            text = f"N = {north} cm\n E = {east} cm\n yaw = {yaw} °"
            font = ImageFont.truetype(BytesIO(b64decode(self.s_font_ttf)), 30)

            draw = ImageDraw.Draw(result)
            draw.polygon([xfl,yfl,xfr,yfr,xbr,ybr,xbl,ybl],width=5,outline=(255, 0, 0, 255))
            draw.text([10,10], text, fill=(255, 0, 0, 255), font=font, spacing=5, align='left')

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
