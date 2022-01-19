"""Test load_config() function."""

from configparser import ConfigParser
from json import dump
from tempfile import NamedTemporaryFile
from unittest import TestCase

from configlib import load_config


class TestLoadConfig(TestCase):
    """Test load_config()."""

    def test_load_json(self):
        with NamedTemporaryFile('w+', suffix='.json') as file:
            dump({}, file)
            file.flush()
            file.seek(0)
            json = load_config(file.name)

        self.assertIsInstance(json, dict)

    def test_load_ini(self):
        with NamedTemporaryFile('w+', suffix='.ini') as file:
            file.write('')
            file.flush()
            file.seek(0)
            ini = load_config(file.name)

        self.assertIsInstance(ini, ConfigParser)
