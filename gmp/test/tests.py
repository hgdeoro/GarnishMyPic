'''
Created on Jan 16, 2013

@author: Horacio G. de Oro
'''

import os
import tempfile
import unittest

from gmp import garnish


class BasicTest(unittest.TestCase):

    def setUp(self):
        this_dir = os.path.dirname(os.path.abspath(__file__))
        self.test_image_01_filename = os.path.join(this_dir, 'test-image-01.jpg')
        assert os.path.exists(self.test_image_01_filename)

    def test_with_test_image_01(self):
        _, filename = tempfile.mkstemp(".jpg", "_gmp_test_")
        os.environ['AUTHOR'] = 'John Doe <jd@example.com>'
        garnish.OVERWRITE = '1'
        garnish.do_garnish(self.test_image_01_filename, filename)
        # ls -1rt /tmp/_gmp_test_*.jpg | tail -n 1 | xargs kde-open
        print "Generated OK - Output file {0}".format(filename)
