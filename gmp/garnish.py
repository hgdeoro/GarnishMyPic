# -*- coding: utf-8 -*-

'''
Created on Jan 14, 2013

@author: Horacio G. de Oro
'''

import datetime
import os
import sys

import pyexif

from PIL import Image, ImageColor, ImageDraw, ImageFont

FONT = os.environ.get('FONT', '/usr/share/fonts/truetype/droid/DroidSans-Bold.ttf')
FONT_SIZE = int(os.environ.get('FONT_SIZE', '12'))
SIZE = (800, 800,)
OVERWRITE = os.environ.get('OVERWRITE', None)
OUTPUT_QUALITY = int(os.environ.get('OUTPUT_QUALITY', '95'))


def main():
    src_filename = sys.argv[1]
    dst_filename = sys.argv[2]

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
    src_image.thumbnail(SIZE, Image.ANTIALIAS)
    w = src_image.size[0]
    h = src_image.size[1] + 18

    font = ImageFont.truetype(FONT, FONT_SIZE)

    garnished = Image.new(src_image.mode, [w, h], ImageColor.getcolor('white', src_image.mode))
    garnished.paste(src_image, (0, 0))

    from_left = 10
    from_top = src_image.size[1] + 1
    draw = ImageDraw.Draw(garnished)
    text = u"'{title}' - ©{year} {author} - ISO: {iso} - Aperture: F/{aperture} - Shutter speed: {shutter}".format(
        title=title, year=year, author=author, iso=iso, aperture=aperture, shutter=shutter)
    draw.text([from_left, from_top], text, fill=ImageColor.getcolor('black', src_image.mode), font=font)

    garnished.save(dst_filename, quality=OUTPUT_QUALITY)


if __name__ == '__main__':
        main()
