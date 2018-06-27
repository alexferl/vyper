# Flask example

A simple example for using Vyper with [Flask](http://flask.pocoo.org/) with command args flags support.

## Running example
```
$ git clone https://github.com/admiralobvious/vyper.git
$ cd vyper/examples/flask_flags_config_app
$ virtualenv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
$ python app.py --hello='from flask and France!'
```
In another terminal window:
```
$ curl http://localhost:5000
```
If everything worked, you should see the following in the terminal:
```
Hello from flask and France!
```
