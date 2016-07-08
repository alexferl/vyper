import logging
import os
import pprint

from . import util

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('vyper')

# Universally supported extensions.
SUPPORTED_EXTS = ['json', 'toml', 'yaml', 'yml']

# Universally supported remote providers.
SUPPORTED_REMOTE_PROVIDERS = ['etcd', 'consul']


class Vyper(object):
    """Vyper is a prioritized configuration registry. It maintains a set of
    configuration sources, fetches values to populate those, and provides
    them according to the source's priority.
    The priority of the sources is the following:
        1. overrides
        2. args
        3. env. variables
        4. config file
        5. key/value store
        6. defaults

    For example, if values from the following sources were loaded:

    defaults: {
        "secret": "",
        "user": "default",
        "endpoint": "https://localhost"
        }

    config: {
        "user": "root"
        "secret": "defaultsecret"
        }

    env: {
        "secret": "somesecretkey"
        }

    The resulting config will have the following values:
        {
            "secret": "somesecretkey",
            "user": "root",
            "endpoint": "https://localhost"
        }
    """
    def __init__(self, config_name='config', key_delimiter='.'):
        # Delimiter that separates a list of keys
        # used to access a nested value in one go.
        self.key_delimiter = key_delimiter

        # A set of paths to look for the config file in.
        self.config_paths = []

        # A set of remote providers to search for the configuration.
        self.remote_providers = []

        # Name of file to look for inside the path.
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

    def watch_config(self):
        # TODO: implement this
        pass

    def set_config_file(self, file_):
        """Explicitly define the path, name and extension of the config file
        Vyper will use this and not check any of the config paths.
        """
        if file_ != '':
            self.config_file = file_

    def set_env_prefix(self, prefix):
        """Define a prefix that ENVIRONMENT variables will use.
        e.g. if your prefix is "spf", the env registry will look
        for env. variables that start with "SPF_"
        """
        if prefix != '':
            self.env_prefix = prefix

    def _merge_with_env_prefix(self, key):
        if self.env_prefix != '':
            return (self.env_prefix + '_' + key).upper()

    def _get_env(self, key):
        """Wrapper around os.getenv() which replaces characters
        in the original key. This allows env vars which have different keys
        than the config object keys.
        """
        if self.env_key_replacer:
            key = self.env_key_replacer.replace(key)
        return os.getenv(key, '')

    def config_file_used(self):
        """Return the file used to populate the config registry."""
        return self.config_file

    def add_config_path(self, path):
        """Add a path for Vyper to search for the config file in.
        Can be called multiple times to define multiple search paths.
        """
        # TODO: implement this

    def add_remote_provider(self, provider, endpoint, path):
        """Adds a remote configuration source.
        Remote Providers are searched in the order they are added.
        provider is a string value, "etcd" or "consul" are currently supported.
        endpoint is the url. etcd requires http://ip:port consul requires
        ip:port path is the path in the k/v store to retrieve configuration
        To retrieve a config file called myapp.json from /configs/myapp.json
        you should set path to /configs and set config name (set_config_name)
        to "myapp"
        """
        # TODO: implement this

    def add_secure_remote_provider(self, provider, endpoint, path,
                                   secretkeyring):
        """AddSecureRemoteProvider adds a remote configuration source.
        Secure Remote Providers are searched in the order they are added.
        provider is a string value, "etcd" or "consul" are currently supported.
        endpoint is the url. etcd requires http://ip:port consul requires
        ip:port secretkeyring is the filepath to your openpgp secret keyring.
        e.g. /etc/secrets/myring.gpg path is the path in the k/v store to
        retrieve configuration.
        To retrieve a config file called myapp.json from /configs/myapp.json
        you should set path to /configs and set config name (set_config_name)
        to"myapp"
        Secure Remote Providers are implemented with
        github.com/xordataexchange/crypt
        """
        # TODO: implement this

    def _provider_path_exists(self):
        # TODO: implement this
        pass

    def _search_dict(self, d, key):
        if key in d:
            return d[key]
        for k, v in d.items():
            if isinstance(v, dict):
                item = self._search_dict(v, key)
                if item is not None:
                    return item

    def get(self, key):
        """Vyper is essentially repository for configurations
        get can retrieve any value given the key to use
        get has the behavior of returning the value associated with the first
        place from where it is set. Viper will check in the following order:
        override, arg, env, config file, key/value store, default.
        """
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

    def sub(self, key):
        """Returns new Vyper instance representing a sub tree of this instance.
        """
        # TODO: implement this

    def bind_args(self, args):
        return self.bind_arg_values(args)

    def bind_arg_values(self, args):
        for k, v in args.items():
            try:
                self.bind_arg_value(k, v)
            except ValueError:
                pass

    def bind_arg_value(self, key, arg):
        if arg is None:
            raise ValueError('arg for {} is None'.format(key))

        self.args[key.lower()] = arg

    def _find(self, key):
        """Given a key, find the value
        Vyper will check in the following order:
        override, arg, env, config file, key/value store, default
        Vyper will check to see if an alias exists first.
        """
        key = self._real_key(key)

        val = self.args.get(key)
        if val:
            log.debug('%s found in args: %s', key, val)
            return val

        val = self.override.get(key)
        if val:
            log.debug('%s found in override: %s', key, val)
            return val

        if self.automatic_env_applied:
            # even if it hasn't been registered, if `automatic_env` is used,
            # check any `get` request
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

        # TODO: implement Test for nested config parameter

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
        """Check to see if the key has been set in any of the data locations.
        """
        # TODO: implement this

    def automatic_env(self):
        """Have Vyper check ENV variables for all keys set in
        config, default & args.
        """
        # TODO: implement this

    def set_env_key_replacer(self, r):
        """Sets the strings.Replacer on the Vyper object.
        Useful for mapping an environment variable to a key that does
        not match it.
        """
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
        """Check to see if the given key (or an alias) is in the config file.
        """
        # if the requested key is an alias, then return the proper key
        key = self._real_key(key)

        exists = self.config.get(key)
        return exists

    def set_default(self, key, value):
        """Set the default value for this key.
        Default only used when no value is provided by the user via
        arg, config or env.
        """
        k = self._real_key(key.lower())
        self.defaults[k] = value

    def set(self, key, value):
        """Sets the value for the key in the override register.
        Will be used instead of values obtained via
        args, config file, env, defaults or key/value store.
        """
        k = self._real_key(key.lower())
        self.override[k] = value

    def read_config(self, file_):
        """Vyper will read a configuration file, setting existing keys to
        `None` if the key does not exist in the file.
        """
        self._unmarshall_reader(file_, self.config)

    def _unmarshall_reader(self, file_, d):
        """Unmarshall a file into a dict."""
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
        """Return all settings as a `dict`."""
        d = {}

        for k in self.all_keys():
            d[k] = self.get(k)

        return d

    def set_config_name(self, name):
        """Name for the config file. Does not include extension."""
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
        # TODO: implement this
        pass

    def _find_config_path(self):
        """Search all `config_paths` for any config file.
        Returns the first path that exists (and is a config file).
        """
        # TODO: implement this

    def debug(self):
        """Prints all configuration registries for debugging purposes."""
        print('Aliases:')
        pprint.pprint(self.aliases)
        print('Override:')
        pprint.pprint(self.override)
        print('Args:')
        pprint.pprint(self.args)
        print('Env:')
        pprint.pprint(self.env)
        print('Key/Value Store:')
        pprint.pprint(self.kvstore)
        print('Config:')
        pprint.pprint(self.config)
        print('Defaults:')
        pprint.pprint(self.defaults)
