"""Configuration file parsing library."""

from configparser import ConfigParser
from json import load
from logging import getLogger
from os import name, getenv
from pathlib import Path
from typing import Iterable, Iterator, Optional, Union


__all__ = ['load_config', 'load_ini', 'load_json', 'search_paths']


JSON = Union[dict, list, str, int, float, bool, None]
NT_ENV_PATH_VARS = ['%LOCALAPPDATA%', '%APPDATA%']
POSIX_CONFIG_DIRS = [Path('/etc'), Path('/usr/local/etc')]
LOGGER = getLogger('configlib')
Config = Union[ConfigParser, JSON]


def log_load(path: Union[Path, str]) -> None:
    """Log the successful loading of the respective path."""

    LOGGER.debug('Loaded config file: %s', path)


def search_dirs() -> Iterable[Path]:
    """Yield config search directories."""

    if name == 'posix':
        return list(POSIX_CONFIG_DIRS)

    if name == 'nt':
        return [Path(getenv(var)) for var in NT_ENV_PATH_VARS]

    raise NotImplementedError(f'Unsupported operating system: {name}')


def search_paths(filename: str) -> Iterator[Path]:
    """Yield POSIX search paths for the respective filename."""

    if (file := Path(filename)).is_absolute():
        yield file
        return

    for config_dir in search_dirs():
        yield config_dir / file

    yield Path.home() / f'.{filename}'


def load_ini(
        filename: str,
        *args,
        encoding: Optional[str] = None,
        interpolation: Optional[type] = None,
        **kwargs
) -> ConfigParser:
    """Load the respective INI file from POSIX search paths."""

    config_parser = ConfigParser(*args, interpolation=interpolation, **kwargs)

    for path in config_parser.read(search_paths(filename), encoding=encoding):
        log_load(path)

    return config_parser


def load_json_file(path: Path, *, encoding: Optional[str] = None) -> JSON:
    """Safely load a single JSOn file."""

    try:
        with path.open('r', encoding=encoding) as file:
            json = load(file)
    except (FileNotFoundError, PermissionError):
        return {}

    log_load(path)
    return json


def load_json(filename: str, *, encoding: Optional[str] = None) -> JSON:
    """Load the respective JSON config file from POSIX search paths."""

    json = {}

    for path in search_paths(filename):
        json.update(load_json_file(path, encoding=encoding))

    return json


def load_config(filename: Union[Path, str], **kwargs) -> Config:
    """Load the respective config file."""

    if Path(filename).suffix == '.json':
        return load_json(filename, **kwargs)

    return load_ini(filename, **kwargs)
