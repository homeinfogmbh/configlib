"""Configuration file parsing library."""

from configparser import ConfigParser
from json import load
from os.path import expanduser, getmtime
from pathlib import Path


__all__ = ['loadcfg', 'parse_bool', 'INIParser', 'JSONParser']


BOOLEAN_STRINGS = {
    'true': True, 'yes': True, 'y': True, 'on': True, '1': True,
    'false': False, 'no': False, 'n': False, 'off': False, '0': False}
CONFIG_DIRS = (Path('/etc'), Path('/usr/local/etc'))


def loadcfg(filename, *args, **kwargs):
    """Loads the files from common locations."""

    config_parser = ConfigParser(*args, **kwargs)

    for config_dir in CONFIG_DIRS:
        config_file = config_dir.joinpath(filename)
        config_parser.read(str(config_file))

    home = Path(expanduser('~'))
    personal_config_file = home.joinpath('.{}'.format(filename))
    config_parser.read(str(personal_config_file))
    return config_parser


def parse_bool(value):
    """Parses a boolean value from a config entry string."""

    if value is None:
        return None

    if isinstance(value, bool):
        return value

    return BOOLEAN_STRINGS.get(value.strip().lower())


class AlertParserMixin:
    """Abstract configuration file parser that recognizes file changes."""

    def __init__(self, file, encoding=None, alert=False):
        """Initializes the parser with the target file.

        Optionally the configuration can be set to be alert to
        file modification time changes to reload it accordingly.
        """
        self.file = Path(file)
        self.encoding = encoding
        self.alert = alert
        self.mtime = None

    @property
    def loaded(self):
        """Determines whether the configuration has been loaded."""
        return self.mtime is not None

    @property
    def changed(self):
        """Determines whether the configuration has changed on disk."""
        return getmtime(self.file) > self.mtime

    def load(self, force=False):
        """Reads the configuration file if
            1)  it was forced,
            2)  it has not yet been loaded
        or
            3)  the Configuration is set to alert and
                the file's timestamp changed.
        """
        if force or not self.loaded or self.alert and self.changed:
            self.read(str(self.file), encoding=self.encoding)
            self.mtime = getmtime(str(self.file))


class INIParser(ConfigParser, AlertParserMixin):     # pylint: disable=R0901
    """Parses INI-ish configuration files."""

    def __init__(self, file, encoding=None, alert=False, **kwargs):
        """Invokes super constructors."""
        AlertParserMixin.__init__(self, file, encoding=encoding, alert=alert)
        ConfigParser.__init__(self, **kwargs)

    def __getitem__(self, item):
        """Conditionally loads the configuration
        file and delegates to superclass.
        """
        self.load()
        return super().__getitem__(item)

    def read(self, filename, encoding=None):    # pylint: disable=W0221
        """Reads the file."""
        self.file = Path(filename)
        return super().read(filename, encoding=encoding)


class JSONParser(AlertParserMixin):
    """Parses JSON-ish configuration files."""

    def __init__(self, file, encoding=None, alert=False):
        """Invokes super constructor and sets inital JSON data."""
        super().__init__(file, encoding=encoding, alert=alert)
        self.json = {}

    def __getitem__(self, item):
        """Conditionally loads the configuration
        file and delegates to the JSON dictionary.
        """
        self.load()
        return self.json[item]

    def __getattr__(self, attr):
        """Conditionally loads the configuration
        file and delegates to the JSON dictionary.
        """
        self.load()
        return getattr(self.json, attr)

    def read(self, filename, encoding=None):
        """Reads the JSON data from the files."""
        try:
            with open(str(filename), 'r', encoding=encoding) as file:
                self.json = load(file)
        except (FileNotFoundError, PermissionError, ValueError):
            return False

        self.file = Path(filename)
        return True
