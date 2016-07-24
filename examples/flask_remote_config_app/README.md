# Flask example

A simple example for using Vyper with [Flask](http://flask.pocoo.org/) and [etcd](https://coreos.com/etcd/docs/latest/)
with live remote config watching and reloading.

## Installing etcd

Follow the instructions [here](https://github.com/coreos/etcd/#getting-started).
When etcd is installed and running, add some data to it:
```
$ etcdctl set /config.json '{"hello": "from flask and etcd!"}'
```

## Running example
```
$ git clone https://github.com/admiralobvious/vyper.git
$ cd vyper/examples/flask_remote_config_app
$ virtualenv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
$ python app.py
```
In another terminal window:
```
$ curl http://localhost:5000
```
If everything worked, you should see the following in the terminal:
```
Hello from flask and etcd!
```
To test that the remote config file is being watched and reloaded,
just change the value is etcd by running:
```
$ etcdctl set /config.json '{"hello": "world!"}'
```
and if you `$ curl http://localhost:5000` you should now see the following in the terminal:
```
Hello world!
```
