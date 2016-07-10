from distconfig import Proxy

try:
    import ujson as json
except ImportError:
    import json

PROVIDER_TYPE = {
    'consul': 'distconfig.backends.consul.ConsulBackend',
    'etcd': 'distconfig.backends.etcd.EtcdBackend',
    'zookeeper': 'distconfig.backends.zookeeper.ZooKeeperBackend'
}


class RemoteProvider(object):
    def __init__(self, provider, client, path):
        provider = PROVIDER_TYPE.get(provider)
        proxy = Proxy.configure(provider, client=client)
        self.config = proxy.get_config(path)

        self.provider = provider
        self.client = client
        self.path = path

    def get(self):
        d = {k: v for k, v in self.config.items()}
        return json.dumps(d)

    def watch(self):
        # TODO: implement this
        pass
