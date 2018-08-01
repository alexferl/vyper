import argparse


class FlagsProvider:
    def __init__(self):
        self.argument_parser = argparse.ArgumentParser(
            description="Command line params")

    def add_argument(self, flag, *args, **kwargs):
        # Make sure to remove the default value if set
        if 'default' in kwargs:
            kwargs.pop('default', None)
        self.argument_parser.add_argument(
            flag,
            **kwargs
        )

    def get_flags(self, args):
        args = args or []
        return vars(self.argument_parser.parse_args(
            args[1:] if len(args) else []))
