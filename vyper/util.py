import json
import logging
import os
import pathlib

import yaml

log = logging.getLogger('vyper.util')


class ConfigParserError(Exception):
    """Denotes failing to parse configuration file."""
    def __init__(self, message, *args):
        self.message = message
        super(ConfigParserError, self).__init__(message, *args)

    def __str__(self):
        return 'While parsing config: {0}'.format(self.message)


def abs_pathify(in_path):
    log.info('Trying to resolve absolute path to %s', in_path)

    try:
        return pathlib.Path(in_path).resolve()
    except (OSError, FileNotFoundError) as e:
        log.error('Couldn\'t discover absolute path: %s', e)
        return ''


def exists(path):
    try:
        os.stat(path)
        return True
    except (OSError, FileNotFoundError):
        return False


def unmarshall_config_reader(file_, d, config_type):
    config_type = config_type.lower()

    if config_type in ['yaml', 'yml']:
        try:
            f = yaml.load(file_)
            d.update(yaml.load(f))
        except Exception as e:
            raise ConfigParserError(e)

    elif config_type == 'json':
        try:
            f = json.load(file_)
            d.update(f)
        except Exception as e:
            raise ConfigParserError(e)

    elif config_type == 'toml':
        try:
            d.update(file_)
        except Exception as e:
            raise ConfigParserError(e)

    return d
