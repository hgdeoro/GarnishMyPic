'''
Created on Jan 16, 2013

@author: Horacio G. de Oro
'''

import os
import tempfile
import unittest

from gmp import garnish
from gmp.garnish import _exiftool_get_json


class BasicTest(unittest.TestCase):

    def setUp(self):
        this_dir = os.path.dirname(os.path.abspath(__file__))
        self.test_image_01_filename = os.path.join(this_dir, 'test-image-01.jpg')
        assert os.path.exists(self.test_image_01_filename)

    def test_exiftool_get_json(self):
        json_data = _exiftool_get_json(self.test_image_01_filename)
        self.assertTrue('Model' in json_data[0])
        self.assertTrue('Make' in json_data[0])

    def test_with_test_image_01(self):
        _, filename = tempfile.mkstemp(".jpg", "_gmp_test_")
        garnish.do_garnish(self.test_image_01_filename, filename,
            author='John Doe <jd@example.com>',
            overwrite=True)
        # ls -1rt /tmp/_gmp_test_*.jpg | tail -n 1 | xargs kde-open
        print "Generated OK - Output file {0}".format(filename)
