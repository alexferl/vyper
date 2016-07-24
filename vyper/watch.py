import os
import threading
import time

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class CustomHandler(FileSystemEventHandler):
    current_event = None

    def process(self, event):
        if event.is_directory is not True:
            self.current_event = event

    def on_modified(self, event):
        self.process(event)

    def on_created(self, event):
        self.process(event)

    def get_event(self):
        current_event = self.current_event
        self.current_event = None
        return current_event


class BaseWatcher(object):
    def __init__(self, config_file, v):
        self.handler = CustomHandler()
        self.config_file = config_file
        self.directory = os.path.dirname(os.path.realpath(config_file))
        self.v = v

    def watch_path(self):
        observer = Observer()
        observer.schedule(self.handler, self.directory)
        observer.start()
        try:
            while True:
                event = self.event
                if event is not None and event.src_path == self.config_file:
                    self.v.read_in_config()
                    if self.v._on_config_change is not None:
                        self.v._on_config_change()
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()

    @property
    def event(self):
        return self.handler.get_event()


class ThreadWatcher(BaseWatcher):
    def __init__(self, config_file, v):
        super(ThreadWatcher, self).__init__(config_file, v)
        self.t = threading.Thread(target=self.watch_path)
        self.t.daemon = True

    def start(self):
        self.t.start()


def get_watcher(config_file, v):
    return ThreadWatcher(config_file, v)
