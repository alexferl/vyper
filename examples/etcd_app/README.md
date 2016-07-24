# etcd example

A simple example for using Vyper with [etcd](https://coreos.com/etcd/docs/latest/) as the remote config system.

## Installing etcd

Follow the instructions [here](https://github.com/coreos/etcd/#getting-started).
When etcd is installed and running, add some data to it:
```
$ etcdctl set /config.toml 'hello = "from etcd!"'
```

## Running example
```
$ git clone https://github.com/admiralobvious/vyper.git
$ cd vyper/examples/etcd_app
$ virtualenv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
$ python app.py
```
If everything worked, you should see the following in the terminal:
```
Hello from etcd!
```
