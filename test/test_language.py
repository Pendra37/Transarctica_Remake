# -*- coding: utf-8 -*-
from os import remove
from os.path import isfile
from model import Language
from unittest import TestCase


class TestLanguage(TestCase):
    def test_load(self):
        language = Language()
        # confirm that defaults are used
        self.assertEquals(language.strings["speed"], "speed")

        language = Language("base")
        # confirm that custom values added
        self.assertEquals(language.strings["speed"], "sebesség")
        # confirm that not custom defined values are still defaults
        self.assertEquals(language.strings["long 1"], "dolor sit amet")

    def test_save(self):
        sample_file = "test/lang_en.xml"
        check_file = "test/lang_check.xml"
        if isfile(sample_file):
            remove(sample_file)
        with open(check_file, "r") as check_file_handle:
           check_xml = check_file_handle.read()
        language = Language()
        language.save(sample_file)
        with open(sample_file, "r") as sample_file_handle:
            sample_xml = sample_file_handle.read()
        self.assertEquals(sample_xml, check_xml)
