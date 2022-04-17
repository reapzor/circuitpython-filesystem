import json


magic_number = 1337
reserved_bytes = 4


def __byte_array_size(memory_bytes):
    byte_array_size = len(memory_bytes)
    return byte_array_size - reserved_bytes


def load_memory(memory_bytes):
    max_buffer_size = __byte_array_size(memory_bytes)
    test_magic_number_bytes = memory_bytes[0:2]
    test_magic_number = int.from_bytes(test_magic_number_bytes, "big")
    if test_magic_number != magic_number:
        return {}
    memory_size_bytes = memory_bytes[2:4]
    memory_size = int.from_bytes(memory_size_bytes, "big")
    if memory_size > max_buffer_size:
        print("memory_size corrupted. Persisted memory/storage reset.")
        return {}
    persisted_memory_bytes = memory_bytes[4:(4 + memory_size)]
    try:
        persisted_memory_string = persisted_memory_bytes.decode()
        return json.loads(persisted_memory_string)
    except ValueError:
        print("persisted_memory_string corrupted. Persisted memory/storage reset.")
        return {}


def save_memory(data, memory_bytes, compare_existing=False):
    if compare_existing:
        existing_data = load_memory(memory_bytes)
        if existing_data == data:
            return
    max_buffer_size = __byte_array_size(memory_bytes)
    magic_number_bytes = magic_number.to_bytes(2, "big")
    memory_string = json.dumps(data)
    memory_string_bytes = memory_string.encode()
    memory_size = len(memory_string_bytes)
    if memory_size > max_buffer_size:
        print("Requested memory space {} too large (> {}). Dict is too large. Try using smaller key strings. ({})".format(memory_size, max_buffer_size, data))
        print("Not persisting user accessible memory/storage.")
        return
    memory_size_bytes = memory_size.to_bytes(2, "big")
    big_array = magic_number_bytes + memory_size_bytes + memory_string_bytes
    memory_bytes[0:(4 + memory_size)] = big_array
