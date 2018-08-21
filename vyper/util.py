import logging
import os
import pathlib

import pytoml as toml
import yaml

try:
    import ujson as json
except ImportError:
    import json

try:
    FileNotFoundError
except NameError:
    FileNotFoundError = OSError

log = logging.getLogger('vyper.util')


class ConfigParserError(Exception):
    """Denotes failing to parse configuration file."""
    def __init__(self, message, *args):
        self.message = message
        super(ConfigParserError, self).__init__(message, *args)

    def __str__(self):
        return 'While parsing config: {0}'.format(self.message)


def abs_pathify(in_path):
    log.info('Trying to resolve absolute path to {0}'.format(in_path))

    try:
        return pathlib.Path(in_path).resolve()
    except FileNotFoundError as e:
        log.error('Couldn\'t discover absolute path: {0}'.format(e))
        return ''


def exists(path):
    try:
        os.stat(str(path))
        return True
    except FileNotFoundError:
        return False


def unmarshall_config_reader(file_, d, config_type):
    config_type = config_type.lower()

    if config_type in ['yaml', 'yml']:
        try:
            f = yaml.load(file_)
            try:
                d.update(yaml.load(f))
            except AttributeError:  # to read files
                d.update(f)
        except Exception as e:
            raise ConfigParserError(e)

    elif config_type == 'json':
        try:
            f = json.loads(file_)
            d.update(f)
        except Exception as e:
            raise ConfigParserError(e)

    elif config_type == 'toml':
        try:
            try:
                f = toml.loads(file_)
                d.update(f)
            except AttributeError:  # to read streams
                d.update(file_)
        except Exception as e:
            raise ConfigParserError(e)

    return d
