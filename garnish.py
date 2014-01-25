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

#
# TODO: add "copyright" exif
#

import datetime
import logging
import os
import sys

from gmp.garnisher import do_garnish, BORDER_SIZE_BOTTOM
from gmp.utils import get_default_font


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
