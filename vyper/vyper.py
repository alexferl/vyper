import logging
import os

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('vyper')


class Vyper(object):
    def __init__(self, config_name='config', key_delimiter='.'):
        self.key_delimiter = key_delimiter

        self.config_name = config_name
        self.config_file = ''
        self.config_type = ''
        self.env_prefix = ''

        self.automatic_env_applied = False
        self.env_key_replacer = None

        self.config = {}
        self.override = {}
        self.defaults = {}
        self.kvstore = {}
        self.args = {}
        self.env = {}
        self.aliases = {}

    def set_config_file(self, file_):
        if file_ != '':
            self.config_file = file_

    def set_env_prefix(self, prefix):
        if prefix != '':
            self.env_prefix = prefix

    def _merge_with_env_prefix(self, key):
        if self.env_prefix != '':
            return (self.env_prefix + '_' + key).upper()

    def _get_env(self, key):
        if self.env_key_replacer:
            key = self.env_key_replacer.replace(key)
        return os.getenv(key, '')

    def config_file_used(self):
        return self.config_file

    def add_config_path(self, path):
        pass

    def get(self, key):
        path = key.split(self.key_delimiter)

        lowercase_key = key.lower()
        val = self._find(lowercase_key)

        if not val:
            source = self._find(path[0].lower())
            if source and isinstance(source, dict):
                val = source[path[1:][0]]

        if not val:
            return None

        return val

    def _find(self, key):
        key = self._real_key(key)

        # TODO: check args here

        val = self.override.get(key, False)
        if val:
            log.debug('%s found in override: %s', key, val)
            return val

        if self.automatic_env_applied:
            val = self._get_env(self._merge_with_env_prefix(key))
            if val != '':
                log.debug('%s found in environment: %s', key, val)
                return val

        env_key = self.env.get(key, False)
        if env_key:
            log.debug('%s registered as env var: %s', key, env_key)
            val = self._get_env(env_key)
            if val != '':
                log.debug('%s found in environment: %s', env_key, val)
                return val
            else:
                log.debug('%s env value unset', env_key)

        val = self.config.get(key, False)
        if val:
            log.debug('%s found in config: %s', key, val)
            return val

        # TODO: tested for nested here

        val = self.kvstore.get(key, False)
        if val:
            log.debug('%s found in key/value store: %s', key, val)
            return val

        val = self.defaults.get(key, False)
        if val:
            log.debug('%s found in defaults: %s', key, val)
            return val

        return None

    def is_set(self, key):
        pass

    def automatic_env(self):
        pass

    def set_env_key_replacer(self, r):
        self.env_key_replacer = r

    def register_alias(self, alias, key):
        self.aliases[alias] = key

    def _register_alias(self, alias, key):
        pass

    def _real_key(self, key):
        new_key = self.aliases.get(key, False)
        if new_key:
            return self._real_key(new_key)
        else:
            return key

    def in_config(self, key):
        pass

    def set_default(self, key, value):
        """Set the default value for this key.
        Default only used when no value is provided by the user via
        arg, config or ENV.
        """
        key = self._real_key(key.lower())
        self.defaults[key] = value

    def set(self, key, value):
        """Sets the value for the key in the override register.
        Will be used instead of values obtained via
        args, config file, ENV, defaults or key/value store.
        """
        key = self._real_key(key.lower())
        self.override[key] = value

    def all_keys(self):
        """Return all keys regardless where they are set."""
        d = {}

        for k in self.defaults.keys():
            d[k.lower()] = {}

        for k in self.args.keys():
            d[k.lower()] = {}

        for k in self.env.keys():
            d[k.lower()] = {}

        for k in self.config.keys():
            d[k.lower()] = {}

        for k in self.kvstore.keys():
            d[k.lower()] = {}

        for k in self.override.keys():
            d[k.lower()] = {}

        for k in self.aliases.keys():
            d[k.lower()] = {}

        return d.keys()

    def all_settings(self):
        """Return all settings as a dict."""
        d = {}

        for k in self.all_keys():
            d[k] = self.get(k)

        return d

    def set_config_name(self, name):
        """Name for the config file. Does not include extension.
        """
        if name != '':
            self.config_name = name

    def set_config_type(self, type_):
        """Sets the type of the configuration returned by the
        remote source, e.g. "json".
        """
        if type_ != '':
            self.config_type = type_

    def _get_config_type(self):
        pass

    def _get_config_file(self):
        pass

    def _search_in_path(self, path):
        pass

    def _find_config_path(self):
        pass
