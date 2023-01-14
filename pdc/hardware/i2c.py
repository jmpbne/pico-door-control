from busio import I2C

from pdc import config

i2c = I2C(config.I2C_SCL, config.I2C_SDA)
