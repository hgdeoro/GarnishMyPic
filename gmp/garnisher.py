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

import logging
import os

from PIL import Image, ImageColor, ImageDraw, ImageFont, ImageOps
from gmp.exif import get_exif_info, copy_exif_info
from gmp.utils import get_camera_image


#===============================================================================
# Hardcoded stuff... some day passed as parameter
#===============================================================================
# BORDER_SIZE_BOTTOM should be "title img" + some margin
BORDER_SIZE_BOTTOM = 20
BORDER_SIZE_BOTTOM_MARGIN = 5
FONT_COLOR = '#ccc'
CAPITALIZE = True

PROPAGANDA = None  # PROPAGANDA = "http://goo.gl/K0tWH"

logger = logging.getLogger('GarnishMyPic')


def do_garnish(input_file, output_dir, author,
    font_file, font_size, output_quality, border_size, border_size_bottom, border_color,
    max_size, year, technical_info, exif_copyright,
    title=None, title_img=None, overwrite=False):
    """
    Process the pic and garnish it. Returns the 'exit status'.
    """

    # TODO: check input file is JPEG
    # TODO: check output file extension is JPEG

    #===========================================================================
    # Clean & check input file
    #===========================================================================
    input_filename_full_path = os.path.normpath(os.path.abspath(input_file))

    if not os.path.exists(input_filename_full_path):
        raise Exception("The input file '%s' does not exists", input_filename_full_path)

    #===========================================================================
    # Create outpu dir if doesn't exists'
    #===========================================================================

    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    #===========================================================================
    # Build output file
    #===========================================================================
    input_basename = os.path.basename(input_filename_full_path)
    fn_root, fn_ext = os.path.splitext(input_basename)
    output_basename = "{}_garnish{}".format(fn_root, fn_ext)
    output_file = os.path.join(output_dir, output_basename)

    dst_filename = output_file
    src_filename = input_file

    #===========================================================================
    # Check if src/dst exists
    # TODO: enhance error message
    #===========================================================================

    if overwrite:
        if os.path.exists(dst_filename):
            logger.info("Will overwrite output file '%s'", dst_filename)
    else:
        if os.path.exists(dst_filename):
            raise Exception("The output file '%s' already exists", dst_filename)

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

    # Camera icon
    camera_image = get_camera_image((font_size + 2, font_size + 2,))

    def rtl(text, rpos, draw):
        text_width = draw.textsize(text, font=font)[0]
        draw.text([rpos - text_width, from_top], text, fill=font_color, font=font)
        return rpos - text_width

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

    #===========================================================================
    # Start writing at the bottom
    #===========================================================================
    # TODO: check math for non-default thumb size
    from_left = border_size
    from_right = garnished.size[0] - border_size
    from_top = garnished.size[1] - border_size - border_size_bottom + BORDER_SIZE_BOTTOM_MARGIN
    # pos start with "from_left", and is incremented while we add contents (img, text)

    pos = from_left
    pos_r = from_right

    draw = ImageDraw.Draw(garnished)

    font_color = ImageColor.getcolor(FONT_COLOR, garnished.mode)

    if title:
        text = u"'{0}' ".format(title)  # WITH trailing space!
        draw.text([pos, from_top], text,
            fill=font_color, font=font)
        text_width = draw.textsize(text, font=font)[0]
        pos = pos + text_width

    elif title_img_image:
        # paste(img, pos, mask) // mask -> transparency
        garnished.paste(title_img_image, (pos, from_top - 0,), title_img_image)
        pos = pos + title_img_image.size[0] + 4

    #===========================================================================
    # Copyright
    #===========================================================================
    if author:
        text = u"©{0} {1} ".format(year, author)  # WITH trailing space!
        draw.text([pos, from_top], text,
            fill=font_color, font=font)
        text_width = draw.textsize(text, font=font)[0]
        pos = pos + text_width

    # Separate the texts
    pos = pos + 10

    #===========================================================================
    # Technical info (from exif tags)
    #===========================================================================
    if technical_info and (exif_info.camera or exif_info.iso or \
        exif_info.aperture or exif_info.shutter):

        separator = ''
        tech_text = ''

        if exif_info.camera:
            if CAPITALIZE:
                camera_name = ' '.join([s.capitalize() for s in exif_info.camera.split()])
            else:
                camera_name = exif_info.camera
            tech_text += separator
            tech_text += camera_name
            separator = ' - '

        if exif_info.shutter:
            tech_text += separator
            tech_text += "Exp: {0}".format(exif_info.shutter)
            separator = ' - '

        if exif_info.iso:
            tech_text += separator
            tech_text += "ISO: {0}".format(exif_info.iso)
            separator = ' - '

        if exif_info.aperture:
            tech_text += separator
            tech_text += "f/{0}".format(exif_info.aperture)
            separator = ' - '

        pos_r = rtl(tech_text, pos_r, draw)

        # Paste camera icon
        camera_pos = pos_r - camera_image.size[0] - 2
        garnished.paste(camera_image, (camera_pos, from_top,), camera_image)

    if pos >= garnished.size[1] or pos_r < pos:
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

    copy_exif_info(src_filename, dst_filename, copyright_value=exif_copyright)

    return 0
