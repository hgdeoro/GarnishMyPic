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
- the [font](https://github.com/hgdeoro/GarnishMyPic/blob/master/LiberationSans-Regular.ttf?raw=true) with `wget https://github.com/hgdeoro/GarnishMyPic/blob/master/LiberationSans-Regular.ttf?raw=true`

You don't realy need to download the font, since you could use any TrueType font,
like **/usr/share/fonts/truetype/ubuntu-font-family/Ubuntu-R.ttf**.


Example
-------------------

    python garnish.py --author "Jonh Doe" --title "Tree" --max-size 600x600 original.jpg thumb.jpg

Will convert the original file:

![Original image](https://raw.github.com/hgdeoro/GarnishMyPic/master/test/original.jpg)

into:

![Thumb with info](https://raw.github.com/hgdeoro/GarnishMyPic/master/test/thumb.jpg)

