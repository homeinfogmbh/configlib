"""Configuration file parsing library."""

from configparser import ConfigParser
from json import load
from logging import getLogger
from os import name, getenv
from pathlib import Path
from typing import Iterator, Optional, Union


__all__ = ['load_ini', 'load_json', 'loadcfg', 'search_paths']


JSON = Union[dict, list, str, int, float, bool, None]
NT_ENV_PATH_VARS = ['%LOCALAPPDATA%', '%APPDATA%']
POSIX_CONFIG_DIRS = [Path('/etc'), Path('/usr/local/etc')]
LOGGER = getLogger('configlib')


def log_load(path: Union[Path, str]) -> None:
    """Logs the successful loading of the respective path."""

    LOGGER.debug('Loaded config file: %s', path)


def search_paths(filename: str) -> Iterator[Path]:
    """Yields POSIX search paths for the respective filename."""

    file = Path(filename)

    if file.is_absolute():
        yield file
        return

    if name == 'posix':
        config_dirs = POSIX_CONFIG_DIRS
    elif name == 'nt':
        config_dirs = [Path(getenv(var)) for var in NT_ENV_PATH_VARS]
    else:
        raise NotImplementedError(f'Unsupported operating system: {name}')

    for config_dir in config_dirs:
        yield config_dir.joinpath(file)

    yield Path.home().joinpath(f'.{filename}')


def load_ini(filename: str, *args, encoding: Optional[str] = None,
             interpolation: Optional[type] = None, **kwargs) -> ConfigParser:
    """Loads the respective INI file from POSIX search paths."""

    config_parser = ConfigParser(*args, interpolation=interpolation, **kwargs)

    for path in config_parser.read(search_paths(filename), encoding=encoding):
        log_load(path)

    return config_parser


def load_json(filename: str, *, encoding: Optional[str] = None) -> JSON:
    """Loads the respective JSON config file from POSIX search paths."""

    json_config = {}

    for path in search_paths(filename):
        try:
            with path.open('r', encoding=encoding) as json:
                json = load(json)
        except FileNotFoundError:
            continue
        except PermissionError:
            continue

        log_load(path)
        json_config.update(json)

    return json_config


def loadcfg(filename: str, *args, encoding: Optional[str] = None,
            **kwargs) -> Union[ConfigParser, JSON]:
    """Loads the respective config file."""

    if Path(filename).suffix == '.json':
        return load_json(filename, encoding=encoding)

    return load_ini(filename, *args, encoding=encoding, **kwargs)
