import vyper
from flask import Flask

app = Flask(__name__)

v = vyper.Vyper()
v.add_config_path('.')
v.set_config_type('json')
v.read_in_config()
app.config.update(v.all_settings(uppercase_keys=True))  # Flask excepts config keys to be in uppercase


@app.route('/')
def hello():
    return app.config['ADMIN_USERNAME']

if __name__ == '__main__':
    app.run()
