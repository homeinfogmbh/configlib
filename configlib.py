"""Configuration file parsing library."""

from os.path import getmtime
from configparser import ConfigParser
from json import load, dumps


__all__ = ['INIParser', 'JSONParser']


class AlertParser:
    """Abstract configuration file parser that recognizes file changes."""

    def __init__(self, file, encoding=None, alert=False):
        """Initializes the parser with the target file.

        Optionally the configuration can be set to be alert to
        file modification time changes to reload it accordingly.
        """
        self.file = file
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
            self.read(self.file, encoding=self.encoding)
            self.mtime = getmtime(self.file)

    def read(self, filename, encoding=None):
        """Reads the file."""
        raise NotImplementedError()


class INIParser(ConfigParser, AlertParser):
    """Parses INI-ish configuration files."""

    def __init__(self, file, encoding=None, alert=False):
        """Invokes super constructors."""
        AlertParser.__init__(self, file, encoding=encoding, alert=alert)
        super().__init__()

    def __getitem__(self, item):
        """Conditionally loads the configuration
        file and delegates to superclass.
        """
        self.load()
        return super().__getitem__(item)


class JSONParser(AlertParser):
    """Parses JSON-ish configuration files."""

    def __init__(self, file, encoding=None, alert=False, indent=2):
        """Invokes super constructor and sets inital JSON data."""
        super().__init__(file, encoding=encoding, alert=alert)
        self.indent = indent
        self.json = {}

    def __enter__(self):
        self.read()
        return self

    def __exit__(self, *_):
        self.write(indent=self.indent)

    def __getitem__(self, item):
        """Conditionally loads the configuration
        file and delegates to the JSON dictionary.
        """
        self.load()
        return self.json[item]

    def __setitem__(self, item, value):
        """Sets the respective item to the JSON dictionary."""
        self.json[item] = value

    def __getattr__(self, attr):
        """Returns the respective config item."""
        return getattr(self.json, attr)

    def __str__(self):
        return dumps(self.json)

    def read(self, filename, encoding=None):
        """Reads the JSON data from the files."""
        try:
            with open(str(filename), 'r', encoding=encoding) as file:
                self.json.update(load(file))
        except (FileNotFoundError, PermissionError, ValueError):
            return False

        return True

    def write(self, indent=2):
        """Reads the JSON data from the file."""
        with open(self.file, 'w', encoding=self.encoding) as file:
            file.write(dumps(self.json, indent=indent))
