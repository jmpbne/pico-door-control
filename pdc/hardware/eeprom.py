from adafruit_24lc32 import EEPROM_I2C

from pdc import config
from pdc.hardware import i2c
from pdc2 import state

device = None


def init_eeprom() -> None:
    global device

    device = EEPROM_I2C(i2c.device, address=config.I2C_ADDRESS_EEPROM)
    state.load_from_eeprom()


def load() -> str:
    try:
        data_bytes = device[:]
        length = data_bytes.index(b"\x00")
    except ValueError:
        data_bytes = b"{}"
        length = len(data_bytes)

    data_bytes = data_bytes[0:length]
    data_str = data_bytes.decode()

    return data_str


def dump(data: str) -> None:
    data_str = data + "\x00"
    data_bytes = data_str.encode()

    print("Writing to EEPROM", data_bytes)
    device[0 : len(data_bytes)] = data_bytes
