import etcd
from flask import Flask
from vyper import v

app = Flask(__name__)
client = etcd.Client()


def update_config():
    """Updates Flask's config."""
    return app.config.update(v.all_settings(uppercase_keys=True))

v.set_config_type('json')
v.add_remote_provider('etcd', client, '/config.json')
v.read_remote_config()
update_config()
v.watch_remote_config()
v.on_remote_config_change(update_config)


@app.route('/')
def hello():
    return 'Hello ' + app.config['HELLO']

if __name__ == '__main__':
    app.run(use_reloader=False)

