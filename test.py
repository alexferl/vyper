from kazoo import client
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

print(client.host)
print(dir(proxy))
print(dir(proxy.backend))

# config is a read only mapping-like object.
config = proxy.get_config('/config.json')

print(config)

print config['key']
