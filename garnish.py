# -*- coding: utf-8 -*-

#===============================================================================
#
#    Copyright 2013 Horacio Guillermo de Oro <hgdeoro@gmail.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#===============================================================================

import datetime
import json
import logging
import os
import subprocess
import sys

from StringIO import StringIO

from PIL import Image, ImageColor, ImageDraw, ImageFont, ImageOps

# TODO: use system font or add font file - check license!

logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
logger = logging.getLogger('GarnishMyPic')

CAMERA_ICON = '\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x01,\x01,\x00\x00\xff\xdb' + \
    '\x00C\x00\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01' + \
    '\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01' + \
    '\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01' + \
    '\x01\x01\x01\x01\x01\x01\xff\xdb\x00C\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01' + \
    '\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01' + \
    '\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01' + \
    '\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\xff\xc2\x00\x11\x08\x00' + \
    '\x10\x00\x10\x03\x01\x11\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x16\x00\x01\x01' + \
    '\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x07\x06\x08\xff\xc4\x00' + \
    '\x15\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x05\x06' + \
    '\xff\xda\x00\x0c\x03\x01\x00\x02\x10\x03\x10\x00\x00\x01\xdf\xea\x1ctJ163\x04\x13' + \
    '\x14\x1f\xff\xc4\x00\x18\x10\x00\x03\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00' + \
    '\x00\x00\x00\x04\x05\x07\x03\x06\xff\xda\x00\x08\x01\x01\x00\x01\x05\x02\xd2\x82' + \
    '\xd0\xa1\xcf\xaf\xf4\xc8\xc6\xc7\x88\xa3`3I\x95]\xa8\x9f\xff\xc4\x00$\x11\x00\x02\x01' + \
    '\x02\x05\x04\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x11\x00\x05' + \
    '\x12\x13!\x14"#1\x062A\xff\xda\x00\x08\x01\x03\x01\x01?\x01\xac\xce2\xcc\xb6H\xd2' + \
    '\xbe\xa3l\xb8\xd6\x11VVr\x97\xd3{\xc7\x0c\xda\x01 \x80\xce\xb6$\x1b^\xc7\x1b\x90\xcd' + \
    '\xe5\xa6\xbfO/\x92\rR\tN\xd3\xf7Gy\x15"Y;H\xef\x11\xa0oaW\xd63\xbf\x8d\xaeqS\x15OVi' + \
    '\x99!\x102\xec\xef\x06E\x91\xe4R<\xb1\x15k\xc8\xc0\xfd\x81\x16\xe0[\x9ah\x16\x9a\x9e' + \
    '\nd$\xa5<1@\xa4\xfb+\x12,jM\xbfH^q\xff\xc4\x00$\x11\x00\x03\x01\x00\x01\x03\x04\x02' + \
    '\x03\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x11\x05\x12\x13\x06\x14!"#2\x00Aa' + \
    '\xff\xda\x00\x08\x01\x02\x01\x01?\x01\xc5\xd0z\xcfW\x85\xa9\xd2\xf3\nx\xcf\x8f\xcdF' + \
    '\x90\x92\xd7\xb40\x05k\xa7)\xaf\x00\x82\xc9:\x02\x03/%{\x87)-PQ\r\xc5\x1bd\x7f\x16' + \
    '\xa3(>i\x9d\x13\xfa\xdb\xb3=/\xa5\xe0\xbe@\xdcI\xf4]\x90}M\\\x8e\xe3\xe9\xff\x00U' + \
    '\xbfB\xc9l\x9e\xc5u%4\x1d*\xde\xe0\xc1\x91\xdas\x9b\x03\xf8l\x1dx\x92\x11\xfa\x90y' + \
    '\xf9<\xfck\xd0\xda\xf5i\xd6\xe0\x07\xd5\xa2\xda\x1c/\xea\x1a\xd4j0\x1c\xff\x00@\xb1' + \
    '\xe3\xfc\xfe\x7f\xff\xc4\x00!\x10\x00\x03\x01\x00\x01\x04\x02\x03\x00\x00\x00\x00' + \
    '\x00\x00\x00\x00\x02\x03\x04\x01\x05\x06\x12\x13\x14\x00\x15\x11$1\xff\xda\x00' + \
    '\x08\x01\x01\x00\x06?\x02\x9a\xfc\xe67\x8a]\xe1\x96&_^WvNg\xa5\x88Q\xfd\' \xc2\xec' + \
    '\x0f\xd5+)\xec\x1d\xa4Z\xd5\xce\xd0^\xa7\xe0\xbbK\x8c\xe4\xd1%tm\xe5t\xfa\xaeB\x84' + \
    '\xaae\xdd\xe9M\xf5\xde\x08\x03}-\xd6&\xf2^\xe3\xc9\x8a"\x99"\x1a\xa6\xa27\xf4}o\xde9>' + \
    '\x8a\x1f/1\xd2\xe4\x9a\x92\xb61\x98\xd1\xcay\xd9\x9c\xb1&4\xf4<\x8a\x16j\xf4|\x89Q' + \
    '\x8e\xe6\xd19tm\x08m7R\xec\xdd\xe6\xfaP\xa6R\x1b\xc5\xaf\x8a@\x99\x8fP\x13\x8b\xc6' + \
    '\x0b\xc78\x82m\xdf\xe8\xade\xbf\x8f\x9f\xff\xc4\x00\x18\x10\x01\x00\x03\x01\x00\x00' + \
    '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x10!\x11\xff\xda\x00\x08\x01\x01\x00' + \
    '\x01?!\x06k\xb5\xe7\xc16\xf5\xc1\xc2\x7f\xf8}\x15\xd7\x16\xc5\xc4\xa0\x86\x04|v\x7f6t\xd1' + \
    '\xe0F\xeb\xa5@qR?\xff\xda\x00\x0c\x03\x01\x00\x02\x00\x03\x00\x00\x00\x10\x92\x9f\xff' + \
    '\xc4\x00\x17\x11\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01' + \
    '\x11!\x00\xff\xda\x00\x08\x01\x03\x01\x01?\x10\x87k\xa5_\x15\x92dc\x16,\xa0\x89\xc8E\xc2' + \
    '\xd6\xbd)\x00\x06o\xdcb2X\xachO \xe1\'\xc9\x84\x10\x18\x02\xac\x03\xbf\xff\xc4\x00\x18' + \
    '\x11\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x11\x00!1\xff' + \
    '\xda\x00\x08\x01\x02\x01\x01?\x10)\xcb\xd0\xba\x14}\xf8\xe0\x9c\x155\xeb\x12\xbcLR\xce' + \
    '\x98t\xfaU\x97\xf4\x06C\xb5\x10m}q]zK-J\xc1[\xbf\xff\xc4\x00\x17\x10\x01\x01\x01\x01\x00' + \
    '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x11!\xff\xda\x00\x08\x01\x01\x00' + \
    '\x01?\x10a\xee+\xc3\xce]3d\xbc\x7f\x8d\xcbP\xa7Y\x9d\xe8\x12X\xd9\x92uddk\xc4\x9fj%' + \
    '\xda\xc5p\xb8\xff\xd9'

PROPAGANDA = None # PROPAGANDA = "http://goo.gl/K0tWH"

#
# Different ways to get exiv information:
#
# - pyexif -> calls 'exiftool'
# - pexif -> doesn't works with Nikon D3100
# - PIL -> detects only a minimal subset compared to 'exiftool'
#            exif = dict((ExifTags.TAGS.get(k, k), v) for (k, v) in src_image._getexif().items())
#            import pprint
#            pprint.pprint(exif)
# - pyexiv2 -> requires compilation of libraries and can't be installed using pip
#
# Resolution: stick with 'pyexif' or call 'exiftool' manually...
#


class ExifInfo(object):
    def __init__(self, filename, iso, aperture, shutter, camera):
        self.filename = filename
        self.iso = os.environ.get('ISO', iso)
        self.aperture = os.environ.get('APERTURE', aperture)
        self.shutter = os.environ.get('SHUTTER_SPEED', shutter)
        self.camera = os.environ.get('CAMERA', camera)


TRY4CAMERA = ('Model', 'Make',)
TRY4APERTURE = ('Aperture', 'FNumber',)
TRY4SHUTTER = ('ShutterSpeed', 'ExposureTime',)
TRY4ISO = ('ISO', 'ISOSetting', 'ISO2',)


def _try_on_dict(exif_dicts, key_list):
    for k in key_list:
        for a_dict in exif_dicts:
            if k in a_dict:
                return a_dict[k]
    return None


def _exiftool_get_json(filename):
    json_output = subprocess.check_output(['exiftool', '-j', filename])
    exif_data = json.loads(json_output)
    return exif_data


def _get_exif_info_exiftool(filename):
    exif_data = _exiftool_get_json(filename)
    return ExifInfo(filename,
        _try_on_dict(exif_data, TRY4ISO),
        _try_on_dict(exif_data, TRY4APERTURE),
        _try_on_dict(exif_data, TRY4SHUTTER),
        _try_on_dict(exif_data, TRY4CAMERA),
    )


def get_exif_info(filename):
    return _get_exif_info_exiftool(filename)


def copy_exif_info(src_filename, dst_filename):
    exif_tags = TRY4ISO + TRY4APERTURE + TRY4SHUTTER + TRY4CAMERA
    subprocess.check_output(
        (
            'exiftool',
            '-all=',
            '-tagsFromFile',
            src_filename,
        )
        +
        tuple("-exif:{0}".format(tag_name) for tag_name in exif_tags)
        +
        (
            dst_filename,
        )
    )


def do_garnish(src_filename, dst_filename, author=None, overwrite=False,
    font_file=None, font_size=None, output_quality=None, border_size=None, border_color=None,
    max_size=None, title=None, year=None, basic_info=None):
    """
    Process the pic and garnish it. Returns the 'exit status'.
    """

    # TODO: check input file is JPEG
    # TODO: check output file extension is JPEG

    assert author is not None
    assert font_file is not None
    assert font_size is not None
    assert output_quality is not None
    assert border_size is not None
    assert border_color is not None
    assert max_size is not None
    assert year is not None
    assert basic_info is not None

    THUMB_SIZE = (max_size[0] - (border_size * 4), max_size[1] - (border_size * 4))

    # TODO: enhance error message
    if not os.path.exists(src_filename):
        logger.error("The input file '%s' does not exists", src_filename)
        return 1

    if overwrite:
        if os.path.exists(dst_filename):
            logger.info("Will overwrite output file '%s'", dst_filename)
    else:
        if os.path.exists(dst_filename):
            logger.error("The output file '%s' already exists", dst_filename)
            return 1

    # Open the image
    try:
        src_image = Image.open(src_filename)
    except:
        logger.error("Couldn't load an image from file %s. Check if it's realy an image", src_filename)
        return 1

    # Get the exif info
    exif_info = get_exif_info(src_filename)

    # Create the thumb...
    src_image.thumbnail(THUMB_SIZE, Image.ANTIALIAS)

    # Add the border
    src_image = ImageOps.expand(src_image, border=border_size, fill='black')

    # Add the 2nd border
    src_image = ImageOps.expand(src_image, border=border_size, fill=border_color)

    # TODO: check math for non-default thumb size
    w = src_image.size[0]
    h = src_image.size[1] + 20 - border_size

    try:
        font = ImageFont.truetype(font_file, font_size)
    except:
        if os.path.exists(font_file):
            logger.error("Couldn't load font from file '%s'", font_file)
            return 1
        else:
            logger.error("The specified font file doens't exists: %s", font_file)
            return 1

    garnished = Image.new(src_image.mode, [w, h], ImageColor.getcolor('white', src_image.mode))
    garnished.paste(src_image, (0, 0))

    # TODO: check math for non-default thumb size
    from_left = 8
    from_top = src_image.size[1] + 3 - border_size

    pos = from_left

    draw = ImageDraw.Draw(garnished)

    if title:
        text = u"'{0}' ".format(title) # WITH trailing space!
        draw.text([pos, from_top], text,
            fill=ImageColor.getcolor('black', src_image.mode), font=font)
        text_width = draw.textsize(text, font=font)[0]
        pos = pos + text_width

    # Copyright
    text = u"©{0} {1} ".format(year, author) # WITH trailing space!
    draw.text([pos, from_top], text,
        fill=ImageColor.getcolor('black', src_image.mode), font=font)
    text_width = draw.textsize(text, font=font)[0]
    pos = pos + text_width

    if basic_info is False and (exif_info.camera or exif_info.iso or \
        exif_info.aperture or exif_info.shutter):

        # Paste camera icon
        pos = pos + 10
        camera_icon = Image.open(StringIO(CAMERA_ICON))
        camera_icon.load()
        garnished.paste(camera_icon, (pos, from_top - 2, ))
        pos = pos + camera_icon.size[0] + 2

        separator = ''

        if exif_info.camera:
            text = "{0}{1}".format(separator, exif_info.camera)
            draw.text([pos, from_top], text,
                fill=ImageColor.getcolor('black', src_image.mode), font=font)
            text_width = draw.textsize(text, font=font)[0]
            pos = pos + text_width
            separator = ' - '

        if exif_info.shutter:
            text = "{0}Exp {1}".format(separator, exif_info.shutter)
            draw.text([pos, from_top], text,
                fill=ImageColor.getcolor('black', src_image.mode), font=font)
            text_width = draw.textsize(text, font=font)[0]
            pos = pos + text_width
            separator = ' - '

        if exif_info.iso:
            text = "{0}ISO {1}".format(separator, exif_info.iso)
            draw.text([pos, from_top], text,
                fill=ImageColor.getcolor('black', src_image.mode), font=font)
            text_width = draw.textsize(text, font=font)[0]
            pos = pos + text_width
            separator = ' - '

        if exif_info.aperture:
            text = "{0}f/{1}".format(separator, exif_info.aperture)
            draw.text([pos, from_top], text,
                fill=ImageColor.getcolor('black', src_image.mode), font=font)
            text_width = draw.textsize(text, font=font)[0]
            pos = pos + text_width
            separator = ' - '

    if pos >= w:
        logger.warn("Text exceeded image width")
    else:
        if PROPAGANDA:
            text = PROPAGANDA
            text_width = draw.textsize(text, font=font)[0]
            if (pos + 20 + text_width) < w:
                # put at the right of the image
                draw.text([(w - text_width - 4), from_top], text,
                    fill=ImageColor.getcolor('#777', src_image.mode), font=font)

    del draw

    garnished.save(dst_filename, quality=output_quality, format='JPEG')

    copy_exif_info(src_filename, dst_filename)

    return 0


def _get_default_font():
    this_dir = os.path.dirname(os.path.abspath(__file__))
    default_font = os.path.join(this_dir, 'LiberationSans-Regular.ttf')
    assert os.path.exists(default_font)
    return default_font


if __name__ == '__main__':
    import argparse

    #===============================================================================
    # Some settings that are globlal could be setted with environment variables
    # (those that are the same for different pics)
    #===============================================================================

    GMP_AUTHOR = os.environ.get('GMP_AUTHOR', None)

    try:
        GMP_OUTPUT_QUALITY = int(os.environ['GMP_OUTPUT_QUALITY'])
    except KeyError:
        # TODO: log warn message
        GMP_OUTPUT_QUALITY = 95
    except ValueError:
        # TODO: log warn message
        GMP_OUTPUT_QUALITY = 95

    try:
        GMP_BORDER = int(os.environ['GMP_DEFAULT_BORDER'])
    except KeyError:
        # TODO: log warn message
        GMP_BORDER = 4
    except ValueError:
        # TODO: log warn message
        GMP_BORDER = 4

    try:
        GMP_FONT = os.environ['GMP_DEFAULT_FONT']
    except KeyError:
        # TODO: log warn message
        GMP_FONT = _get_default_font()
    except ValueError:
        # TODO: log warn message
        GMP_FONT = _get_default_font()

    try:
        GMP_FONT_SIZE = int(os.environ['GMP_DEFAULT_FONT_SIZE'])
    except KeyError:
        # TODO: log warn message
        GMP_FONT_SIZE = 12
    except ValueError:
        # TODO: log warn message
        GMP_FONT_SIZE = 12

    try:
        GMP_MAX_SIZE = int(os.environ['GMP_DEFAULT_MAX_SIZE'])
        GMP_MAX_SIZE = '{}x{}'.format(GMP_MAX_SIZE, GMP_MAX_SIZE)
    except KeyError:
        # TODO: log warn message
        GMP_MAX_SIZE = '800x800'
    except ValueError:
        # TODO: log warn message
        GMP_MAX_SIZE = '800x800'

    try:
        GMP_COLOR = os.environ['GMP_COLOR']
    except KeyError:
        # TODO: log warn message
        GMP_COLOR = '#545454'
        GMP_COLOR = '#eee'

    parser = argparse.ArgumentParser()
    parser.add_argument("src_file", help="Path to the original photography")
    parser.add_argument("dst_file", help="Path where to create the thumbnail")
    parser.add_argument("--author", help="Author information (this script also checks "
        "for the GMP_AUTHOR environment variable", default=GMP_AUTHOR)
    parser.add_argument("--title", help="Title of the pic")
    parser.add_argument("--year", help="Year to use on copyright (defaults to current year)",
        default=datetime.date.today().year)
    parser.add_argument("--overwrite", help="Overwrite dst_file if exists",
        action='store_true')
    parser.add_argument("--output-quality", help="Quality of generated JPG (1-100)",
        type=int, default=GMP_OUTPUT_QUALITY)
    parser.add_argument("--border-size", help="Border size in pixels",
        type=int, default=GMP_BORDER)
    parser.add_argument("--border-color", help="Border color",
        default=GMP_COLOR)
    parser.add_argument("--font", help="Path to the TrueType font to use",
        default=GMP_FONT)
    parser.add_argument("--font-size", help="Size of text",
        type=int, default=GMP_FONT_SIZE)
    parser.add_argument("--max-size", help="Max size of output image",
        default=GMP_MAX_SIZE)
    parser.add_argument("--basic-info", help="Doesn't include technical info (iso, F, exposure)",
        action='store_true')
    args = parser.parse_args()

    if not args.author:
        parser.error("You must specify 'GMP_AUTHOR' environment variable, "
            "or the --author argument")

    # TODO: check proper conversion of these int()s and show error message on error
    try:
        max_size = [int(size) for size in args.max_size.split('x')]
    except KeyError:
        parser.error("Wrong --max-size: must specify in the form WIDTHxHEIGHT (ej: 800x800)")
    except ValueError:
        parser.error("Wrong --max-size: must specify in the form WIDTHxHEIGHT (ej: 800x800)")

    if len(max_size) != 2:
        parser.error("Wrong --max-size: must specify in the form WIDTHxHEIGHT (ej: 800x800)")

    exit_status = do_garnish(args.src_file, args.dst_file,
        author=args.author,
        overwrite=args.overwrite,
        font_file=args.font,
        font_size=args.font_size,
        output_quality=args.output_quality,
        border_size=args.border_size,
        border_color=args.border_color,
        max_size=max_size,
        title=args.title,
        year=args.year,
        basic_info=args.basic_info
    )

    sys.exit(exit_status)
