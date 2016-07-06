class UnsupportedConfigError(Exception):
    """Denotes encountering an unsupported configuration file type."""


class UnsupportedRemoteProviderError(Exception):
    """Denotes encountering an unsupported remote provider.
    Currently only etcd and Consul are supported.
    """


class RemoteConfigError(Exception):
    """Denotes encountering an error while trying to
    pull the configuration from the remote provider.
    """


class ConfigFileNotFoundError(Exception):
    """Denotes failing to find configuration file"""
