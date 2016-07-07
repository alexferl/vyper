import logging
import os

from . import util

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

    def _search_dict(self, d, key):
        if key in d: return d[key]
        for k, v in d.items():
            if isinstance(v, dict):
                item = self._search_dict(v, key)
                if item is not None:
                    return item

    def get(self, key):
        path = key.split(self.key_delimiter)

        lowercase_key = key.lower()
        val = self._find(lowercase_key)

        if not val:
            source = self._find(path[0].lower())
            if source and isinstance(source, dict):
                val = self._search_dict(source, path[-1])

        if not val:
            return None

        return val

    def _find(self, key):
        key = self._real_key(key)

        # TODO: check args here

        val = self.override.get(key)
        if val:
            log.debug('%s found in override: %s', key, val)
            return val

        if self.automatic_env_applied:
            val = self._get_env(self._merge_with_env_prefix(key))
            if val != '':
                log.debug('%s found in environment: %s', key, val)
                return val

        env_key = self.env.get(key)
        if env_key:
            log.debug('%s registered as env var: %s', key, env_key)
            val = self._get_env(env_key)
            if val != '':
                log.debug('%s found in environment: %s', env_key, val)
                return val
            else:
                log.debug('%s env value unset', env_key)

        val = self.config.get(key)
        if val:
            log.debug('%s found in config: %s', key, val)
            return val

        # TODO: tested for nested here

        val = self.kvstore.get(key)
        if val:
            log.debug('%s found in key/value store: %s', key, val)
            return val

        val = self.defaults.get(key)
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
        """Aliases provide another accessor for the same key.
        This enables one to change a name without breaking the application.
        """
        alias = alias.lower()
        key = key.lower()
        if alias != key and alias != self._real_key(key):
            exists = self.aliases.get('alias')

            if not exists:
                # if we alias something that exists in one of the dicts to
                # another name, we'll never be able to get that value using the
                # original name, so move the config value to the new _real_key.
                val = self.config.get('alias')
                if val:
                    self.config.pop(alias)
                    self.config[key] = val
                val = self.kvstore.get('alias')
                if val:
                    self.kvstore.pop(alias)
                    self.kvstore[key] = val
                val = self.defaults.get('alias')
                if val:
                    self.defaults.pop(alias)
                    self.defaults[key] = val
                val = self.override.get('alias')
                if val:
                    self.override.pop(alias)
                    self.override[key] = val

                self.aliases[alias] = key
        else:
            log.warning('Creating circular reference alias %s %s %s',
                        alias, key, self._real_key(key))

    def _real_key(self, key):
        new_key = self.aliases.get(key)
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
        k = self._real_key(key.lower())
        self.defaults[k] = value

    def set(self, key, value):
        """Sets the value for the key in the override register.
        Will be used instead of values obtained via
        args, config file, ENV, defaults or key/value store.
        """
        k = self._real_key(key.lower())
        self.override[k] = value

    def unmarshall_reader(self, file_, d):
        return util.unmarshall_config_reader(file_, d, self._get_config_type())

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
        if self.config_type != '':
            return self.config_type

    def _get_config_file(self):
        if self.config_file != '':
            return self.config_file

    def _search_in_path(self, path):
        pass

    def _find_config_path(self):
        pass
