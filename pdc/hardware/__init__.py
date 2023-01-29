from pdc.hardware.display import init_display
from pdc.hardware.eeprom import init_eeprom
from pdc.hardware.i2c import init_i2c
from pdc.hardware.keys import init_keys
from pdc.hardware.rtc import init_rtc


def init_hardware() -> None:
    init_i2c()
    init_eeprom()
    init_rtc()
    init_display()
    init_keys()
    # init_motor()
