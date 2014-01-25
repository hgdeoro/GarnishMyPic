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
from gmp.utils import GMP_AUTHOR,\
    GMP_EXIF_COPYRIGHT, GMP_TITLE_IMAGE, GMP_TITLE, GMP_OUTPUT_QUALITY,\
    GMP_BORDER, GMP_COLOR, GMP_FONT, GMP_DEFAULT_FONT_SIZE, GMP_DEFAULT_MAX_SIZE,\
    GMP_OUTPUT_DIR


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

    parser = argparse.ArgumentParser()
    parser.add_argument("input_files", help="Input files to process", nargs="+")
    parser.add_argument("--output-dir", "-d", help="Output directory",
        default=GMP_OUTPUT_DIR)
    parser.add_argument("--author", help="Author information",
        default=GMP_AUTHOR)
    parser.add_argument("--exif-copyright", help="Information to set as 'copyright' exif tag",
        default=GMP_EXIF_COPYRIGHT)
    parser.add_argument("--title", help="Title of the pic",
        default=GMP_TITLE)
    parser.add_argument("--title-img", help="Image to use for title at the bottom",
        default=GMP_TITLE_IMAGE)
    parser.add_argument("--year", help="Year to use on copyright (defaults to current year)",
        default=datetime.date.today().year)
    parser.add_argument("--overwrite", "-o", help="Overwrite dst_file if exists",
        action='store_true')
    parser.add_argument("--output-quality", "-q", help="Quality of generated JPG (1-100)",
        type=int, default=GMP_OUTPUT_QUALITY)
    parser.add_argument("--border-size", help="Border size in pixels",
        type=int, default=GMP_BORDER)
    parser.add_argument("--border-color", help="Border color", default=GMP_COLOR)
    parser.add_argument("--font", help="Path to the TrueType font to use", default=GMP_FONT)
    parser.add_argument("--font-size", help="Size of text", type=int,
        default=GMP_DEFAULT_FONT_SIZE)
    parser.add_argument("--max-size", help="Max size of output image",
        default=GMP_DEFAULT_MAX_SIZE)
    parser.add_argument("--technical-info", "-i", help="Include technical info (iso, F, exposure)",
        action='store_true')
    args = parser.parse_args()

    # TODO: check proper conversion of these int()s and show error message on error
    
    #===========================================================================
    # Check image size
    #===========================================================================
    try:
        max_size = [int(size) for size in args.max_size.split('x')]
    except KeyError:
        parser.error("Wrong --max-size: must specify in the form WIDTHxHEIGHT (ej: 800x800)")
    except ValueError:
        parser.error("Wrong --max-size: must specify in the form WIDTHxHEIGHT (ej: 800x800)")

    if len(max_size) != 2:
        parser.error("Wrong --max-size: must specify in the form WIDTHxHEIGHT (ej: 800x800)")

    for input_file in args.input_files:
        exit_status = do_garnish(input_file, args.output_dir,
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
            technical_info=args.technical_info,
            exif_copyright=args.exif_copyright
        )

    sys.exit(exit_status)
