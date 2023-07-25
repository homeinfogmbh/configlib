"""Test load_json() function."""

from json import dump
from tempfile import NamedTemporaryFile
from unittest import TestCase

from configlib import load_json


JSON = {
    "list": [True, "two", 3, 4.0],
    "bool": False,
    "null": None,
    "object": {"key": "value"},
}


class TestLoadJSON(TestCase):
    """Test load_json()."""

    def setUp(self) -> None:
        with NamedTemporaryFile("w+", suffix=".json") as file:
            dump(JSON, file)
            file.flush()
            file.seek(0)
            self.json = load_json(file.name)

    def test_instance(self):
        self.assertIsInstance(self.json, dict)

    def test_value(self):
        self.assertDictEqual(self.json, JSON)
