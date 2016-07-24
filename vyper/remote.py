from __future__ import absolute_import

from distconfig import Proxy
import pytoml as toml
import yaml

try:
    import ujson as json
except ImportError:
    import json

from . import constants, errors

PROVIDER_TYPE = {
    'consul': 'distconfig.backends.consul.ConsulBackend',
    'etcd': 'distconfig.backends.etcd.EtcdBackend',
    'zookeeper': 'distconfig.backends.zookeeper.ZooKeeperBackend'
}


class RemoteProvider(object):
    def __init__(self, provider, client, path, v):
        self.v = v
        config_type = self.v._config_type
        if config_type != '' and config_type in constants.SUPPORTED_EXTS:
            self.config_type = config_type
        else:
            raise errors.UnsupportedConfigError(config_type)

        provider = PROVIDER_TYPE.get(provider)
        self.proxy = Proxy.configure(provider,
                                     client=client,
                                     parser=self._get_parser())

        self.config = self.proxy.get_config(path)

    @property
    def provider(self):
        return self.provider

    @property
    def client(self):
        return self.client

    @property
    def path(self):
        return self.path

    def _get_parser(self):
        if self.config_type == 'json':
            return json.loads
        elif self.config_type in ['yaml', 'yml']:
            return yaml.load
        elif self.config_type == 'toml':
            return toml.loads

    def get(self):
        d = {}
        for k, v in self.config.items():
            d[k] = v

        if self.config_type != 'toml':
            return json.dumps(d)
        else:
            return d

    def add_listener(self, cb=None):
        if cb is not None:
            self.proxy.backend.add_listener(cb)
        else:
            self.proxy.backend.add_listener(self._update_kvstore)

    def _update_kvstore(self, e):
        self.v._kvstore = e

