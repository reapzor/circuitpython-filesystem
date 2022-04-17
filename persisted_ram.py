from alarm import sleep_memory
import json


class PersistedRam:

    def __init__(self):
        self.loaded = False
        self._memory = {}
        self.magic_number = 1337
        self.max_size = 4096
        self.max_buffer_size = self.max_size - 4

    def load(self):
        self.loaded = True
        test_magic_number_bytes = sleep_memory[0:2]
        test_magic_number = int.from_bytes(test_magic_number_bytes, "big")
        if test_magic_number != self.magic_number:
            self._memory = {}
            return
        memory_size_bytes = sleep_memory[2:4]
        memory_size = int.from_bytes(memory_size_bytes, "big")
        if memory_size > self.max_buffer_size:
            print("memory_size corrupted. Persisted ram reset.")
            self._memory = {}
            return
        persisted_ram_bytes = sleep_memory[4:(4 + memory_size)]
        try:
            persisted_ram_string = persisted_ram_bytes.decode()
            persisted_ram_dict = json.loads(persisted_ram_string)
            self._memory = persisted_ram_dict
        except ValueError:
            print("persisted_ram_bytes/string corrupted. Persisted ram reset.")
            self._memory = {}
            return

    def save(self):
        magic_number_bytes = self.magic_number.to_bytes(2, "big")
        memory_string = json.dumps(self._memory)
        memory_string_bytes = memory_string.encode()
        memory_size = len(memory_string_bytes)
        if memory_size > self.max_buffer_size:
            print("Requested memory space {} too large (> {}). Dict is too large. Try using smaller key strings.".format(memory_size, self.max_buffer_size))
            print("Not persisting user accessible memory.")
            return
        memory_size_bytes = memory_size.to_bytes(2, "big")
        sleep_memory[0:2] = magic_number_bytes
        sleep_memory[2:4] = memory_size_bytes
        print(4 + memory_size)
        sleep_memory[4:(4 + memory_size)] = memory_string_bytes

    @property
    def memory(self):
        if not self.loaded:
            self.load()
        return self._memory


persisted_ram = PersistedRam()
