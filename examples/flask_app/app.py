import vyper
from flask import Flask
app = Flask(__name__)
v = vyper.Vyper()
#v.set_config_type('yaml')
v.add_config_path('.')
v.read_in_config()
app.config.update(v.all_settings(uppercase_keys=True))


@app.route("/")
def hello():
    c = app.config.items()
    return str(c)

if __name__ == "__main__":
    app.run()
