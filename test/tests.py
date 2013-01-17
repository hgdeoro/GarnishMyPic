'''
Created on Jan 16, 2013

@author: Horacio G. de Oro
'''

import os
import tempfile
import unittest

import garnish


class BasicTest(unittest.TestCase):

    def setUp(self):
        this_dir = os.path.dirname(os.path.abspath(__file__))
        self.test_image_01_filename = os.path.join(this_dir, 'test-image-01.jpg')
        assert os.path.exists(self.test_image_01_filename)

    def test_exiftool_get_json(self):
        json_data = garnish._exiftool_get_json(self.test_image_01_filename)
        self.assertTrue('Model' in json_data[0])
        self.assertTrue('Make' in json_data[0])

    def test_with_test_image_01(self):
        # Temporary file for output
        _, filename = tempfile.mkstemp(".jpg", "_gmp_test_")

        # Default parameters
        kwargs = dict(
            title='Some test',
            author='John Doe <jd@example.com>',
            overwrite=True,
            year=2000,
            font_file='/usr/share/fonts/truetype/droid/DroidSans-Bold.ttf',
            font_size=12,
            output_quality=90,
            border_size=4,
            max_size=(800, 800,),
        )

        # First, check if works
        exit_status = garnish.do_garnish(self.test_image_01_filename, filename, **kwargs)
        self.assertEqual(exit_status, 0)

        # Check if fails when overwrite is false and file exists
        kwargs2 = dict(kwargs)
        kwargs2['overwrite'] = False
        exit_status = garnish.do_garnish(self.test_image_01_filename, filename, **kwargs2)
        self.assertEqual(exit_status, 1)

        # Check if detects non-existing font-file
        kwargs2 = dict(kwargs)
        kwargs2['font_file'] = '/non/existing/font/file.ttf'
        exit_status = garnish.do_garnish(self.test_image_01_filename, filename, **kwargs2)
        self.assertEqual(exit_status, 1)

        # Check if detect input file that isn't an image
        kwargs2 = dict(kwargs)
        exit_status = garnish.do_garnish(__file__, filename, **kwargs2)
        self.assertEqual(exit_status, 1)

        # ls -1rt /tmp/_gmp_test_*.jpg | tail -n 1 | xargs kde-open
        print "Generated OK - Output file {0}".format(filename)
