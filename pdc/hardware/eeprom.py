from adafruit_24lc32 import EEPROM_I2C

from pdc import config
from pdc.hardware.i2c import i2c

_eeprom = EEPROM_I2C(i2c, address=config.I2C_ADDRESS_EEPROM)


def load() -> str:
    try:
        data_bytes = _eeprom[:]
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
    _eeprom[0 : len(data_bytes)] = data_bytes
