from controller.core import nvm

data = {}


def init():
    load_state_safe()


def load_state():
    data.clear()
    data.update(**nvm.read_nvm())


def load_default_state():
    data.clear()


def load_state_safe():
    try:
        load_state()
    except Exception as e:
        print(f"Could not load settings because of {e.__class__.__name__}")
        load_default_state()


def save_state():
    nvm.write_nvm(data)
