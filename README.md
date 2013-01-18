Garnish my pic
====================

Creates a thumbnail of your photo, add a border and put the folowing texts at the bottom:

- title (if specified) - from command line
- year - from command line
- author -from command line or environment variable
- camera model, iso setting, aperture (f number) and exposure time (shutter speed) - from EXIF information


Requeriments
-------------------

- Python 2.7
- exiftool (to install on Ubuntu, run `sudo apt-get install libimage-exiftool-perl`)
- PIL (to install on Ubuntu, run `sudo apt-get install python-imaging`)


Install
-------------------

You can download a [ZIP file](https://github.com/hgdeoro/GarnishMyPic/archive/master.zip).

Or simply donwload:

- the [Python script](https://raw.github.com/hgdeoro/GarnishMyPic/master/garnish.py) with `wget https://raw.github.com/hgdeoro/GarnishMyPic/master/garnish.py`
- the [font](https://github.com/hgdeoro/GarnishMyPic/blob/master/LiberationSans-Regular.ttf?raw=true) with `wget 'https://github.com/hgdeoro/GarnishMyPic/blob/master/LiberationSans-Regular.ttf?raw=true'`

You don't realy need to download the font, since you could use any TrueType font,
like **/usr/share/fonts/truetype/ubuntu-font-family/Ubuntu-R.ttf**, and reference it from the command line.

    python garnish.py (...) --font /usr/share/fonts/truetype/ubuntu-font-family/Ubuntu-R.ttf


Usage
-------------------

    usage: garnish.py [-h] [--author AUTHOR] [--title TITLE] [--year YEAR]
                  [--overwrite] [--output-quality OUTPUT_QUALITY]
                  [--border-size BORDER_SIZE] [--font FONT]
                  [--font-size FONT_SIZE] [--max-size MAX_SIZE] [--basic-info]
                  src_file dst_file

    positional arguments:
      src_file              Path to the original photography
      dst_file              Path where to create the thumbnail

    optional arguments:
      -h, --help            show this help message and exit
      --author AUTHOR       Author information (this script also checks for the
                            GMP_AUTHOR environment variable
      --title TITLE         Title of the pic
      --year YEAR           Year to use on copyright (defaults to current year)
      --overwrite           Overwrite dst_file if exists
      --output-quality OUTPUT_QUALITY
                            Quality of generated JPG (1-100)
      --border-size BORDER_SIZE
                            Border size in pixels
      --font FONT           Path to the TrueType font to use
      --font-size FONT_SIZE
                            Size of text
      --max-size MAX_SIZE   Max size of output image
      --basic-info          Doesn't include technical info (iso, F, exposure)


Example
-------------------

    python garnish.py --author "Jonh Doe" --title "Tree" --max-size 600x600 original.jpg thumb.jpg

Will convert the original file:

![Original image](https://raw.github.com/hgdeoro/GarnishMyPic/master/test/original.jpg)

into:

![Thumb with info](https://raw.github.com/hgdeoro/GarnishMyPic/master/test/thumb.jpg)


Credits
-------------------

- For the camera icon, I use the awesome icons from [http://www.famfamfam.com/lab/icons/silk/](http://www.famfamfam.com/lab/icons/silk/).

License
-------------------

    Copyright 2013 Horacio Guillermo de Oro <hgdeoro@gmail.com>
    
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    
    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.


