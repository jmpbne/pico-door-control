from controller.core import rtc, state
from controller.display import display


def main():
    rtc.init()
    state.init()
    display.init()

    display.render((0, 0, "FIRST"), (1, 1, "SECOND"), (2, 6, "THIRD"))

    while True:
        pass


if __name__ == "__main__":
    main()
