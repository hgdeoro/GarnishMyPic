# -*- coding: utf-8 -*-

'''
Created on Jan 14, 2013

@author: Horacio G. de Oro
'''

import datetime
import os
import sys

import pyexif

from PIL import Image, ImageColor, ImageDraw, ImageFont, ImageOps

# TODO: get parameters/config from arguments

# TODO: use system font or add font file - check license!
FONT = os.environ.get('FONT', '/usr/share/fonts/truetype/droid/DroidSans-Bold.ttf')
FONT_SIZE = int(os.environ.get('FONT_SIZE', '12'))
SIZE = (800, 800,)
OVERWRITE = os.environ.get('OVERWRITE', None)
OUTPUT_QUALITY = int(os.environ.get('OUTPUT_QUALITY', '95'))
BORDER = int(os.environ.get('BORDER', '4'))

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


def main():
    # TODO: check input file is JPEG
    # TODO: check output file extension is JPEG
    src_filename = sys.argv[1]
    dst_filename = sys.argv[2]

    THUMB_SIZE = (SIZE[0] - (BORDER * 4), SIZE[1] - (BORDER * 4))

    # TODO: enhance error message
    assert os.path.exists(src_filename), \
        "The input file '{0}' does not exists".format(src_filename)
    if OVERWRITE is None:
        # TODO: enhance error message
        assert not os.path.exists(dst_filename), \
            "The output file '{0}' already exists".format(dst_filename)

    try:
        author = os.environ['AUTHOR']
    except KeyError:
        raise(Exception("You must specify 'AUTHOR' environment variable"))
    title = os.environ.get('TITLE', None)
    year = os.environ.get('YEAR', datetime.date.today().year)

    editor = pyexif.ExifEditor(src_filename)

    # TODO: check if this tags works with different cameras
    shutter = editor.getTag('ShutterSpeed')
    iso = editor.getTag('ISOSetting')
    aperture = editor.getTag('Aperture')

    src_image = Image.open(src_filename)
    src_image.thumbnail(THUMB_SIZE, Image.ANTIALIAS)

    src_image = ImageOps.expand(src_image, border=4, fill='black')
    src_image = ImageOps.expand(src_image, border=4, fill='white')

    # TODO: check math for non-default thumb size
    w = src_image.size[0]
    h = src_image.size[1] + 18 - BORDER

    font = ImageFont.truetype(FONT, FONT_SIZE)

    garnished = Image.new(src_image.mode, [w, h], ImageColor.getcolor('white', src_image.mode))
    garnished.paste(src_image, (0, 0))

    # TODO: check math for non-default thumb size
    from_left = 10
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

    if iso:
        text = "- ISO: {0} ".format(iso)
        draw.text([pos, from_top], text,
            fill=ImageColor.getcolor('black', src_image.mode), font=font)
        text_width = draw.textsize(text, font=font)[0]
        pos = pos + text_width

    if aperture:
        text = "- Aperture: F/{0} ".format(aperture)
        draw.text([pos, from_top], text,
            fill=ImageColor.getcolor('black', src_image.mode), font=font)
        text_width = draw.textsize(text, font=font)[0]
        pos = pos + text_width

    if shutter:
        text = "- Shutter speed: {0} ".format(shutter)
        draw.text([pos, from_top], text,
            fill=ImageColor.getcolor('black', src_image.mode), font=font)
        text_width = draw.textsize(text, font=font)[0]
        pos = pos + text_width

    del draw

    garnished.save(dst_filename, quality=OUTPUT_QUALITY, format='JPEG')

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
        main()
