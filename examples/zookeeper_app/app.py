from kazoo import client
from vyper import v

client = client.KazooClient()
client.start()

v.set_config_type("json")
v.add_remote_provider("zookeeper", client, "/config.json")
v.read_remote_config()

print("Hello " + v.get("hello"))
