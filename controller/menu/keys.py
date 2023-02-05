from keypad import Keys

from controller import config

device = Keys(config.BUTTONS, value_when_pressed=False)


def init():
    pass


def get_event():
    event = device.events.get()

    if not event or not event.pressed:
        return None

    return event
