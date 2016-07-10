import vyper
from flask import Flask
app = Flask(__name__)

import etcd

from distconfig import Proxy

#client = client.KazooClient()
# The user must call ``KazooClient.start()`` before using this particular
# backend
#client.start()
client = etcd.Client()

proxy = Proxy.configure(
    'distconfig.backends.etcd.EtcdBackend',
    client=client,
)

v = vyper.Vyper()
#v.set_config_type('yaml')
v.add_remote_provider('etcd', client, '/config.json')
v.set_config_type('yaml')
v.read_remote_config()
v.get('key')
app.config.update(v.all_settings(uppercase_keys=True))


@app.route("/")
def hello():
    c = app.config.items()
    print(v.get('key'))
    return str(c)

if __name__ == "__main__":
    app.run()
