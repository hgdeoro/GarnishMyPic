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

FONT = os.environ.get('FONT', '/usr/share/fonts/truetype/droid/DroidSans-Bold.ttf')
FONT_SIZE = int(os.environ.get('FONT_SIZE', '12'))
SIZE = (800, 800,)
OVERWRITE = os.environ.get('OVERWRITE', None)
OUTPUT_QUALITY = int(os.environ.get('OUTPUT_QUALITY', '95'))
BORDER = int(os.environ.get('BORDER', '4'))


def main():
    src_filename = sys.argv[1]
    dst_filename = sys.argv[2]

    THUMB_SIZE = (SIZE[0] - (BORDER * 4), SIZE[1] - (BORDER * 4))

    assert os.path.exists(src_filename), \
        "The input file '{0}' does not exists".format(src_filename)
    if OVERWRITE is None:
        assert not os.path.exists(dst_filename), \
            "The output file '{0}' already exists".format(dst_filename)

    title = os.environ.get('TITLE', '?')
    author = os.environ.get('AUTHOR', '?')
    year = os.environ.get('YEAR', datetime.date.today().year)

    editor = pyexif.ExifEditor(src_filename)
    shutter = editor.getTag('ShutterSpeed')
    iso = editor.getTag('ISOSetting')
    aperture = editor.getTag('Aperture')

    src_image = Image.open(src_filename)
    src_image.thumbnail(THUMB_SIZE, Image.ANTIALIAS)

    src_image = ImageOps.expand(src_image, border=4, fill='black')
    src_image = ImageOps.expand(src_image, border=4, fill='white')

    w = src_image.size[0]
    h = src_image.size[1] + 18 - BORDER

    font = ImageFont.truetype(FONT, FONT_SIZE)

    garnished = Image.new(src_image.mode, [w, h], ImageColor.getcolor('white', src_image.mode))
    garnished.paste(src_image, (0, 0))

    from_left = 10
    from_top = src_image.size[1] + 1 - BORDER
    draw = ImageDraw.Draw(garnished)
    text = u"'{title}' ©{year} {author} - ISO: {iso} - Aperture: F/{aperture} - Shutter speed: {shutter}".format(
        title=title, year=year, author=author, iso=iso, aperture=aperture, shutter=shutter)
    draw.text([from_left, from_top], text, fill=ImageColor.getcolor('black', src_image.mode), font=font)

    garnished.save(dst_filename, quality=OUTPUT_QUALITY)

    editor = pyexif.ExifEditor(dst_filename)
    #    shutter = editor.getTag('ShutterSpeed')
    #    iso = editor.getTag('ISOSetting')
    #    aperture = editor.getTag('Aperture')
    editor.setTag('ShutterSpeed', shutter)
    editor.setTag('ISOSetting', iso)
    editor.setTag('Aperture', aperture)


if __name__ == '__main__':
        main()
