# -*- coding: utf-8 -*-

'''
Created on Jan 14, 2013

@author: Horacio G. de Oro
'''

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

# Defaults
DEFAULT_FONT = '/usr/share/fonts/truetype/droid/DroidSans-Bold.ttf'
DEFAULT_FONT_SIZE = 12
DEFAULT_OUTPUT_QUALITY = int(os.environ.get('OUTPUT_QUALITY', '95'))
DEFAULT_BORDER = int(os.environ.get('BORDER', '4'))
DEFAULT_MAX_SIZE = (800, 800,)

#
# How to get exiv information:
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


def _get_exif_info_pyexif(filename):
    import pyexif #@UnresolvedImport
    editor = pyexif.ExifEditor(filename)
    # TODO: check if this tags works with different cameras
    return ExifInfo(filename, editor.getTag('ISOSetting'), editor.getTag('Aperture'),
        editor.getTag('ShutterSpeed'), None)


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
    font_file=DEFAULT_FONT, font_size=DEFAULT_FONT_SIZE,
    output_quality=DEFAULT_OUTPUT_QUALITY, border_size=DEFAULT_BORDER,
    max_size=DEFAULT_MAX_SIZE, title=None, year=None):
    # TODO: check input file is JPEG
    # TODO: check output file extension is JPEG

    assert author is not None
    assert year is not None

    THUMB_SIZE = (max_size[0] - (border_size * 4), max_size[1] - (border_size * 4))

    # TODO: enhance error message
    if not os.path.exists(src_filename):
        logger.error("The input file '%s' does not exists", src_filename)
        sys.exit(1)

    if overwrite:
        if os.path.exists(dst_filename):
            logger.info("Will overwrite output file '%s'", dst_filename)
    else:
        if os.path.exists(dst_filename):
            logger.error("The output file '%s' already exists", dst_filename)
            sys.exit(1)

    exif_info = get_exif_info(src_filename)

    src_image = Image.open(src_filename)
    src_image.thumbnail(THUMB_SIZE, Image.ANTIALIAS)

    src_image = ImageOps.expand(src_image, border=border_size, fill='black')
    src_image = ImageOps.expand(src_image, border=border_size, fill='white')

    # TODO: check math for non-default thumb size
    w = src_image.size[0]
    h = src_image.size[1] + 18 - border_size

    font = ImageFont.truetype(font_file, font_size)

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

    #    tmp = StringIO()
    #    garnished.save(tmp, quality=OUTPUT_QUALITY, format='JPEG')
    #
    #    output = pexif.JpegFile.fromString(tmp.getvalue(), 'rw')
    #    # T-O-D-O: this DOESN'T WORK!
    #    output.exif.primary.ShutterSpeed = str(shutter)
    #    output.exif.primary.ISOSetting = str(iso)
    #    output.exif.primary.Aperture = str(aperture)
    #    output.writeFile(dst_filename)

if __name__ == '__main__':
    import argparse

    GMP_AUTHOR = os.environ.get('GMP_AUTHOR', None)

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
        type=int, default=DEFAULT_OUTPUT_QUALITY)
    parser.add_argument("--border-size", help="Border size in pixels",
        type=int, default=DEFAULT_BORDER)
    parser.add_argument("--font", help="Path to the TrueType font to use",
        default=DEFAULT_FONT)
    parser.add_argument("--font-size", help="Size of text",
        type=int, default=DEFAULT_FONT_SIZE)
    parser.add_argument("--max-size", help="Max size of output image")
    args = parser.parse_args()

    if not args.author:
        parser.error("You must specify 'GMP_AUTHOR' environment variable, "
            "or the --author argument")

    # TODO: check proper conversion of these int()s and show error message on error
    if args.max_size is not None:
        max_size = [int(size) for size in args.max_size.split('x')]
        if len(max_size) != 2:
            parser.error("Wrong --max-size: must specify in the form WIDTHxHEIGHT")
    else:
        max_size = DEFAULT_MAX_SIZE

    do_garnish(args.src_file, args.dst_file,
        author=args.author,
        overwrite=args.overwrite,
        font_file=args.font,
        font_size=args.font_size,
        output_quality=args.output_quality,
        border_size=args.border_size,
        max_size=max_size,
        title=args.title,
        year=args.year,
    )
