# -*- coding: utf-8 -*-

'''
Created on Jan 14, 2013

@author: Horacio G. de Oro
'''

import datetime
import os

from PIL import Image, ImageColor, ImageDraw, ImageFont, ImageOps
import subprocess
import json

# TODO: remove all these env. variables and use program arguments
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


class ExifInfo(object):
    def __init__(self, filename, iso, aperture, shutter, camera):
        self.filename = filename
        self.iso = os.environ.get('ISO', iso)
        self.aperture = os.environ.get('APERTURE', aperture)
        self.shutter = os.environ.get('SHUTTER_SPEED', shutter)
        self.camera = os.environ.get('CAMERA', camera)


def _get_exif_info_pyexif(filename):
    import pyexif
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


def do_garnish(src_filename, dst_filename):
    # TODO: check input file is JPEG
    # TODO: check output file extension is JPEG

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

    exif_info = get_exif_info(src_filename)

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
    # TODO: get parameters/config from arguments
    import sys
    src_filename = sys.argv[1]
    dst_filename = sys.argv[2]
    do_garnish(src_filename, dst_filename)


#===============================================================================
# Full list of tags (reported by 'exiftool -s -u FILE.JPG | cut -d : -f 1| sort ') of a Nikon D3100
#===============================================================================
#    ActiveD-Lighting
#    AFAperture
#    AFAreaMode
#    AFInfo2Version
#    AFPointsUsed
#    Aperture
#    AutoDistortionControl
#    AutoFocus
#    BitsPerSample
#    BlueBalance
#    Brightness
#    CFAPattern
#    CircleOfConfusion
#    ColorBalanceUnknown
#    ColorComponents
#    ColorSpace
#    ComponentsConfiguration
#    CompressedBitsPerPixel
#    Compression
#    Contrast
#    ContrastDetectAF
#    ContrastDetectAFInFocus
#    CreateDate
#    CreatorTool
#    CropHiSpeed
#    CurrentIPTCDigest
#    CustomRendered
#    DateDisplayFormat
#    DateTimeOriginal
#    DaylightSavings
#    DigitalZoomRatio
#    Directory
#    DirectoryNumber
#    DistortionVersion
#    DOF
#    EffectiveMaxAperture
#    EncodingProcess
#    ExifByteOrder
#    ExifImageHeight
#    ExifImageWidth
#    ExifToolVersion
#    ExifVersion
#    ExitPupilPosition
#    ExposureBracketValue
#    ExposureCompensation
#    ExposureDifference
#    ExposureMode
#    ExposureProgram
#    ExposureTime
#    ExposureTuning
#    ExternalFlashExposureComp
#    ExternalFlashFirmware
#    ExternalFlashFlags
#    FileInfoVersion
#    FileModifyDate
#    FileName
#    FileNumber
#    FilePermissions
#    FileSize
#    FileSource
#    FileType
#    FilterEffect
#    FirmwareVersion
#    Flash
#    FlashColorFilter
#    FlashCommanderMode
#    FlashCompensation
#    FlashControlMode
#    FlashExposureBracketValue
#    FlashExposureComp
#    FlashGNDistance
#    FlashGroupACompensation
#    FlashGroupAControlMode
#    FlashGroupBCompensation
#    FlashGroupBControlMode
#    FlashGroupCCompensation
#    FlashGroupCControlMode
#    FlashInfoVersion
#    FlashMode
#    FlashpixVersion
#    FlashSetting
#    FlashSource
#    FlashType
#    FNumber
#    FocalLength
#    FocalLength35efl
#    FocalLengthIn35mmFormat
#    FocusDistance
#    FocusMode
#    FocusPosition
#    FOV
#    GainControl
#    GPSVersionID
#    HighISONoiseReduction
#    HueAdjustment
#    HyperfocalDistance
#    ImageBoundary
#    ImageDataSize
#    ImageHeight
#    ImageSize
#    ImageWidth
#    InteropIndex
#    InteropVersion
#    ISO
#    ISO2
#    ISOExpansion
#    ISOExpansion2
#    ISOSetting
#    Lens
#    LensDataVersion
#    LensFStops
#    LensID
#    LensIDNumber
#    LensSpec
#    LensType
#    LightSource
#    LightValue
#    Make
#    MakerNoteVersion
#    MaxApertureAtMaxFocal
#    MaxApertureAtMinFocal
#    MaxApertureValue
#    MaxFocalLength
#    MCUVersion
#    MeteringMode
#    MIMEType
#    MinFocalLength
#    Model
#    ModifyDate
#    MultiExposureAutoGain
#    MultiExposureMode
#    MultiExposureShots
#    MultiExposureVersion
#    Nikon_0x002d
#    Nikon_0x008a
#    Nikon_0x009d
#    Nikon_0x00a3
#    Nikon_0x00bb
#    NoiseReduction
#    Orientation
#    OriginatingProgram
#    PhaseDetectAF
#    PictureControlAdjust
#    PictureControlBase
#    PictureControlName
#    PictureControlQuickAdjust
#    PictureControlVersion
#    PowerUpTime
#    PreviewImage
#    PreviewImageLength
#    PreviewImageStart
#    PrimaryAFPoint
#    ProcessingSoftware
#    ProgramShift
#    ProgramVersion
#    Quality
#    RedBalance
#    ResolutionUnit
#    RetouchHistory
#    Saturation
#    ScaleFactor35efl
#    SceneCaptureType
#    SceneType
#    SensingMethod
#    SerialNumber
#    Sharpness
#    ShootingMode
#    ShotInfoVersion
#    ShutterCount
#    ShutterSpeed
#    Software
#    SubjectDistanceRange
#    SubSecCreateDate
#    SubSecDateTimeOriginal
#    SubSecModifyDate
#    SubSecTime
#    SubSecTimeDigitized
#    SubSecTimeOriginal
#    ThumbnailImage
#    ThumbnailLength
#    ThumbnailOffset
#    Timezone
#    ToningEffect
#    ToningSaturation
#    UnknownInfoVersion
#    UserComment
#    VariProgram
#    VibrationReduction
#    VRInfoVersion
#    WB_RBLevels
#    WhiteBalance
#    WhiteBalanceFineTune
#    XMPToolkit
#    XResolution
#    YCbCrPositioning
#    YCbCrSubSampling
#    YResolution
#===============================================================================
