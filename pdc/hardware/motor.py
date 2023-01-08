from digitalio import DigitalInOut, Direction
from pwmio import PWMOut

from pdc import config


MotorDirection = int


class Motor:
    CLOSE = 0
    OPEN = 1

    def __init__(self) -> None:
        self.speed = PWMOut(config.MOTOR_SPEED)

        self.phase1 = DigitalInOut(config.MOTOR_PHASE1)
        self.phase1.direction = Direction.OUTPUT

        self.phase2 = DigitalInOut(config.MOTOR_PHASE2)
        self.phase2.direction = Direction.OUTPUT

        self.stop()

    def open(self, percentage: int = 100) -> None:
        self.speed.duty_cycle = get_duty_cycle(percentage)
        self.phase1.value = True
        self.phase2.value = False

    def close(self, percentage: int = 100) -> None:
        self.speed.duty_cycle = get_duty_cycle(percentage)
        self.phase1.value = False
        self.phase2.value = True

    def stop(self) -> None:
        self.speed.duty_cycle = 0
        self.phase1.value = False
        self.phase2.value = False

    def deinit(self) -> None:
        # TODO: convert into context manager
        self.speed.deinit()
        self.phase1.deinit()
        self.phase2.deinit()


def get_duty_cycle(percentage: int) -> int:
    if percentage < 0:
        percentage = 0
    if percentage > 100:
        percentage = 100

    return 65535 * percentage // 100


def init_motor() -> Motor:
    return Motor()
