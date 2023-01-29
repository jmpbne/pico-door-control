from digitalio import DigitalInOut, Direction
from microcontroller import Pin
from pwmio import PWMOut

MotorDirection = int


class Motor:
    CLOSE = 0
    OPEN = 1

    def __init__(self, phase1: Pin, phase2: Pin, pwm: Pin) -> None:
        self.speed = PWMOut(pwm)

        self.phase1 = DigitalInOut(phase1)
        self.phase1.direction = Direction.OUTPUT

        self.phase2 = DigitalInOut(phase2)
        self.phase2.direction = Direction.OUTPUT

        self.stop()

    def open(self, percentage: float = 1.0) -> None:
        self.speed.duty_cycle = get_duty_cycle(percentage)
        self.phase1.value = True
        self.phase2.value = False

    def close(self, percentage: float = 1.0) -> None:
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


def get_duty_cycle(percentage: float) -> int:
    percentage = int(percentage * 100)

    if percentage < 0:
        percentage = 0
    if percentage > 100:
        percentage = 100

    return 65535 * percentage // 100
