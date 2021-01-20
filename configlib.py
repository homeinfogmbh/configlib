"""Configuration file parsing library."""

from configparser import ConfigParser
from json import load
from logging import getLogger
from pathlib import Path
from typing import Iterator, Optional, Union


__all__ = ['posix_paths', 'load_ini', 'load_json', 'loadcfg']


JSON = Union[dict, list, str, int, float, bool, None]
POSIX_CONFIG_DIRS = [Path('/etc'), Path('/usr/local/etc')]
LOGGER = getLogger('configlib')


def log_load(path: Union[Path, str]) -> None:
    """Logs the successful loading of the respective path."""

    LOGGER.debug('Loaded config file: %s', path)


def posix_paths(filename: str) -> Iterator[Path]:
    """Yields POSIX search paths for the respective filename."""

    file = Path(filename)

    if file.is_absolute():
        yield file
        return

    for config_dir in POSIX_CONFIG_DIRS:
        yield config_dir.joinpath(file)

    yield Path.home().joinpath(f'.{filename}')


def load_ini(filename: str, *args, encoding: Optional[str] = None,
             interpolation: Optional[type] = None, **kwargs) -> ConfigParser:
    """Loads the respective INI file from POSIX search paths."""

    config_parser = ConfigParser(*args, interpolation=interpolation, **kwargs)
    loaded = config_parser.read(posix_paths(filename), encoding=encoding)

    for path in loaded:
        log_load(path)

    return config_parser


def load_json(filename: str, *, encoding: Optional[str] = None) -> JSON:
    """Loads the respective JSON config file from POSIX search paths."""

    json_config = {}

    for posix_path in posix_paths(filename):
        try:
            with posix_path.open('r', encoding=encoding) as json:
                json = load(json)
        except FileNotFoundError:
            continue
        except PermissionError:
            continue

        log_load(posix_path)
        json_config.update(json)

    return json_config


def loadcfg(filename: str, *args, encoding: Optional[str] = None,
            **kwargs) -> Union[ConfigParser, JSON]:
    """Loads the respective config file."""

    if Path(filename).suffix == '.json':
        return load_json(filename, encoding=encoding)

    return load_ini(filename, *args, encoding=encoding, **kwargs)
