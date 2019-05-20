"""Configuration file parsing library."""

from configparser import ConfigParser
from json import load
from logging import getLogger
from pathlib import Path


__all__ = ['posix_paths', 'load_ini', 'loadcfg', 'load_json']


POSIX_CONFIG_DIRS = (Path('/etc'), Path('/usr/local/etc'))
LOGGER = getLogger(__file__)


def log_load(path):
    """Logs the successful loading of the respective path."""

    LOGGER.debug('Loaded config file: %s', path)


def posix_paths(filename):
    """Yields POSIX search paths for the respective filename."""

    file = Path(filename)

    if file.is_absolute():
        yield file
        return

    for config_dir in POSIX_CONFIG_DIRS:
        yield config_dir.joinpath(file)

    yield Path.home().joinpath('.{}'.format(filename))


def load_ini(filename, *args, encoding=None, interpolation=None, **kwargs):
    """Loads the respective INI file from POSIX search paths."""

    config_parser = ConfigParser(*args, interpolation=interpolation, **kwargs)
    loaded = config_parser.read(posix_paths(filename), encoding=encoding)

    for path in loaded:
        log_load(path)

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

        log_load(posix_path)
        json_config.update(json)

    return json_config
