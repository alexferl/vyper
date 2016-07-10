from distconfig import Proxy
import pytoml as toml
import yaml

try:
    import ujson as json
except ImportError:
    import json

from . import errors, vyper

PROVIDER_TYPE = {
    'consul': 'distconfig.backends.consul.ConsulBackend',
    'etcd': 'distconfig.backends.etcd.EtcdBackend',
    'zookeeper': 'distconfig.backends.zookeeper.ZooKeeperBackend'
}


class RemoteProvider(object):
    def __init__(self, provider, client, path, config_type):
        if config_type != '' and config_type in vyper.SUPPORTED_EXTS:
            self.config_type = config_type
        else:
            raise errors.UnsupportedConfigError(config_type)

        provider = PROVIDER_TYPE.get(provider)
        proxy = Proxy.configure(provider,
                                client=client,
                                parser=self._get_parser())
        self.config = proxy.get_config(path)

        self.provider = provider
        self.client = client
        self.path = path

    def _get_parser(self):
        if self.config_type == 'json':
            return json.loads
        elif self.config_type in ['yaml', 'yml']:
            return yaml.load
        elif self.config_type == 'toml':
            return toml.loads

    def get(self):
        d = {k: v for k, v in self.config.items()}
        if self.config_type != 'toml':
            return json.dumps(d)
        else:
            return d

    def watch(self):
        # TODO: implement this
        pass
