from microcontroller import nvm
from _persisted_helper import load_memory, save_memory


class PersistedStorage:

    def __init__(self):
        self.loaded = False
        self._data = {}

    def load(self):
        self.loaded = True
        self._data = load_memory(nvm)

    def save(self):
        save_memory(self._data, nvm, compare_existing=True)

    @property
    def data(self):
        if not self.loaded:
            self.load()
        return self._data


persisted_storage = PersistedStorage()
