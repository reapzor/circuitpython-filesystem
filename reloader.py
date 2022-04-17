import supervisor
from persisted_ram import persisted_ram


class Reloader:

    def __init__(self):
        pass

    def reload(self):
        if persisted_ram.loaded:
            persisted_ram.save()
        supervisor.reload()


reloader = Reloader()
