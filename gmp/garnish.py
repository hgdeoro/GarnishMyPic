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
FONT_SIZE = int(os.environ.get('FONT_SIZE', '14'))


def main():
    title = os.environ.get('TITLE', '?')
    author = os.environ.get('AUTHOR', '?')
    year = os.environ.get('YEAR', datetime.date.today().year)

    editor = pyexif.ExifEditor(sys.argv[1])
    shutter = editor.getTag('ShutterSpeed')
    iso = editor.getTag('ISOSetting')
    aperture = editor.getTag('Aperture')

    src_image = Image.open(sys.argv[1])
    w = src_image.size[0]
    h = src_image.size[1] + 100

    font = ImageFont.truetype(FONT, FONT_SIZE)

    garnished = Image.new(src_image.mode, [w, h], ImageColor.getcolor('white', src_image.mode))
    garnished.paste(src_image, (0, 0))

    from_left = 10
    from_top = src_image.size[1] + 5
    draw = ImageDraw.Draw(garnished)
    text = u"'{title}' - ©{year} {author} - ISO: {iso} - Aperture: F/{aperture} - Shutter speed: {shutter}".format(
        title=title, year=year, author=author, iso=iso, aperture=aperture, shutter=shutter)
    draw.text([from_left, from_top], text, fill=ImageColor.getcolor('black', src_image.mode), font=font)

    garnished.save(sys.argv[2])


if __name__ == '__main__':
        main()
