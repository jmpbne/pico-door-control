import json

from microcontroller import nvm

HEADER_SIZE = 2
HEADER_SIZE_BITS = 16


def read_data_length():
    hi, lo = nvm[0:HEADER_SIZE]
    return hi * (1 << 8) + lo


def make_data_length(length):
    assert 0 <= length < (1 << HEADER_SIZE_BITS)

    hi, lo = divmod(length, (1 << 8))
    return bytes((hi, lo))


def read_nvm():
    raw_length = read_data_length()

    print(f"Reading {raw_length} bytes of data from NVM")
    raw_bytes = nvm[HEADER_SIZE : raw_length + HEADER_SIZE]
    raw_str = raw_bytes.decode()

    data = json.loads(raw_str)

    return data


def write_nvm(data):
    raw_str = json.dumps(data, separators=(",", ":"))
    raw_bytes = raw_str.encode()
    raw_length = len(raw_bytes)

    print(f"Writing {raw_length} bytes of data to NVM")
    nvm[0 : raw_length + HEADER_SIZE] = make_data_length(raw_length) + raw_bytes
