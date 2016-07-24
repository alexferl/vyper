from flask import Flask
from vyper import v

app = Flask(__name__)


def update_config():
    """Updates Flask's config."""
    return app.config.update(v.all_settings(uppercase_keys=True))

v.add_config_path('.')
v.set_config_type('json')
v.read_in_config()
update_config()
v.watch_config()
v.on_config_change(update_config)


@app.route('/')
def hello():
    return 'Hello ' + app.config['HELLO']

if __name__ == '__main__':
    app.run(use_reloader=False)
