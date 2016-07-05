
class Vyper(object):

    def __init__(self, config_name='config', key_delimiter='.'):
        self.config_name = config_name
        self.key_delimiter = key_delimiter
        self.config = {}
        self.override = {}
        self.defaults = {k: v for k, v in self.__class__.__dict__.items()
                         if k[:1] != '_'}
        self.kvstore = {}
        self.args = {}
        self.env = {}
        self.aliases = {}

    def get(self, key):
        if key in self.config:
            return self.config[key]
        elif key in self.defaults:
            return self.defaults[key]
        else:
            print("fuck")

    def set(self, key, value):
        self.config[key] = value

    def set_default(self, key, value):
        self.defaults[key] = value

    def register_alias(self, alias, key):
        self.aliases[alias] = key

    def _real_key(self, key):
        new_key = self.aliases.get(key, None)
        if new_key:
            return self._real_key(new_key)
        else:
            return key



class MyConfig(Vyper):
    APP_NAME = 'myapp'


c = MyConfig()

print(c.APP_NAME)
