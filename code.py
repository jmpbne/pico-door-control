from controller.core import rtc, state
from controller.menu import display, keys
from controller.menu.scenes import SceneManager


def main():
    rtc.init()
    state.init()
    display.init()
    keys.init()

    manager = SceneManager()

    while True:
        manager.poll()


if __name__ == "__main__":
    main()
