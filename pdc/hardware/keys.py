from keypad import Keys

from pdc import config

device = None


def init_keys() -> None:
    global device

    device = Keys(config.BUTTONS, value_when_pressed=config.BUTTONS_VALUE_WHEN_PRESSED)
