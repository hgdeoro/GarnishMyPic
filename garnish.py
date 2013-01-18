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

from PIL import Image, ImageColor, ImageDraw, ImageFont, ImageOps

# TODO: use system font or add font file - check license!

logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
logger = logging.getLogger('GarnishMyPic')

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
    font_file=None, font_size=None, output_quality=None, border_size=None,
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

    # Create the thumb and add the border
    src_image.thumbnail(THUMB_SIZE, Image.ANTIALIAS)
    src_image = ImageOps.expand(src_image, border=border_size, fill='black')
    src_image = ImageOps.expand(src_image, border=border_size, fill='white')

    # TODO: check math for non-default thumb size
    w = src_image.size[0]
    h = src_image.size[1] + 18 - border_size

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
    from_left = 6
    from_top = src_image.size[1] + 1 - border_size

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

    if basic_info is False:
        if exif_info.camera:
            text = "- Camera: {0} ".format(exif_info.camera)
            draw.text([pos, from_top], text,
                fill=ImageColor.getcolor('black', src_image.mode), font=font)
            text_width = draw.textsize(text, font=font)[0]
            pos = pos + text_width
    
        if exif_info.iso:
            text = "- ISO: {0} ".format(exif_info.iso)
            draw.text([pos, from_top], text,
                fill=ImageColor.getcolor('black', src_image.mode), font=font)
            text_width = draw.textsize(text, font=font)[0]
            pos = pos + text_width
    
        if exif_info.aperture:
            text = "- Aperture: F/{0} ".format(exif_info.aperture)
            draw.text([pos, from_top], text,
                fill=ImageColor.getcolor('black', src_image.mode), font=font)
            text_width = draw.textsize(text, font=font)[0]
            pos = pos + text_width
    
        if exif_info.shutter:
            text = "- Shutter speed: {0} ".format(exif_info.shutter)
            draw.text([pos, from_top], text,
                fill=ImageColor.getcolor('black', src_image.mode), font=font)
            text_width = draw.textsize(text, font=font)[0]
            pos = pos + text_width

    del draw

    garnished.save(dst_filename, quality=output_quality, format='JPEG')

    if pos >= w:
        logger.warn("Image was saved OK, but text exceeded image width")

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
        GMP_FONT = int(os.environ['GMP_DEFAULT_FONT'])
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
    except KeyError:
        # TODO: log warn message
        GMP_MAX_SIZE = '800x800'
    except ValueError:
        # TODO: log warn message
        GMP_MAX_SIZE = '800x800'

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
        max_size=max_size,
        title=args.title,
        year=args.year,
        basic_info=args.basic_info
    )

    sys.exit(exit_status)
