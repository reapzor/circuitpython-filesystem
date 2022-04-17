import supervisor
from persisted_ram import persisted_ram
from persisted_storage import persisted_storage


class Reloader:

    def __init__(self):
        pass

    def reload(self):
        if persisted_ram.loaded:
            persisted_ram.save()
        if persisted_storage.loaded:
            persisted_storage.save()
        supervisor.reload()


reloader = Reloader()
