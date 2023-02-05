from controller.core import rtc, state
from controller.menu import display, keys


def main():
    rtc.init()
    state.init()
    display.init()
    keys.init()

    display.render((0, 0, "FIRST"), (1, 1, "SECOND"), (2, 6, "THIRD"))

    while True:
        event = keys.get_event()
        if event:
            print(event)


if __name__ == "__main__":
    main()
