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

import os

from PIL import Image


def get_default_font():
    this_dir = os.path.dirname(os.path.abspath(__file__))
    default_font = os.path.join(this_dir, '../LiberationSans-Regular.ttf')
    assert os.path.exists(default_font)
    return default_font


def get_camera_image(max_size):
    this_dir = os.path.dirname(os.path.abspath(__file__))
    camera_icon_filename = os.path.join(this_dir, '../camera-icon.png')
    assert os.path.exists(camera_icon_filename)

    camera_image = Image.open(camera_icon_filename)
    camera_image.thumbnail(max_size, Image.ANTIALIAS)
    return camera_image


def env_get_int(env_name, default):
    try:
        return int(os.environ[env_name])
    except KeyError:
        return default
    except ValueError:
        return default

#===============================================================================
# Default values
#===============================================================================
GMP_AUTHOR = os.environ.get('GMP_AUTHOR', None)
GMP_EXIF_COPYRIGHT = os.environ.get('GMP_EXIF_COPYRIGHT', None)
GMP_FONT = os.environ.get('GMP_FONT', get_default_font())
GMP_DEFAULT_MAX_SIZE = os.environ.get('GMP_DEFAULT_MAX_SIZE', '800x800')
GMP_COLOR = os.environ.get('GMP_COLOR', '#545454')
GMP_TITLE_IMAGE = os.environ.get('GMP_TITLE_IMAGE', None)
GMP_TITLE = os.environ.get('GMP_TITLE', None)
GMP_OUTPUT_DIR = os.environ.get('GMP_OUTPUT_DIR',
    os.path.join(os.path.abspath(os.path.expanduser('~')), "Desktop/"))

GMP_OUTPUT_QUALITY = env_get_int('GMP_OUTPUT_QUALITY', 97)
GMP_BORDER = env_get_int('GMP_DEFAULT_BORDER', 10)
GMP_DEFAULT_FONT_SIZE = env_get_int('GMP_DEFAULT_FONT_SIZE', 12)
