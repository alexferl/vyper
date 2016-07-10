zkCli -server localhost:2181
[zk: localhost:2181(CONNECTED) 6] create /config.json {}
Created /config.json
[zk: localhost:2181(CONNECTED) 9] set /config.json '{"hello": "from zookeeper!"}'
