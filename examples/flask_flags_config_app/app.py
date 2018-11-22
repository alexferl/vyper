import sys
from flask import Flask
from vyper import FlagsProvider, v

app = Flask(__name__)


def update_config():
    """Updates Flask's config."""
    return app.config.update(v.all_settings(uppercase_keys=True))


fp = FlagsProvider()
fp.add_argument("--hello",
                type=str,
                help="From where to say hello (default %(default)s)")
v.bind_flags(fp, sys.argv)
update_config()
v.watch_config()
v.on_config_change(update_config)


@app.route("/")
def hello():
    return "Hello " + app.config["HELLO"]


if __name__ == "__main__":
    app.run(use_reloader=False)
