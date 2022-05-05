import argparse
import json
import os
import tempfile
import unittest

import toml
import vyper
import yaml
from builtins import str as text
from vyper import errors

try:
    FileNotFoundError
except NameError:
    FileNotFoundError = OSError

yaml_duplicate_in_nested = """
sweet:
  home:
    alabama: yeap
  job:
    alabama: noway
"""

yaml_example = """Hacker: true
name: steve
pets:
    count: 0
    names: []
    preferred_veterinarian: ''
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
beard: true"""

toml_example = """title = "TOML Example"
[owner]
organization = "MongoDB"
Bio = "MongoDB Chief Developer Advocate & Hacker at Large"
dob = 1979-05-27T07:32:00Z # First class dates? Why not?"""

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
            {"type": "Devil's Food"},
        ]
    },
    "icings": {
        "regular": {"types": ["plain", "glazed"]},
        "premium": {"types": ["passionfruit", "chocolate"]},
    },
    "ingredients": {
        "batter": {
            "Regular": {
                "eggs": 2,
            }
        }
    },
}

json_camel_case_example = {
    "Id": "0001",
    "Type": "donut",
    "Name": "Cake",
    "PPU": 0.55,
    "Batters": {
        "Batter": [
            {"Type": "Regular"},
            {"Type": "Chocolate"},
            {"Type": "Blueberry"},
            {"Type": "Devil's Food"},
        ],
    },
    "Prices": [
        "0.42",
        "0.82",
    ],
    "Icings": {
        "Regular": {"Types": ["plain", "glazed"]},
        "Premium": {"Types": ["passionfruit", "chocolate"]},
    },
}


class TestVyper(unittest.TestCase):
    def setUp(self):
        self.v = vyper.Vyper()
        self.v.parse_argv_disabled = True

    def _init_configs(self):
        self.v.set_config_type("yaml")
        r = yaml.safe_dump(text(yaml_example))
        self.v._unmarshall_reader(r, self.v._config)

        self.v.set_config_type("json")
        r = json.dumps(json_example)
        self.v._unmarshall_reader(r, self.v._config)

        self.v.set_config_type("toml")
        r = toml.loads(toml_example)
        self.v._unmarshall_reader(r, self.v._config)

    def _init_yaml(self):
        self.v.set_config_type("yaml")
        r = yaml.safe_dump(yaml_example)
        self.v._unmarshall_reader(r, self.v._config)

    def _init_json(self, fixture=None):
        self.v.set_config_type("json")
        r = json.dumps(fixture or json_example)
        self.v._unmarshall_reader(r, self.v._config)

    def _init_toml(self):
        self.v.set_config_type("toml")
        r = toml.loads(toml_example)
        self.v._unmarshall_reader(r, self.v._config)

    def _init_dirs(self):
        test_dirs = ["a a", "b", "D_"]
        config = "improbable"
        root = tempfile.mkdtemp()

        def cleanup():
            try:
                os.removedirs(root)
            except (FileNotFoundError, OSError):
                pass

        os.chdir(root)

        for dir_ in test_dirs:
            os.mkdir(dir_, 0o0750)

            f = "{0}.toml".format(config)
            flags = os.O_WRONLY | os.O_CREAT
            rel_path = "{0}/{1}".format(dir_, f)
            abs_file_path = os.path.join(root, rel_path)
            with os.fdopen(os.open(abs_file_path, flags, 0o0640), "w") as fp:
                fp.write('key = "value is {0}"\n'.format(dir_))

        return root, config, cleanup

    def test_basics(self):
        self.v.set_config_file("/tmp/config.yaml")
        self.assertEqual("/tmp/config.yaml", self.v._get_config_file())

    def test_default(self):
        self.v.set_default("age", 45)
        self.assertEqual(45, self.v.get("age"))

        self.v.set_default("clothing.jacket", "slacks")
        self.assertEqual("slacks", self.v.get("clothing.jacket"))

    def test_unmarshalling(self):
        self.v.set_config_type("yaml")
        r = yaml.safe_dump(yaml_example)
        self.v._unmarshall_reader(r, self.v._config)
        self.assertTrue(self.v.in_config("name"))
        self.assertFalse(self.v.in_config("state"))
        self.assertEqual("steve", self.v.get("name"))
        self.assertEqual(35, self.v.get("age"))

    def test_yaml_duplication_nested(self):
        self.v.set_config_type("yaml")
        r = yaml.safe_dump(yaml_duplicate_in_nested)
        self.v._unmarshall_reader(r, self.v._config)
        self.assertEqual("yeap", self.v.get("sweet.home.alabama"))
        self.assertEqual("noway", self.v.get("sweet.job.alabama"))

    def test_override(self):
        self.v.set("age", 40)
        self.assertEqual(40, self.v.get("age"))

    def test_bind_args(self):
        arg_set = argparse.ArgumentParser()

        test_values = {"host": "localhost", "port": "6060", "endpoint": "/public"}

        for name, value in test_values.items():
            arg_set.add_argument("--" + name, default=value)

        self.v.bind_args(arg_set)

        for name, value in test_values.items():
            self.assertEqual(self.v.get(name), value)

    def test_bind_arg(self):
        arg_set = argparse.ArgumentParser()
        arg_set.add_argument("--testflag", default="testing")
        args = arg_set.parse_known_args()

        self.v.bind_arg("testvalue", vars(args[0])["testflag"])

        self.assertEqual("testing", self.v.get("testvalue"))

    def test_args_with_value(self):
        fp = argparse.ArgumentParser()
        fp.add_argument("--app-name", type=str, help="Application and process name")
        fp.add_argument(
            "--env",
            type=str,
            choices=["dev", "pre-prod", "prod"],
            help="Application env (default %(default)s)",
        )
        self.v._bind_parser_values(fp, ["--app-name=cmd-app", "--env=prod"])
        self.assertEqual("cmd-app", self.v.get("app_name"))
        self.assertEqual("prod", self.v.get("env"))

    def test_args_with_bad_value(self):
        p = argparse.ArgumentParser()
        p.add_argument("--app-name", type=str, help="Application and process name")
        p.add_argument(
            "--env",
            type=str,
            choices=["dev", "pre-prod", "prod"],
            help="Application env",
        )
        # Setting a value flag which is not in the choices list should raise a system error
        # Help will be shown in cmd to see how to use the flag.
        with self.assertRaises(SystemExit):
            self.v._bind_parser_values(
                p, ["--app-name=cmd-app", "--env=not-in-the-list"]
            )

    def test_args_override(self):
        # Yaml config
        self.v.set_config_type("yaml")
        r = yaml.safe_dump("yaml_param: from_yaml")
        self.v._unmarshall_reader(r, self.v._config)

        # Overrides
        self.v.set("overrides_param", "from_overrides")
        self.assertEqual("from_overrides", self.v.get("overrides_param"))

        # Default
        self.v.set_default("default_param", "from_default")
        self.assertEqual("from_default", self.v.get("default_param"))

        p = argparse.ArgumentParser()
        p.add_argument("--yaml-param", type=str)
        p.add_argument("--overrides-param", type=str, default="override_arg")
        p.add_argument("--default-param", type=str)
        p.add_argument("--default-param-arg", type=str, default="default_from_arg")

        self.v._bind_parser_values(
            p, ["--yaml-param=from_flags", "--default-param=from_flags"]
        )

        self.assertEqual("from_flags", self.v.get("yaml_param"))
        self.assertEqual("from_overrides", self.v.get("overrides_param"))
        self.assertEqual("from_flags", self.v.get("default_param"))
        self.assertEqual("default_from_arg", self.v.get("default_param_arg"))

    def test_default_post(self):
        self.assertNotEqual("NYC", self.v.get("state"))
        self.v.set_default("state", "NYC")
        self.assertEqual("NYC", self.v.get("state"))

    def test_nested_default_post(self):
        self._init_yaml()
        self.assertTrue(self.v.is_set("clothing"))
        self.assertFalse(self.v.is_set("clothing.gloves"))
        self.assertNotEqual("leather", self.v.get("clothing.gloves"))
        self.v.set_default("clothing.gloves", "leather")
        self.assertEqual("leather", self.v.get("clothing.gloves"))

    def test_aliases(self):
        self.v.register_alias("years", "age")
        self.v.set("years", 45)
        self.assertEqual(45, self.v.get("age"))

    def test_alias_in_config_file(self):
        # the config file specifies "beard". If we make this an alias for
        # "hasbeard", we still want the old config file to work with beard.
        self._init_yaml()
        self.v.register_alias("hasbeard", "beard")
        self.assertEqual(True, self.v.get("hasbeard"))
        self.assertEqual(True, self.v.get("beard"))
        self.v.set("hasbeard", False)
        self.assertEqual(False, self.v.get("hasbeard"))
        self.assertEqual(False, self.v.get("beard"))

    def test_yaml(self):
        self._init_yaml()
        self.assertEqual("steve", self.v.get("name"))

    def test_json(self):
        self._init_json()
        self.assertEqual("0001", self.v.get("id"))

    def test_toml(self):
        self._init_toml()
        self.assertEqual("TOML Example", self.v.get("title"))

    def test_env_override_default_subclass(self):
        os.environ["CLASS.KEY2"] = "newval2"

        self.v.set_default("class.key1", "val1")
        self.v.set_default("class.key2", "val2")
        self.v.set_default("class.key3", "val3")

        self.v.bind_env("class.key1")
        self.v.bind_env("class.key2")
        self.v.bind_env("class.key3")

        self.assertEqual("val1", self.v.get("class.key1"))

    def test_env(self):
        self._init_json()

        self.v.bind_env("id")
        self.v.bind_env("f", "FOOD")
        self.v.bind_env("icings.premium.types", "PREMIUM_ICINGS")

        os.environ["ID"] = "13"
        os.environ["FOOD"] = "apple"
        os.environ["NAME"] = "crunk"
        os.environ["PREMIUM_ICINGS"] = "Regular,Chocolate"

        self.assertEqual("13", self.v.get("id"))
        self.assertEqual("apple", self.v.get("f"))
        self.assertEqual("Cake", self.v.get("name"))

        self.assertEqual("Regular,Chocolate", self.v.get("icings.premium.types"))
        self.assertEqual("Regular,Chocolate", self.v.get("icings")["premium"]["types"])
        self.assertEqual("Regular,Chocolate", self.v.get("icings.premium")["types"])

        self.v.automatic_env()

        self.assertEqual("crunk", self.v.get("name"))

    def test_auto_env(self):
        self.v.automatic_env()
        os.environ["FOO_BAR"] = "13"
        self.assertEqual("13", self.v.get("foo_bar"))

    def test_auto_env_with_prefix(self):
        self.v.automatic_env()
        self.v.set_env_prefix("Baz")
        os.environ["BAZ_BAR"] = "13"
        self.assertEqual("13", self.v.get("bar"))

    def test_set_env_replacer(self):
        self.v.automatic_env()
        os.environ["REFRESH_INTERVAL"] = "30s"

        self.v.set_env_key_replacer("-", "_")

        self.assertEqual("30s", self.v.get("refresh-interval"))

    def test_all_keys(self):
        self._init_json()
        self.v.set("setkey", "setvalue")
        self.v.set_default("defaultkey", "defaultvalue")
        all_keys = [
            "batters",
            "name",
            "icings",
            "ppu",
            "type",
            "id",
            "setkey",
            "defaultkey",
            "ingredients",
        ]
        self.assertSetEqual(set(self.v.all_keys()), set(all_keys))

    def test_case_insensitive(self):
        self.v.set("Title", "Checking Case")
        self.assertEqual("Checking Case", self.v.get("tItle"))

        self._init_json(fixture=json_camel_case_example)
        self.assertEqual("0001", self.v.get("Id"))
        self.assertEqual(
            {
                "Batter": [
                    {"Type": "Regular"},
                    {"Type": "Chocolate"},
                    {"Type": "Blueberry"},
                    {"Type": "Devil's Food"},
                ],
            },
            self.v.get("batters"),
        )
        self.assertEqual(
            [
                "0.42",
                "0.82",
            ],
            self.v.get("prices"),
        )

    def test_aliases_of_aliases(self):
        self.v.register_alias("Foo", "Bar")
        self.v.register_alias("Bar", "Title")
        self.v.set("Foo", "Checking Case")

        self.assertEqual("Checking Case", self.v.get("Bar"))

    def test_recursive_aliases(self):
        self.v.register_alias("Baz", "Roo")
        self.v.register_alias("Roo", "baz")

    def test_unmarshall(self):
        self.v.set_default("port", 1313)
        self.v.set("name", "Steve")

        cls = type("MyClass", (), {})
        c = self.v.unmarshall(cls)

        self.assertEqual(c.name, self.v.get("name"))
        self.assertEqual(c.port, self.v.get("port"))

        self.v.set("port", 1234)
        c = self.v.unmarshall(cls)
        self.assertEqual(c.port, self.v.get("port"))

    def test_is_set(self):
        self.v.set_config_type("yaml")
        self.v.read_config(yaml.safe_dump(text(yaml_example)))
        self.assertTrue(self.v.is_set("pets.count"))
        self.assertTrue(self.v.is_set("pets.names"))
        self.assertTrue(self.v.is_set("pets.preferred_veterinarian"))
        self.assertTrue(self.v.is_set("clothing.jacket"))
        self.assertFalse(self.v.is_set("clothing.jackets"))
        self.assertFalse(self.v.is_set("helloworld"))
        self.v.set("helloworld", "fubar")
        self.assertTrue(self.v.is_set("helloworld"))

    def test_dirs_search(self):
        root, config, cleanup = self._init_dirs()

        try:
            v = vyper.Vyper()
            v.set_config_name(config)
            v.set_config_type("toml")
            v.set_default("key", "default")

            entries = os.listdir(root)
            for e in entries:
                if os.path.isdir(e):
                    v.add_config_path(e)

            v.read_in_config()

            self.assertEqual("value is " + v._config_paths[0].name, v.get_string("key"))
        finally:
            cleanup()

    def test_wrong_dirs_search_not_found(self):
        _, config, cleanup = self._init_dirs()

        try:
            v = vyper.Vyper()
            v.set_config_name(config)
            v.set_default("key", "default")

            v.add_config_path("whattayoutalkingabout")
            v.add_config_path("thispathainthere")

            self.assertRaises(errors.UnsupportedConfigError, v.read_in_config)

            self.assertEqual("default", v.get_string("key"))
        finally:
            cleanup()

    def test_bound_case_sensitivity(self):
        self._init_yaml()
        self.assertEqual("brown", self.v.get("eyes"))

        self.v.bind_env("eYEs", "TURTLE_EYES")
        os.environ["TURTLE_EYES"] = "blue"

        self.assertEqual("blue", self.v.get("eyes"))

        arg_set = argparse.ArgumentParser()
        arg_set.add_argument("--eyeballs", default="green")
        args = arg_set.parse_known_args()

        self.v.bind_arg("eYEs", vars(args[0])["eyeballs"])
        self.assertEqual("green", self.v.get("eyes"))

    def test_complex_bound_case_sensitivity(self):
        self._init_json(fixture=json_camel_case_example)
        self.assertEqual(["plain", "glazed"], self.v.get("Icings.Regular.Types"))

        self.v.bind_env("IcIngs.ReGular.TyPes", "REGULAR_ICING")
        self.v.bind_env("IcIngs.Premium", "PREMIUM_ICING")
        os.environ["REGULAR_ICING"] = "chocolate"
        os.environ["PREMIUM_ICING"] = "Sold Out"

        self.assertEqual("chocolate", self.v.get("Icings.Regular.Types"))
        self.assertEqual("Sold Out", self.v.get("Icings.Premium"))
        self.assertEqual("chocolate", self.v.get("Icings.Regular")["Types"])

        icings = self.v.get("icings")
        self.assertEqual("Sold Out", icings["Premium"])
        self.assertEqual({"Types": "chocolate"}, icings["Regular"])

    def test_sub(self):
        self.v.set_config_type("yaml")
        self.v.read_config(yaml.safe_dump(text(yaml_example)))

        subv = self.v.sub("clothing")
        self.assertEqual(self.v.get("clothing.pants.size"), subv.get("pants.size"))

        subv = self.v.sub("clothing.pants")
        self.assertEqual(self.v.get("clothing.pants.size"), subv.get("size"))

        subv = self.v.sub("clothing.pants.size")
        self.assertEqual(subv, None)

    def test_unmarshalling_with_aliases(self):
        self.v.set_default("Id", 1)
        self.v.set("name", "Steve")
        self.v.set("lastname", "Owen")

        self.v.register_alias("UserId", "Id")
        self.v.register_alias("Firstname", "name")
        self.v.register_alias("Surname", "lastname")

        cls = type("MyClass", (), {})
        c = self.v.unmarshall(cls)

        self.assertEqual(c.id, 1)
        self.assertEqual(c.firstname, "Steve")
        self.assertEqual(c.surname, "Owen")

    def test_get_bool(self):
        self.v.set("mykey", "FALSE")
        self.assertEqual(self.v.get_bool("mykey"), False)

        self.v.set("mykey", "fAlSe")
        self.assertEqual(self.v.get_bool("mykey"), False)

        # make sure we don't try to .lower() non-strings
        self.v.set("myintkey", 3)
        self.assertEqual(self.v.get_bool("myintkey"), True)

        self.v.set("myfloatkey", 3.14159)
        self.assertEqual(self.v.get_bool("myfloatkey"), True)

    def test_merge_config(self):
        x = "a: abc"
        y = "b: xyz"
        self.v.set_config_type("yaml")

        self.v.read_config(yaml.safe_dump(text(x)))
        self.assertEqual(self.v.get("a"), "abc")

        self.v.merge_config(yaml.safe_dump(text(y)))
        self.assertEqual(self.v.get("a"), "abc")
        self.assertEqual(self.v.get("b"), "xyz")

    def test_merge_overwrite_key(self):
        x = "a: abc"
        y = "a: xyz"
        self.v.set_config_type("yaml")

        self.v.read_config(yaml.safe_dump(text(x)))
        self.assertEqual(self.v.get("a"), "abc")

        self.v.merge_config(yaml.safe_dump(text(y)))
        self.assertEqual(self.v.get("a"), "xyz")

    def test_merge_recurse_missing_source_key(self):
        x = "a: abc"
        y = """a: xyz
b:
  c: def"""
        self.v.set_config_type("yaml")

        self.v.read_config(yaml.safe_dump(text(x)))
        self.assertEqual(self.v.get("a"), "abc")

        self.v.merge_config(yaml.safe_dump(text(y)))
        self.assertEqual(self.v.get("a"), "xyz")
        self.assertEqual(self.v.get("b.c"), "def")

    def test_merge_recurse_missing_destination_key(self):
        x = """a: abc
b:
  c: xyz"""
        y = "a: xyz"
        self.v.set_config_type("yaml")

        self.v.read_config(yaml.safe_dump(text(x)))
        self.assertEqual(self.v.get("a"), "abc")

        self.v.merge_config(yaml.safe_dump(text(y)))
        self.assertEqual(self.v.get("a"), "xyz")
        self.assertEqual(self.v.get("b.c"), "xyz")

    def test_not_found(self):
        not_found_key = "not.found.key"
        self.assertEqual(self.v.get(not_found_key), None)
        self.assertEqual(self.v.get_string(not_found_key), "")
        self.assertEqual(self.v.get_int(not_found_key), 0)
        self.assertEqual(self.v.get_float(not_found_key), 0.0)
        self.assertEqual(self.v.get_bool(not_found_key), False)

    def test_nested_keys_with_environment_variables(self):
        os.environ["ENV_PREFIX_NAME"] = "john"
        os.environ["ENV_PREFIX_CLOTHING_PANTS_SIZE"] = "small"

        self._init_yaml()
        self.v.set_env_prefix("env_prefix")
        self.v.automatic_env()

        self.assertEqual("small", self.v.get("clothing.pants.size"))
        self.assertEqual(35, self.v.get("age"))
        self.assertEqual("john", self.v.get("name"))

    def test_nested_defaults_same_as_config(self):
        self._init_json()
        self.v.set_default(
            "ingredients",
            {
                "batter": {
                    "Regular": {
                        "milk": "raw",
                    }
                }
            },
        )

        self.v.debug()

        self.assertEqual("raw", self.v.get("ingredients.batter.Regular.milk"))
