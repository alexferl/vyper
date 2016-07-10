import consul
import vyper

client = consul.Consul()

v = vyper.Vyper()
v.set_config_type('yaml')
v.add_remote_provider('consul', client, 'config.yaml')
v.read_remote_config()

print('Hello ' + v.get('hello'))
