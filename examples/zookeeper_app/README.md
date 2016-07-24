# ZooKeeper example

A simple example for using Vyper with [ZooKeeper](https://zookeeper.apache.org/) as the remote config system.

## Installing ZooKeeper

Follow the instructions [here](https://zookeeper.apache.org/doc/trunk/zookeeperStarted.html#ch_GettingStarted).
When ZooKeeper is installed and running, add some data to it:
```
$ zkCli -server localhost:2181
[zk: localhost:2181(CONNECTED) 6] create /config.json {}
Created /config.json
[zk: localhost:2181(CONNECTED) 9] set /config.json '{"hello": "from zookeeper!"}'
```

## Running example
```
$ git clone https://github.com/admiralobvious/vyper.git
$ cd vyper/examples/zookeeper_app
$ virtualenv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
$ python app.py
```
If everything worked, you should see the following in the terminal:
```
Hello from zookeeper!
```
