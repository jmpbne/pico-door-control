from keypad import Keys

from pdc import config


def init_keys() -> Keys:
    return Keys(config.BUTTONS, value_when_pressed=config.BUTTONS_VALUE_WHEN_PRESSED)
