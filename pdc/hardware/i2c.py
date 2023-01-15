from busio import I2C

from pdc import config

device = None


def init_i2c() -> None:
    global device

    device = I2C(config.I2C_SCL, config.I2C_SDA)
