import argparse
import json
import tempfile
import unittest

import os
import pytoml as toml
import vyper
import yaml
from builtins import str as text
from vyper import errors

try:
    FileNotFoundError
except NameError:
    FileNotFoundError = OSError


yaml_example = '''Hacker: true
name: steve
hobbies:
- skateboarding
- snowboarding
- go
clothing:
  jacket: leather
  trousers: denim
  pants:
    size: large
age: 35
eyes : brown
beard: true'''

toml_example = '''title = "TOML Example"
[owner]
organization = "MongoDB"
Bio = "MongoDB Chief Developer Advocate & Hacker at Large"
dob = 1979-05-27T07:32:00Z # First class dates? Why not?'''

json_example = {
    "id": "0001",
    "type": "donut",
    "name": "Cake",
    "ppu": 0.55,
    "batters": {
        "batter": [
            {"type": "Regular"},
            {"type": "Chocolate"},
            {"type": "Blueberry"},
            {"type": "Devil's Food"}
        ]
    }
}


class TestVyper(unittest.TestCase):
    def setUp(self):
        self.v = vyper.Vyper()

    def _init_configs(self):
        self.v.set_config_type('yaml')
        r = yaml.dump(text(yaml_example))
        self.v._unmarshall_reader(r, self.v._config)

        self.v.set_config_type('json')
        r = json.dumps(json_example)
        self.v._unmarshall_reader(r, self.v._config)

        self.v.set_config_type('toml')
        r = toml.loads(toml_example)
        self.v._unmarshall_reader(r, self.v._config)

    def _init_yaml(self):
        self.v.set_config_type('yaml')
        r = yaml.dump(yaml_example)
        self.v._unmarshall_reader(r, self.v._config)

    def _init_json(self):
        self.v.set_config_type('json')
        r = json.dumps(json_example)
        self.v._unmarshall_reader(r, self.v._config)

    def _init_toml(self):
        self.v.set_config_type('toml')
        r = toml.loads(toml_example)
        self.v._unmarshall_reader(r, self.v._config)

    def _init_dirs(self):
        test_dirs = ['a a', 'b', 'c\c', 'D_']
        config = 'improbable'

        root = tempfile.mkdtemp()

        def cleanup():
            try:
                os.removedirs(root)
            except FileNotFoundError:
                pass

        os.chdir(root)

        for dir_ in test_dirs:
            os.mkdir(dir_, 0o0750)

            f = '{0}.toml'.format(config)
            flags = os.O_WRONLY | os.O_CREAT
            rel_path = '{0}/{1}'.format(dir_, f)
            abs_file_path = os.path.join(root, rel_path)
            with os.fdopen(os.open(abs_file_path, flags, 0o0640), 'w') as fp:
                fp.write("key = \"value is {0}\"\n".format(dir_))

        return root, config, cleanup

    def test_basics(self):
        self.v.set_config_file('/tmp/config.yaml')
        self.assertEqual('/tmp/config.yaml', self.v._get_config_file())

    def test_default(self):
        self.v.set_default('age', 45)
        self.assertEqual(45, self.v.get('age'))

        self.v.set_default('clothing.jacket', 'slacks')
        self.assertEqual('slacks', self.v.get('clothing.jacket'))

    def test_unmarshalling(self):
        # TODO: not complete
        self.v.set_config_type('yaml')
        r = yaml.dump(yaml_example)
        self.v._unmarshall_reader(r, self.v._config)
        self.assertTrue(self.v.in_config('name'))
        self.assertFalse(self.v.in_config('state'))
        self.assertEqual('steve', self.v.get('name'))
        self.assertEqual(35, self.v.get('age'))

    def test_override(self):
        self.v.set('age', 40)
        self.assertEqual(40, self.v.get('age'))

    def test_default_post(self):
        self.assertNotEqual('NYC', self.v.get('state'))
        self.v.set_default('state', 'NYC')
        self.assertEqual('NYC', self.v.get('state'))

    def test_aliases(self):
        self.v.register_alias('years', 'age')
        self.v.set('years', 45)
        self.assertEqual(45, self.v.get('age'))

    #def test_alias_in_config_file(self):
    #    # the config file specifies "beard". If we make this an alias for
    #    # "hasbeard", we still want the old config file to work with beard.
    #    self._init_yaml()
    #    self.v.register_alias('beard', 'hasbeard')
    #    # self.v.debug()
    #    self.assertEqual(True, self.v.get('hasbeard'))
    #    self.v.set('hasbeard', False)
    #    self.assertEqual(False, self.v.get('beard'))

    def test_yaml(self):
        self._init_yaml()
        self.assertEqual('steve', self.v.get('name'))

    def test_json(self):
        self._init_json()
        self.assertEqual('0001', self.v.get('id'))

    def test_toml(self):
        self._init_toml()
        self.assertEqual('TOML Example', self.v.get('title'))

    def test_env(self):
        self._init_json()

        self.v.bind_env('id')
        self.v.bind_env('f', 'FOOD')

        os.environ['ID'] = '13'
        os.environ['FOOD'] = 'apple'
        os.environ['NAME'] = 'crunk'

        self.assertEqual('13', self.v.get('id'))
        self.assertEqual('apple', self.v.get('f'))
        self.assertEqual('Cake', self.v.get('name'))

        self.v.automatic_env()

        self.assertEqual('crunk', self.v.get('name'))

    def test_auto_env(self):
        self.v.automatic_env()
        os.environ['FOO_BAR'] = '13'
        self.assertEqual('13', self.v.get('foo_bar'))

    def test_auto_env_with_prefix(self):
        self.v.automatic_env()
        self.v.set_env_prefix('Baz')
        os.environ['BAZ_BAR'] = '13'
        self.assertEqual('13', self.v.get('bar'))

    def test_set_env_replacer(self):
        self.v.automatic_env()
        os.environ['REFRESH_INTERVAL'] = '30s'

        self.v.set_env_key_replacer('-', '_')

        self.assertEqual('30s', self.v.get('refresh-interval'))

    def test_all_keys(self):
        pass

    def test_case_insensitive(self):
        self.v.set('Title', 'Checking Case')
        self.assertEqual('Checking Case', self.v.get('tItle'))

    def test_aliases_of_aliases(self):
        self.v.register_alias('Foo', 'Bar')
        self.v.register_alias('Bar', 'Title')
        self.v.set('Foo', 'Checking Case')

        self.assertEqual('Checking Case', self.v.get('Bar'))

    def test_recursive_aliases(self):
        self.v.register_alias('Baz', 'Roo')
        self.v.register_alias('Roo', 'baz')

    def test_unmarshall(self):
        self.v.set_default('port', 1313)
        self.v.set('name', 'Steve')

        cls = type('MyClass', (), {})
        c = self.v.unmarshall(cls)

        self.assertEqual(c.name, self.v.get('name'))
        self.assertEqual(c.port, self.v.get('port'))

        self.v.set('port', 1234)
        c = self.v.unmarshall(cls)
        self.assertEqual(c.port, self.v.get('port'))

    def test_bind_args(self):
        arg_set = argparse.ArgumentParser()

        test_values = {
            'host': 'localhost',
            'port': '6060',
            'endpoint': '/public'
        }

        for name, value in test_values.items():
            arg_set.add_argument('--' + name, default=value)

        args = arg_set.parse_known_args()
        self.v.bind_args(vars(args[0]))

        for name, value in test_values.items():
            self.assertEqual(self.v.get(name), value)

    def test_bind_arg(self):
        arg_set = argparse.ArgumentParser()
        arg_set.add_argument('--testflag', default='testing')
        args = arg_set.parse_known_args()

        self.v.bind_arg('testvalue', vars(args[0])['testflag'])

        self.assertEqual('testing', self.v.get('testvalue'))

    def test_is_set(self):
        self.v.set_config_type('yaml')
        self.v.read_config(yaml.dump(text(yaml_example)))
        self.assertTrue(self.v.is_set('clothing.jacket'))
        self.assertFalse(self.v.is_set('clothing.jackets'))
        self.assertFalse(self.v.is_set('helloworld'))
        self.v.set('helloworld', 'fubar')
        self.assertTrue(self.v.is_set('helloworld'))

    def test_dirs_search(self):
        root, config, cleanup = self._init_dirs()

        try:
            v = vyper.Vyper()
            v.set_config_name(config)
            v.set_config_type('toml')
            v.set_default('key', 'default')

            entries = os.listdir(root)
            for e in entries:
                if os.path.isdir(e):
                    v.add_config_path(e)

            v.read_in_config()

            self.assertEqual('value is ' + v._config_paths[0].name,
                             v.get('key'))
        finally:
            cleanup()

    def test_wrong_dirs_search_not_found(self):
        _, config, cleanup = self._init_dirs()

        try:
            v = vyper.Vyper()
            v.set_config_name(config)
            v.set_default('key', 'default')

            v.add_config_path('whattayoutalkingabout')
            v.add_config_path('thispathainthere')

            self.assertRaises(errors.UnsupportedConfigError, v.read_in_config)

            self.assertEqual('default', v.get('key'))
        finally:
            cleanup()

    def test_bound_case_sensitivity(self):
        self._init_yaml()
        self.assertEqual('brown', self.v.get('eyes'))

        self.v.bind_env('eYEs', 'TURTLE_EYES')
        os.environ['TURTLE_EYES'] = 'blue'

        self.assertEqual('blue', self.v.get('eyes'))

        arg_set = argparse.ArgumentParser()
        arg_set.add_argument('--eyeballs', default='green')
        args = arg_set.parse_known_args()

        self.v.bind_arg('eYEs', vars(args[0])['eyeballs'])
        self.assertEqual('green', self.v.get('eyes'))

    def test_sub(self):
        self.v.set_config_type('yaml')
        self.v.read_config(yaml.dump(text(yaml_example)))

        subv = self.v.sub('clothing')
        self.assertEqual(self.v.get('clothing.pants.size'),
                         subv.get('pants.size'))

        subv = self.v.sub('clothing.pants')
        self.assertEqual(self.v.get('clothing.pants.size'), subv.get('size'))

        subv = self.v.sub('clothing.pants.size')
        self.assertEqual(subv, None)

    def test_unmarshalling_with_aliases(self):
        self.v.set_default('Id', 1)
        self.v.set('name', 'Steve')
        self.v.set('lastname', 'Owen')

        self.v.register_alias('UserId', 'Id')
        self.v.register_alias('Firstname', 'name')
        self.v.register_alias('Surname', 'lastname')

        cls = type('MyClass', (), {})
        c = self.v.unmarshall(cls)

        self.assertEqual(c.id, 1)
        self.assertEqual(c.firstname, 'Steve')
        self.assertEqual(c.surname, 'Owen')
