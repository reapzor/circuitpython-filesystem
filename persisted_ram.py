from alarm import sleep_memory
from _persisted_helper import load_memory, save_memory


class PersistedRam:

    def __init__(self):
        self.loaded = False
        self._data = {}

    def load(self):
        self.loaded = True
        self._data = load_memory(sleep_memory)

    def save(self):
        save_memory(self._data, sleep_memory)

    @property
    def data(self):
        if not self.loaded:
            self.load()
        return self._data


persisted_ram = PersistedRam()
