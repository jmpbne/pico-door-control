from digitalio import DigitalInOut, Direction
from microcontroller import Pin


class Motor:
    CLOSE = 0
    OPEN = 1

    def __init__(self, phase1_pin: Pin, phase2_pin: Pin) -> None:
        self.phase1 = DigitalInOut(phase1_pin)
        self.phase1.direction = Direction.OUTPUT

        self.phase2 = DigitalInOut(phase2_pin)
        self.phase2.direction = Direction.OUTPUT

        self.stop()

    def open(self) -> None:
        self.phase1.value = True
        self.phase2.value = False

    def close(self) -> None:
        self.phase1.value = False
        self.phase2.value = True

    def stop(self) -> None:
        self.phase1.value = False
        self.phase2.value = False

    def deinit(self) -> None:
        # TODO: convert into context manager
        self.phase1.deinit()
        self.phase2.deinit()
