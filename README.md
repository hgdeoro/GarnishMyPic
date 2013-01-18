Garnish my pic
====================

Creates a thumbnail of your photo, add a border and put the folowing texts at the bottom:

- title (if specified) - from command line
- year - from command line
- author -from command line or environment variable
- camera model, iso setting, aperture (f number) and exposure time (shutter speed) - from EXIF information

Example
-------------------

    python garnish.py --author "Jonh Doe <jd@example.com>" --title "Tree, tree, tree" original.jpg thumb.jpg

Will convert:

![Original image](https://raw.github.com/hgdeoro/GarnishMyPic/master/test/original.jpg)

into:

![Thumb with info](https://raw.github.com/hgdeoro/GarnishMyPic/master/test/thumb.jpg)

