# Consul example

A simple example for using Vyper with [Consul](https://www.consul.io/) as the remote config system.

## Installing Consul

Follow the instructions [here](https://www.consul.io/intro/getting-started/install.html).
You only need to get to `Starting the Agent`.
When Consul is installed and running, add some data to it:
```
$ curl -X PUT -d 'hello: "from consul!"' http://localhost:8500/v1/kv/config.yaml
```

## Running example
```
$ git clone https://github.com/admiralobvious/vyper.git
$ cd vyper/examples/consul/app
$ virtualenv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
$ python app.py
```
If everything worked, you should see the following in the terminal:
```
Hello from consul!
```