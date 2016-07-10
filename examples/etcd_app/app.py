import etcd
import vyper

client = etcd.Client()

v = vyper.Vyper()
v.set_config_type('toml')
v.add_remote_provider('etcd', client, '/config.toml')
v.read_remote_config()

print('Hello ' + v.get('hello'))
