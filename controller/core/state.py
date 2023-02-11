from controller.core import nvm

data = {}


def init():
    load_state()


def load_state():
    data.clear()
    data.update(**nvm.read_nvm())


def load_default_state():
    data.clear()


def load_state_safe():
    try:
        load_state()
    except Exception as e:
        print(f"Could not load settings because of {type(e)}")
        load_default_state()


def save_state():
    nvm.write_nvm(data)
