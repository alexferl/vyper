# Flask example

A simple example for using Vyper with [Flask](http://flask.pocoo.org/) with live config watching and reloading.

## Running example
```
$ git clone https://github.com/admiralobvious/vyper.git
$ cd vyper/examples/flask_config_reload_app
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
Hello from flask!
```
To test that the config file is being watched and reloaded,
just change the `hello` key value to `world!` in config.json and if you
`$ curl http://localhost:5000` you should now see the following in the terminal:
```
Hello world!
```
