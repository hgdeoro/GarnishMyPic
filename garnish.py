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

from StringIO import StringIO
import datetime
import logging
import os
import sys

from PIL import Image, ImageColor, ImageDraw, ImageFont, ImageOps

from gmp.exif import get_exif_info, copy_exif_info
from gmp.resources import CAMERA_ICON
from gmp.utils import get_default_font


# TODO: use system font or add font file - check license!
logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
logger = logging.getLogger('GarnishMyPic')

PROPAGANDA = None  # PROPAGANDA = "http://goo.gl/K0tWH"

#===============================================================================
# Hardcoded stuff... some day passed as parameter
#===============================================================================
# BORDER_SIZE_BOTTOM should be "title img" + some margin
BORDER_SIZE_BOTTOM = 20
BORDER_SIZE_BOTTOM_MARGIN = 5

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


def do_garnish(src_filename, dst_filename, author,
    font_file, font_size, output_quality, border_size, border_size_bottom, border_color,
    max_size, year, basic_info, title=None,
    title_img=None, overwrite=False):
    """
    Process the pic and garnish it. Returns the 'exit status'.
    """

    # TODO: check input file is JPEG
    # TODO: check output file extension is JPEG

    #===========================================================================
    # Check if src/dst exists
    # TODO: enhance error message
    #===========================================================================
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

    #===========================================================================
    # Get exif
    #===========================================================================
    exif_info = get_exif_info(src_filename)

    #===========================================================================
    # Open things: src image, title image, font
    #===========================================================================
    try:
        src_image = Image.open(src_filename)
    except:
        logger.error("Couldn't load an image from file %s. Check if it's realy an image",
            src_filename)
        return 1

    # Open the 'title image'
    if title_img:
        try:
            title_img_image = Image.open(title_img)
        except:
            logger.error("Couldn't load an image from file %s. Check if it's realy an image",
                title_img)
            return 1
    else:
        title_img_image = None

    # Font
    try:
        font = ImageFont.truetype(font_file, font_size)
    except:
        if os.path.exists(font_file):
            logger.error("Couldn't load font from file '%s'", font_file)
            return 1
        else:
            logger.error("The specified font file doens't exists: %s", font_file)
            return 1

    #===========================================================================
    # Create the thumb and a copy to work on
    #===========================================================================
    src_image.thumbnail(max_size, Image.ANTIALIAS)

    garnished = Image.new(src_image.mode, src_image.size,
        ImageColor.getcolor('white', src_image.mode))
    garnished.paste(src_image, (0, 0))

    #===========================================================================
    # Add the border -> left, top, right, bottom
    #===========================================================================
    real_border_size = (border_size, border_size, border_size, border_size + border_size_bottom)
    garnished = ImageOps.expand(garnished, border=real_border_size, fill=border_color)

    # TODO: check math for non-default thumb size
    from_left = 8
    from_top = garnished.size[1] - border_size - border_size_bottom + BORDER_SIZE_BOTTOM_MARGIN

    # pos start with "from_left", and is incremented while we add contents (img, text)
    pos = from_left

    draw = ImageDraw.Draw(garnished)

    if title:
        text = u"'{0}' ".format(title)  # WITH trailing space!
        draw.text([pos, from_top], text,
            fill=ImageColor.getcolor('black', garnished.mode), font=font)
        text_width = draw.textsize(text, font=font)[0]
        pos = pos + text_width
    elif title_img_image:
        # paste(img, pos, mask) // mask -> transparency
        garnished.paste(title_img_image, (pos, from_top - 0,), title_img_image)
        pos = pos + title_img_image.size[0] + 4

    #    # Copyright
    #    text = u"©{0} {1} ".format(year, author)  # WITH trailing space!
    #    draw.text([pos, from_top], text,
    #        fill=ImageColor.getcolor('black', garnished.mode), font=font)
    #    text_width = draw.textsize(text, font=font)[0]
    #    pos = pos + text_width

    if basic_info is False and (exif_info.camera or exif_info.iso or \
        exif_info.aperture or exif_info.shutter):

        # Paste camera icon
        pos = pos + 10
        camera_icon = Image.open(StringIO(CAMERA_ICON))
        camera_icon.load()
        garnished.paste(camera_icon, (pos, from_top - 2,))
        pos = pos + camera_icon.size[0] + 2

        separator = ''

        if exif_info.camera:
            text = "{0}{1}".format(separator, exif_info.camera)
            draw.text([pos, from_top], text,
                fill=ImageColor.getcolor('black', garnished.mode), font=font)
            text_width = draw.textsize(text, font=font)[0]
            pos = pos + text_width
            separator = ' - '

        if exif_info.shutter:
            text = "{0}Exp {1}".format(separator, exif_info.shutter)
            draw.text([pos, from_top], text,
                fill=ImageColor.getcolor('black', garnished.mode), font=font)
            text_width = draw.textsize(text, font=font)[0]
            pos = pos + text_width
            separator = ' - '

        if exif_info.iso:
            text = "{0}ISO {1}".format(separator, exif_info.iso)
            draw.text([pos, from_top], text,
                fill=ImageColor.getcolor('black', garnished.mode), font=font)
            text_width = draw.textsize(text, font=font)[0]
            pos = pos + text_width
            separator = ' - '

        if exif_info.aperture:
            text = "{0}f/{1}".format(separator, exif_info.aperture)
            draw.text([pos, from_top], text,
                fill=ImageColor.getcolor('black', garnished.mode), font=font)
            text_width = draw.textsize(text, font=font)[0]
            pos = pos + text_width
            separator = ' - '

    if pos >= garnished.size[1]:
        logger.warn("Text exceeded image width")
    #    else:
    #        if PROPAGANDA:
    #            text = PROPAGANDA
    #            text_width = draw.textsize(text, font=font)[0]
    #            if (pos + 20 + text_width) < w:
    #                # put at the right of the image
    #                draw.text([(w - text_width - 4), from_top], text,
    #                    fill=ImageColor.getcolor('#777', garnished.mode), font=font)

    del draw

    garnished.save(dst_filename, quality=output_quality, format='JPEG')

    copy_exif_info(src_filename, dst_filename)

    return 0


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
        GMP_OUTPUT_QUALITY = 97
    except ValueError:
        # TODO: log warn message
        GMP_OUTPUT_QUALITY = 97

    try:
        GMP_BORDER = int(os.environ['GMP_DEFAULT_BORDER'])
    except KeyError:
        # TODO: log warn message
        GMP_BORDER = 10
    except ValueError:
        # TODO: log warn message
        GMP_BORDER = 10

    try:
        GMP_FONT = os.environ['GMP_DEFAULT_FONT']
    except KeyError:
        # TODO: log warn message
        GMP_FONT = get_default_font()
    except ValueError:
        # TODO: log warn message
        GMP_FONT = get_default_font()

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

    parser = argparse.ArgumentParser()
    parser.add_argument("src_file", help="Path to the original photography")
    parser.add_argument("dst_file", help="Path where to create the thumbnail")
    parser.add_argument("--author", help="Author information (this script also checks "
        "for the GMP_AUTHOR environment variable", default=GMP_AUTHOR)
    parser.add_argument("--title", help="Title of the pic")
    parser.add_argument("--title-img", help="Image to use for title at the bottom")
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
        border_size_bottom=BORDER_SIZE_BOTTOM,
        max_size=max_size,
        title=args.title,
        title_img=args.title_img,
        year=args.year,
        basic_info=args.basic_info
    )

    sys.exit(exit_status)
