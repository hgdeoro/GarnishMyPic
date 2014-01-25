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

import json
import os
import subprocess


class ExifInfo(object):
    def __init__(self, filename, iso, aperture, shutter, camera):
        self.filename = filename
        self.iso = os.environ.get('ISO', iso)
        self.aperture = os.environ.get('APERTURE', aperture)
        self.shutter = os.environ.get('SHUTTER_SPEED', shutter)
        self.camera = os.environ.get('CAMERA', camera)


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
