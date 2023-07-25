"""Test load_ini() function."""

from configparser import ConfigParser
from tempfile import NamedTemporaryFile
from unittest import TestCase

from configlib import load_ini


INI_FILE = """\
[FirstSection]
string = Hello
no_spaces_around_delimiters=World

[second_section]
integer = 42
float = 3.14
boolean = yes
"""


class TestLoadIni(TestCase):
    """Test load_ini()."""

    def setUp(self) -> None:
        with NamedTemporaryFile("w+", suffix=".ini") as file:
            file.write(INI_FILE)
            file.flush()
            file.seek(0)
            self.ini = load_ini(file.name)

    def test_instance(self):
        self.assertIsInstance(self.ini, ConfigParser)

    def test_sections(self):
        self.assertSequenceEqual(
            list(self.ini), ["DEFAULT", "FirstSection", "second_section"]
        )

    def test_values(self):
        self.assertEqual(self.ini.get("FirstSection", "string"), "Hello")
        self.assertEqual(
            self.ini.get("FirstSection", "no_spaces_around_delimiters"), "World"
        )
        self.assertEqual(self.ini.getint("second_section", "integer"), 42)
        self.assertEqual(self.ini.getfloat("second_section", "float"), 3.14)
        self.assertEqual(self.ini.getboolean("second_section", "boolean"), True)
