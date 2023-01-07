from digitalio import DigitalInOut, Direction

from pdc import config


class Motor:
    CLOSE = 0
    OPEN = 1

    def __init__(self) -> None:
        self.phase1 = DigitalInOut(config.MOTOR_PHASE1)
        self.phase1.direction = Direction.OUTPUT

        self.phase2 = DigitalInOut(config.MOTOR_PHASE2)
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


def init_motor() -> Motor:
    return Motor()
