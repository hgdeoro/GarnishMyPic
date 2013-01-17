# -*- coding: utf-8 -*-

'''
Created on Jan 14, 2013

@author: Horacio G. de Oro
'''

import datetime
import json
import os
import subprocess

from PIL import Image, ImageColor, ImageDraw, ImageFont, ImageOps


# TODO: remove all these env. variables and use program arguments
# TODO: use system font or add font file - check license!
SIZE = (800, 800,)
OUTPUT_QUALITY = int(os.environ.get('OUTPUT_QUALITY', '95'))
BORDER = int(os.environ.get('BORDER', '4'))

# Defaults
DEFAULT_FONT = '/usr/share/fonts/truetype/droid/DroidSans-Bold.ttf'
DEFAULT_FONT_SIZE = 12

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


def do_garnish(src_filename, dst_filename, author=None, overwrite=False, font_file=None, font_size=None):
    # TODO: check input file is JPEG
    # TODO: check output file extension is JPEG

    THUMB_SIZE = (SIZE[0] - (BORDER * 4), SIZE[1] - (BORDER * 4))

    # TODO: enhance error message
    assert os.path.exists(src_filename), \
        "The input file '{0}' does not exists".format(src_filename)
    if not overwrite:
        # TODO: enhance error message
        assert not os.path.exists(dst_filename), \
            "The output file '{0}' already exists".format(dst_filename)

    title = os.environ.get('TITLE', None)
    year = os.environ.get('YEAR', datetime.date.today().year)

    exif_info = get_exif_info(src_filename)

    src_image = Image.open(src_filename)
    src_image.thumbnail(THUMB_SIZE, Image.ANTIALIAS)

    src_image = ImageOps.expand(src_image, border=4, fill='black')
    src_image = ImageOps.expand(src_image, border=4, fill='white')

    # TODO: check math for non-default thumb size
    w = src_image.size[0]
    h = src_image.size[1] + 18 - BORDER

    font = ImageFont.truetype(font_file or DEFAULT_FONT, font_size or DEFAULT_FONT_SIZE)

    garnished = Image.new(src_image.mode, [w, h], ImageColor.getcolor('white', src_image.mode))
    garnished.paste(src_image, (0, 0))

    # TODO: check math for non-default thumb size
    from_left = 6
    from_top = src_image.size[1] + 1 - BORDER

    pos = from_left

    draw = ImageDraw.Draw(garnished)

    #    text = u"'{title}' ©{year} {author} - ISO: {iso} - Aperture: F/{aperture} - Shutter speed: {shutter}".format(
    #        title=title, year=year, author=author, iso=iso, aperture=aperture, shutter=shutter)
    #    draw.text([from_left, from_top], text, fill=ImageColor.getcolor('black', src_image.mode), font=font)

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

    garnished.save(dst_filename, quality=OUTPUT_QUALITY, format='JPEG')

    if pos >= w:
        raise(Exception("Image was saved OK, but text exceeded image width."))

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
    parser = argparse.ArgumentParser()
    parser.add_argument("src_file", help="Path to the original photography")
    parser.add_argument("dst_file", help="Path where to create the thumbnail")
    parser.add_argument("--author", help="Author information")
    parser.add_argument("--font", help="Path to the TrueType font to use",
        default=DEFAULT_FONT)
    parser.add_argument("--font-size", help="Size of text",
        type=int, default=DEFAULT_FONT_SIZE)
    parser.add_argument("--overwrite", help="Overwrite dst_file if exists",
        action='store_true')
    args = parser.parse_args()

    if not args.author and not os.environ.get('GMP_AUTHOR'):
        parser.error("You must specify 'GMP_AUTHOR' environment variable, "
            "or the --author argument")

    do_garnish(args.src_file, args.dst_file,
        author=args.author,
        overwrite=args.overwrite,
        font_file=args.font,
        font_size=args.font_size)
