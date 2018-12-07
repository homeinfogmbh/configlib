"""Configuration file parsing library."""

from configparser import ConfigParser
from json import load
from os.path import expanduser
from pathlib import Path


__all__ = ['posix_paths', 'load_ini', 'loadcfg', 'load_json']


POSIX_CONFIG_DIRS = (Path('/etc'), Path('/usr/local/etc'))


def posix_paths(filename):
    """Yields POSIX search paths for the respective filename."""

    file = Path(filename)

    if file.is_absolute():
        yield file
        return

    for config_dir in POSIX_CONFIG_DIRS:
        yield config_dir.joinpath(file)

    home = Path(expanduser('~'))
    yield home.joinpath('.{}'.format(filename))


def load_ini(filename, *args, interpolation=None, **kwargs):
    """Loads the respective INI file from POSIX search paths."""

    config_parser = ConfigParser(*args, interpolation=interpolation, **kwargs)

    for posix_path in posix_paths(filename):
        config_parser.read(str(posix_path))

    return config_parser


loadcfg = load_ini  # pylint: disable=C0103


def load_json(filename):
    """Loads the respective JSON config file from POSIX search paths."""

    json_config = {}

    for posix_path in posix_paths(filename):
        try:
            with posix_path.open('r') as json:
                json = load(json)
        except FileNotFoundError:
            continue
        except PermissionError:
            continue

        json_config.update(json)

    return json_config
