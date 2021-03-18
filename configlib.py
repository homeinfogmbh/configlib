"""Configuration file parsing library."""

from configparser import ConfigParser
from json import load
from logging import getLogger
from os import name, getenv
from pathlib import Path
from typing import Any, Iterator, Optional, Union


__all__ = ['loadcfg']


JSON = Union[dict, list, str, int, float, bool, None]
NT_ENV_PATH_VARS = ['%LOCALAPPDATA%', '%APPDATA%']
POSIX_CONFIG_DIRS = [Path('/etc'), Path('/usr/local/etc')]
LOGGER = getLogger('configlib')


class DeferredConfigProxy:
    """Proxy to access a configuration object with delayed file loading."""

    def __init__(self, filename: Union[Path, str], **kwargs):
        """Sets the config file path."""
        self.filename = Path(filename)
        self.kwargs = kwargs
        self.config_object = None

    @property
    def loaded(self) -> bool:
        """Determines whether the configuration has been loaded."""
        return self.config_object is not None

    def load(self, *, force: bool = False) -> bool:
        """Loads the configuration file."""
        if force or self.config_object is None:
            self.config_object = load_config(self.filename, **self.kwargs)
            return True

        return False

    def __getitem__(self, key: str) -> Any:
        """Delegates to the config object."""
        self.load()
        return self.config_object[key]

    def __getattr__(self, attr: str) -> Any:
        """Delegates to the config object."""
        self.load()
        return getattr(self.config_object, attr)


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


def load_config(filename: Path, **kwargs) -> Union[ConfigParser, JSON]:
    """Loads the respective config file."""

    if filename.suffix == '.json':
        return load_json(filename, **kwargs)

    return load_ini(filename, **kwargs)


def loadcfg(filename: str, **kwargs) -> DeferredConfigProxy:
    """Loads the respective config file."""

    return DeferredConfigProxy(filename, **kwargs)
