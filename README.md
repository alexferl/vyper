# Vyper [![Build Status](https://travis-ci.com/alexferl/vyper.svg?branch=master)](https://travis-ci.com/alexferl/vyper) [![codecov](https://codecov.io/gh/alexferl/vyper/branch/master/graph/badge.svg)](https://codecov.io/gh/alexferl/vyper)

Python configuration with (more) fangs! Python port of the very awesome [Viper](https://github.com/spf13/viper) for Go.

## PyPI name change
The package changed name on pypi from `vyper` to `vyper-config` on August 20th 2018.
The `vyper` name is now used by the following [project](https://github.com/ethereum/vyper).
The `vyper-config` package is available on [PyPI](https://pypi.org/project/vyper-config/).

## What is Vyper?

Vyper is a complete configuration solution for Python applications including 12 factor apps. It is designed
to work within an application, and can handle all types of configuration needs and formats. It supports:

* setting defaults
* reading from JSON, TOML, and YAML config files
* live watching and re-reading of config files (optional)
* reading from environment variables
* reading from remote config systems (etcd, Consul or ZooKeeper)
* live watching and re-reading of remote config files (optional)
* reading from command line arguments
* reading from buffer
* setting explicit values

Vyper can be thought of as a registry for all of your applications
configuration needs.

## Why Vyper?

When building a modern application, you don’t want to worry about
configuration file formats; you want to focus on building awesome software.
Vyper is here to help with that.

Vyper does the following for you:

1. Find, load, and unmarshall a configuration file in JSON, TOML, or YAML format.
2. Provide a mechanism to set default values for your different
   configuration options.
3. Provide a mechanism to set override values for options specified through
   command line arguments.
4. Provide an alias system to easily rename parameters without breaking existing
   code.
5. Make it easy to tell the difference between when a user has provided a
   command line or config file which is the same as the default.

Vyper uses the following precedence order. Each item takes precedence over the
item below it:

 * explicit call to set
 * argument
 * environment variable
 * config
 * key/value store
 * default

Vyper configuration keys are case insensitive.

## Putting Values into Vyper

### Establishing Defaults

A good configuration system will support default values. A default value is not
required for a key, but it's useful in the event that a key hasn't been set via
config file, environment variable, remote configuration or argument.

Examples:

```python
v.set_default('ContentDir', 'content')
v.set_default('LayoutDir', 'layouts')
v.set_default('Taxonomies', {'tag': 'tags', 'category': 'categories'})
```

### Reading Config Files

Vyper requires minimal configuration so it knows where to look for config files.
Vyper supports JSON, TOML and YAML files. Vyper can search multiple paths, but
currently a single Vyper instance only supports a single configuration file.
Vyper does not default to any configuration search paths leaving defaults decision
to an application.

Here is an example of how to use Vyper to search for and read a configuration file.
None of the specific paths are required, but at least one path should be provided
where a configuration file is expected.

```python
v.set_config_name('config')  # name of config file (without extension)
v.add_config_path('/etc/appname/')  # path to look for the config file in
v.add_config_path('$HOME/.appname')  # call multiple times to add many search paths
v.add_config_path('.')  # optionally look for config in the working directory
v.read_in_config()  # Find and read the config file
```

### Watching and re-reading config files

Vyper supports the ability to have your application live read a config file while running.

Gone are the days of needing to restart a server to have a config take effect,
vyper powered applications can read an update to a config file while running and
not miss a beat.

Simply tell the Vyper instance to watch_config().
Optionally you can provide a function for Vyper to run each time a change occurs.

**Make sure you add all of the config_paths prior to calling `watch_config()`**

```python
v.watch_config()
def f():
    print('Config file changed')
v.on_config_change(f)
```

### Reading Config from buffer

Vyper pre-defines many configuration sources such as files, environment
variables, arguments, and remote K/V store, but you are not bound to them. You can
also implement your own required configuration source and feed it to Vyper.

```python
v.set_config_type('yaml')  # or v.set_config_type('YAML')

# any approach to require this configuration into your program.
yaml_example = '''
Hacker: true
name: steve
hobbies:
- skateboarding
- snowboarding
- go
clothing:
  jacket: leather
  trousers: denim
age: 35
eyes : brown
beard: true
'''

v.read_config(yaml_example)

v.get('name')  # this would be 'steve'
```

### Setting Overrides

These could be from a command line argument, or from your own application logic.

```python
v.set('Verbose', True)
v.set('LogFile', log_file)
```

### Registering and Using Aliases

Aliases permit a single value to be referenced by multiple keys

```python
v.register_alias('loud', 'Verbose')

v.set('verbose', True)  # same result as next line
v.set('loud', True)  # same result as prior line

v.get_bool('loud')  # True
v.get_bool('verbose')  # True
```

### Working with Environment Variables

Vyper has full support for environment variables. This enables 12 factor
applications out of the box. There are four methods that exist to aid working
with ENV:

 * `automatic_env()`
 * `bind_env(string)`
 * `set_env_prefix(string)`
 * `set_env_replacer(string)`

_When working with ENV variables, it’s important to recognize that Vyper
treats ENV variables as case sensitive._

Vyper provides a mechanism to try to ensure that ENV variables are unique. By
using `set_env_prefix()`, you can tell Vyper to use add a prefix while reading from
the environment variables. Both `bind_env()` and `automatic_env()` will use this
prefix.

`bind_env()` takes one or two parameters. The first parameter is the key name, the
second is the name of the environment variable. The name of the environment
variable is case sensitive. If the ENV variable name is not provided, then
Vyper will automatically assume that the key name matches the ENV variable name,
but the ENV variable is IN ALL CAPS. When you explicitly provide the ENV
variable name, it **does not** automatically add the prefix.

One important thing to recognize when working with ENV variables is that the
value will be read each time it is accessed. Vyper does not fix the value when
the `bind_env()` is called.

`automatic_env()` is a powerful helper especially when combined with
`set_env_prefix()`. When called, Vyper will check for an environment variable any
time a `v.get()` request is made. It will apply the following rules. It will
check for a environment variable with a name matching the key uppercased and
prefixed with the `env_prefix()` if set.

`set_env_replacer()` allows you to use a `str` object to rewrite Env
keys to an extent. This is useful if you want to use `-` or something in your
`get()` calls, but want your environmental variables to use `_` delimiters. An
example of using it can be found in `tests/test_vyper.py`.

#### Env example

```python
v.set_env_prefix('spf')  # will be uppercased automatically
v.bind_env('id')

os.environ['SPF_ID'] = '13'  # typically done outside of the app

id = v.get('id')  # 13
```

### Working with command line arguments

Vyper has the ability to bind to command line arguments.
Specifically, Vyper supports `argparse`.
See [doc](docs.python.org/3.7/library/argparse.html#argparse.ArgumentParser)
for more details.

The values are set when the binding method is called.

As it deals with command line arguments, the `bind_args()` method needs to be called passing
an instance of argparse.ArgumentParser(). The method also sets defaults based on what you pass
via `add_argument()` `default` parameter.

Note: If you don't specify a default, the values will be set to `None`.

```python
p = argparse.ArgumentParser(description="Application settings")
p.add_argument('--app-name', type=str, help='Application and process name')
p.add_argument('--env', type=str, choices=['dev', 'pre-prod', 'prod'], help='Application env')
p.add_argument('--port', type=int, default=5000, help='Application port')
p.add_argument('--password', type=str, help='Application password')
v.bind_args(p)

# "your_app.py", "--app-name=cmd-app", "--env=prod"

app_name = v.get('app_name')  # 'cmd-app'
env = v.get('env')            # 'prod'
port = v.get('port')          # 5000
password = v.get('password')  # `None`
```

## Getting Values From Vyper

In Vyper, there are a few ways to get a value depending on the value's type.
The following functions and methods exist:

 * `get(key)`
 * `get_bool(key) : bool`
 * `get_float(key) : float`
 * `get_int(key) : int`
 * `get_string(key) : str`
 * `is_set(key) : bool`

One important thing to recognize is that each get function will return a zero
value if it’s not found. To check if a given key exists, the `is_set()` method
has been provided.

Example:
```python
v.get_string('logfile')  # case-insensitive Setting & Getting
if v.get_bool('verbose'):
    print('verbose enabled')
```
### Accessing nested keys

The accessor methods also accept formatted paths to deeply nested keys. For
example, if the following JSON file is loaded:

```json
{
    "host": {
        "address": "localhost",
        "port": 5799
    },
    "datastore": {
        "metric": {
            "host": "127.0.0.1",
            "port": 3099
        },
        "warehouse": {
            "host": "198.0.0.1",
            "port": 2112
        }
    }
}

```

Vyper can access a nested field by passing a `.` delimited path of keys:

```python
v.get_string('datastore.metric.host')  # returns '127.0.0.1'
```

This obeys the precedence rules established above; the search for the root key
(in this example, `datastore`) will cascade through the remaining configuration
registries until found. The search for the sub-keys (`metric` and `host`),
however, will not.

For example, if the `metric` key was not defined in the configuration loaded
from file, but was defined in the defaults, Vyper would return the zero value.

On the other hand, if the primary key was not defined, Vyper would go through
the remaining registries looking for it.

Lastly, if there exists a key that matches the delimited key path, its value
will be returned instead. E.g.

```json
{
    "datastore.metric.host": "0.0.0.0",
    "host": {
        "address": "localhost",
        "port": 5799
    },
    "datastore": {
        "metric": {
            "host": "127.0.0.1",
            "port": 3099
        },
        "warehouse": {
            "host": "198.0.0.1",
            "port": 2112
        }
    }
}

v.get_string('datastore.metric.host')  # returns '0.0.0.0'
```

## Vyper or Vypers?

Vyper comes ready to use out of the box. There is no configuration or
initialization needed to begin using Vyper. Since most applications will want
to use a single central repository for their configuration, the vyper package
provides this. It is similar to a singleton.

In all of the examples above, they demonstrate using vyper in it's singleton
style approach.
