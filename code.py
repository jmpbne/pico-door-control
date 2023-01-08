from keypad import Event

import asyncio
from adafruit_datetime import datetime, timedelta

from pdc import config
from pdc.date import (
    datetime_to_timearray,
    format_datetime,
    format_timearray,
    format_timearray_cursor,
    get_max_value_for_timearray_digit,
    is_timearray_valid,
    timearray_to_datetime,
)
from pdc.hardware.display import WriteCommand, init_display, write
from pdc.hardware.keys import init_keys
from pdc.hardware.motor import Motor, MotorDirection, init_motor
from pdc.hardware.rtc import init_clock, set_clock
from pdc.locale import get_locale_function
from pdc.menu import MenuManager, Scene

try:
    from typing import List, NoReturn, Optional
except ImportError:
    List = ...
    NoReturn = ...
    Optional = ...

_ = get_locale_function(config.LOCALE)

OPENING_COOLDOWN = False
OPENING_DURATION = config.MOTOR_DURATION_DEFAULT
OPENING_DUTY_CYCLE = config.MOTOR_DUTY_CYCLE_DEFAULT
OPENING_TIME: Optional[datetime] = None


class IdleScene(Scene):
    def __init__(self, manager: MenuManager) -> None:
        super().__init__(manager)

        self.clock_task = None
        self.is_opening = False

    def on_enter(self) -> None:
        super().on_enter()
        self.clock_task = asyncio.create_task(self.update_clock())

    def on_exit(self) -> None:
        super().on_exit()
        self.clock_task.cancel()

    def on_press(self, event: Event) -> None:
        if self.is_opening:
            return

        super().on_press(event)

    async def update_clock(self) -> NoReturn:
        while True:
            await asyncio.sleep(5)
            self.update_display()

    @property
    def display_commands(self) -> List[WriteCommand]:
        return [
            write(0, 0, format_datetime(datetime.now())),
            write(0, 7, "->"),
            write(0, 11, format_datetime(OPENING_TIME)),
            write(3, 0, _("Opening..."), cond=self.is_opening),
        ]


class ManualControlScene(Scene):
    def __init__(self, manager: MenuManager) -> None:
        super().__init__(manager)

        self.control_task = None
        self.motor = None
        self.percentage = OPENING_DUTY_CYCLE

    def on_exit(self) -> None:
        if self.motor:
            self.motor.deinit()

        super().on_exit()

    def on_press(self, event: Event) -> None:
        if self.control_task:
            return

        if event.key_number == 0:
            self._change_percentage()
        if event.key_number == 1:
            self._motor_close()
        elif event.key_number == 2:
            self._motor_open()
        elif event.key_number == 3:
            self.next_scene()

    def _change_percentage(self) -> None:
        self.percentage += config.MOTOR_DUTY_CYCLE_STEP
        if self.percentage > config.MOTOR_DUTY_CYCLE_MAX:
            self.percentage = config.MOTOR_DUTY_CYCLE_MIN

        self.update_display()

    def _motor_close(self) -> None:
        self.control_task = asyncio.create_task(self.manual_control(Motor.CLOSE))

    def _motor_open(self) -> None:
        self.control_task = asyncio.create_task(self.manual_control(Motor.OPEN))

    async def manual_control(self, direction: MotorDirection) -> None:
        self.update_display()

        if not self.motor:
            self.motor = init_motor()

        if direction == Motor.CLOSE:
            self.motor.close(self.percentage)
        elif direction == Motor.OPEN:
            self.motor.open(self.percentage)

        await asyncio.sleep(1.0)
        self.motor.stop()

        self.control_task = None
        self.update_display()

    @property
    def display_commands(self) -> List[WriteCommand]:
        return [
            write(0, 0, _("Manual control")),
            write(3, 0, f"       ↓ ↑    {_('OK')}", cond=not self.control_task),
            write(3, 0, f"{self.percentage}%"),
        ]


class AbstractTimeScene(Scene):
    def __init__(self, manager: MenuManager) -> None:
        super().__init__(manager)

        self.time = [0, 0, 0, 0]
        self.default_time = [0, 0, 0, 0]

        self.cursor_position = 0

    def on_press(self, event: Event) -> None:
        if event.key_number == 0:
            self._reset_value()
        elif event.key_number == 1:
            self._change_digit()
        elif event.key_number == 2:
            self._change_position()
        elif event.key_number == 3:
            if is_timearray_valid(self.time):
                super().on_press(event)

    def _reset_value(self) -> None:
        self.time = list(self.default_time)
        self.update_display()

    def _change_digit(self) -> None:
        # todo: move to pdc.date
        digit = self.time[self.cursor_position]
        digit += 1
        if digit > get_max_value_for_timearray_digit(self.cursor_position):
            digit = 0
        self.time[self.cursor_position] = digit
        self.update_display()

    def _change_position(self) -> None:
        # todo: move to pdc.date
        pos = self.cursor_position
        pos += 1
        if pos == len(self.time):
            pos = 0
        self.cursor_position = pos
        self.update_display()


class AutoOpenTimeScene(AbstractTimeScene):
    def __init__(self, manager: MenuManager) -> None:
        super().__init__(manager)

        self.time = datetime_to_timearray(OPENING_TIME)
        self.default_time = list(self.time)

    def on_exit(self) -> None:
        # todo: do not use global variables
        global OPENING_COOLDOWN
        global OPENING_TIME

        if self.time != self.default_time:
            OPENING_TIME = timearray_to_datetime(self.time)
            OPENING_COOLDOWN = False
            print("setting up new opening time")
        else:
            print("no opening time change")

        super().on_exit()

    @property
    def display_commands(self) -> List[WriteCommand]:
        return [
            write(0, 0, _("Opening timer")),
            write(1, 0, format_timearray(self.time)),
            write(2, 0, format_timearray_cursor(self.cursor_position)),
            write(3, 0, f"{_('Reset')}  ↑ →"),
            write(3, 14, _("OK"), cond=is_timearray_valid(self.time)),
        ]


class AutoOpenDurationScene(Scene):
    def __init__(self, manager: MenuManager) -> None:
        super().__init__(manager)

        self.duration = OPENING_DURATION
        self.default_duration = OPENING_DURATION

    def on_exit(self) -> None:
        # todo: do not use global variables
        global OPENING_DURATION

        OPENING_DURATION = self.duration
        print("changed opening duration")

        super().on_exit()

    def on_press(self, event: Event) -> None:
        if event.key_number == 0:
            self._reset_value()
        elif event.key_number == 1:
            self._decrease_value()
        elif event.key_number == 2:
            self._increase_value()
        elif event.key_number == 3:
            self.next_scene()

    def _reset_value(self) -> None:
        self.duration = self.default_duration
        self.update_display()

    def _decrease_value(self) -> None:
        if self.duration > config.MOTOR_DURATION_MIN:
            self.duration -= config.MOTOR_DURATION_STEP
            self.update_display()

    def _increase_value(self) -> None:
        if self.duration < config.MOTOR_DURATION_MAX:
            self.duration += config.MOTOR_DURATION_STEP
            self.update_display()

    def _format_time(self) -> str:
        # todo: move to separate file
        return f"{(self.duration / 1000.0):.2f}s"

    @property
    def display_commands(self) -> List[WriteCommand]:
        return [
            write(0, 0, _("Opening duration")),
            write(1, 0, self._format_time()),
            write(3, 0, f"{_('Reset')}  ↓ ↑    {_('OK')}"),
        ]


class AutoOpenSpeedScene(Scene):
    def __init__(self, manager: MenuManager) -> None:
        super().__init__(manager)

        self.percentage = OPENING_DUTY_CYCLE
        self.default_percentage = OPENING_DUTY_CYCLE

    def on_exit(self) -> None:
        # todo: do not use global variables
        global OPENING_DUTY_CYCLE

        OPENING_DUTY_CYCLE = self.percentage
        print("changed opening percentage")

        super().on_exit()

    def on_press(self, event: Event) -> None:
        if event.key_number == 0:
            self._reset_value()
        elif event.key_number == 1:
            self._decrease_value()
        elif event.key_number == 2:
            self._increase_value()
        elif event.key_number == 3:
            self.next_scene()

    def _reset_value(self) -> None:
        self.percentage = self.default_percentage
        self.update_display()

    def _decrease_value(self) -> None:
        if self.percentage > config.MOTOR_DUTY_CYCLE_MIN:
            self.percentage -= config.MOTOR_DUTY_CYCLE_STEP
            self.update_display()

    def _increase_value(self) -> None:
        if self.percentage < config.MOTOR_DUTY_CYCLE_MAX:
            self.percentage += config.MOTOR_DUTY_CYCLE_STEP
            self.update_display()

    def _format_percentage(self) -> str:
        # todo: move to separate file
        return f"{self.percentage}%"

    @property
    def display_commands(self) -> List[WriteCommand]:
        return [
            write(0, 0, _("Opening speed")),
            write(1, 0, self._format_percentage()),
            write(3, 0, f"{_('Reset')}  ↓ ↑    {_('OK')}"),
        ]


class CurrentTimeScene(AbstractTimeScene):
    def __init__(self, manager: MenuManager) -> None:
        super().__init__(manager)

        self.time = datetime_to_timearray(datetime.now())
        self.default_time = list(self.time)

    def on_exit(self) -> None:
        global OPENING_COOLDOWN

        if self.time != self.default_time:
            set_clock(timearray_to_datetime(self.time).timetuple())
            OPENING_COOLDOWN = False
            print("setting up new current time")
        else:
            print("no current time change")

        super().on_exit()

    @property
    def display_commands(self) -> List[WriteCommand]:
        return [
            write(0, 0, _("Current time")),
            write(1, 0, format_timearray(self.time)),
            write(2, 0, format_timearray_cursor(self.cursor_position)),
            write(3, 0, f"{_('Reset')}  ↑ →"),
            write(3, 14, _("OK"), cond=is_timearray_valid(self.time)),
        ]


async def control(manager: MenuManager) -> NoReturn:
    # todo: do not use global variables
    global OPENING_COOLDOWN
    global OPENING_TIME

    while True:
        current = datetime.now()
        opening = OPENING_TIME

        print(current, "->", opening)

        if (
            opening
            and current.hour == opening.hour
            and current.minute == opening.minute
        ):
            if OPENING_COOLDOWN:
                print("cooldown")
            elif manager.current_scene_id == 0:
                # todo: use context manager to lock keys temporarily
                manager.current_scene.is_opening = True
                manager.current_scene.update_display()

                print("opening the door automatically...", datetime.now())
                motor = init_motor()
                motor.open(OPENING_DUTY_CYCLE)
                await asyncio.sleep(OPENING_DURATION / 1000.0)
                motor.stop()
                motor.deinit()
                print("door opened", datetime.now())

                manager.current_scene.is_opening = False
                manager.current_scene.update_display()

                OPENING_COOLDOWN = True
            else:
                print("not opening door, go back to IdleScene")
        else:
            OPENING_COOLDOWN = False

        await asyncio.sleep(5)


async def main() -> NoReturn:
    display = init_display()
    keys = init_keys()
    init_clock()

    menu = MenuManager(
        scenes=[
            IdleScene,
            ManualControlScene,
            AutoOpenTimeScene,
            AutoOpenDurationScene,
            AutoOpenSpeedScene,
            CurrentTimeScene,
        ],
        display=display,
        keys=keys,
    )

    menu_task = asyncio.create_task(menu.task())
    control_task = asyncio.create_task(control(menu))

    await asyncio.gather(menu_task, control_task)


if __name__ == "__main__":
    asyncio.run(main())
