import supervisor
import microcontroller
from persisted_ram import persisted_ram
from persisted_storage import persisted_storage


class Reloader:

    def __init__(self):
        pass

    def __save(self):
        if persisted_ram.loaded:
            persisted_ram.save()
        if persisted_storage.loaded:
            persisted_storage.save()

    def reload(self):
        self.__save()
        supervisor.reload()

    def reset(self):
        self.__save()
        microcontroller.reset()


reloader = Reloader()
