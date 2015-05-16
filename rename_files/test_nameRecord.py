from unittest import TestCase

__author__ = 'California Audio Visual Preservation Project'

from rename_files.renaming_model import *
class TestNameRecord(TestCase):
    def setUp(self):
        self.tester = NameRecord("/Volumes/CAVPPTestDrive/DPLA0003/Images/_Anaheim/tif/ana103.tif", "caps000001", )
    def test_get_status(self):
        self.fail()

    def test_set_Pending(self):
        self.fail()

    def test_set_Done(self):
        self.fail()

    def test_calculate_md5(self):
        self.fail()