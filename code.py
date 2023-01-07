import asyncio
from adafruit_datetime import datetime

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
from pdc.hardware.display import init_display, write
from pdc.hardware.keys import init_keys
from pdc.hardware.motor import Motor, init_motor
from pdc.hardware.rtc import init_clock, set_clock
from pdc.locale import get_locale_function
from pdc.menu import MenuManager, Scene

try:
    from typing import Optional
except ImportError:
    Optional = ...


_ = get_locale_function(config.LOCALE)


OPENING_TIME: Optional[datetime] = None


class IdleScene(Scene):
    def __init__(self, manager):
        super().__init__(manager)

        self.clock_task = None
        self.control_task = None

    def on_enter(self):
        super().on_enter()
        self.clock_task = asyncio.create_task(self.update_clock())

    def on_exit(self):
        super().on_exit()
        self.clock_task.cancel()

    def on_press(self, event):
        if self.control_task:
            return

        super().on_press(event)

    async def scheduled_control(self):
        self.update_display()

        motor = init_motor()
        motor.open()
        await asyncio.sleep(5.0)
        motor.stop()
        motor.deinit()

        self.control_task = None
        self.update_display()

    async def update_clock(self):
        while True:
            if OPENING_TIME:
                d = datetime.now()
                now_time = d.hour, d.minute
                opening_time = OPENING_TIME.hour, OPENING_TIME.minute

                if now_time == opening_time and not self.control_task:
                    # todo: open door only once
                    print("opening the door automatically...", datetime.now())
                    coro = self.scheduled_control()
                    self.control_task = asyncio.create_task(coro)
                else:
                    print("not opening door", datetime.now())

            await asyncio.sleep(5)
            self.update_display()

    @property
    def display_commands(self):
        return [
            write(0, 0, format_datetime(datetime.now())),
            write(0, 7, "->"),
            write(0, 11, format_datetime(OPENING_TIME)),
            write(3, 0, _("Opening..."), cond=self.control_task),
        ]


class ManualControlScene(Scene):
    def __init__(self, manager):
        super().__init__(manager)

        self.control_task = None
        self.motor = None

    def on_exit(self):
        if self.motor:
            self.motor.deinit()

        super().on_exit()

    def on_press(self, event):
        if self.control_task:
            return

        if event.key_number == 1:
            self._motor_close()
        elif event.key_number == 2:
            self._motor_open()
        elif event.key_number == 3:
            self.next_scene()

    def _motor_close(self):
        self.control_task = asyncio.create_task(self.manual_control(Motor.CLOSE))

    def _motor_open(self):
        self.control_task = asyncio.create_task(self.manual_control(Motor.OPEN))

    async def manual_control(self, direction):
        self.update_display()

        if not self.motor:
            self.motor = init_motor()

        if direction == Motor.CLOSE:
            self.motor.close()
        elif direction == Motor.OPEN:
            self.motor.open()

        await asyncio.sleep(1.0)
        self.motor.stop()

        self.control_task = None
        self.update_display()

    @property
    def display_commands(self):
        return [
            write(0, 0, _("Manual control")),
            write(3, 0, f"       ↓ ↑    {_('OK')}", cond=not self.control_task),
        ]


class AbstractTimeScene(Scene):
    def __init__(self, manager):
        super().__init__(manager)

        self.time = [0, 0, 0, 0]
        self.default_time = [0, 0, 0, 0]

        self.cursor_position = 0

    def on_press(self, event):
        if event.key_number == 0:
            self._reset_time()
        elif event.key_number == 1:
            self._change_digit()
        elif event.key_number == 2:
            self._change_position()
        elif event.key_number == 3:
            if is_timearray_valid(self.time):
                super().on_press(event)

    def _reset_time(self):
        self.time = list(self.default_time)
        self.update_display()

    def _change_digit(self):
        # todo: move to pdc.date
        digit = self.time[self.cursor_position]
        digit += 1
        if digit > get_max_value_for_timearray_digit(self.cursor_position):
            digit = 0
        self.time[self.cursor_position] = digit
        self.update_display()

    def _change_position(self):
        # todo: move to pdc.date
        pos = self.cursor_position
        pos += 1
        if pos == len(self.time):
            pos = 0
        self.cursor_position = pos
        self.update_display()


class AutoOpenTimeScene(AbstractTimeScene):
    def __init__(self, manager):
        super().__init__(manager)

        self.time = datetime_to_timearray(OPENING_TIME)
        self.default_time = list(self.time)

    def on_exit(self):
        # todo: do not use global variables
        global OPENING_TIME

        if self.time != self.default_time:
            OPENING_TIME = timearray_to_datetime(self.time)
            print("setting up new opening time")
        else:
            print("no opening time change")

        super().on_exit()

    @property
    def display_commands(self):
        return [
            write(0, 0, _("Opening time")),
            write(1, 0, format_timearray(self.time)),
            write(2, 0, format_timearray_cursor(self.cursor_position)),
            write(3, 0, f"{_('Reset')}  ↓ →"),
            write(3, 14, _("OK"), cond=is_timearray_valid(self.time)),
        ]


class CurrentTimeScene(AbstractTimeScene):
    def __init__(self, manager):
        super().__init__(manager)

        self.time = datetime_to_timearray(datetime.now())
        self.default_time = list(self.time)

    def on_exit(self):
        if self.time != self.default_time:
            set_clock(timearray_to_datetime(self.time).timetuple())
            print("setting up new current time")
        else:
            print("no current time change")

        super().on_exit()

    @property
    def display_commands(self):
        return [
            write(0, 0, _("Current time")),
            write(1, 0, format_timearray(self.time)),
            write(2, 0, format_timearray_cursor(self.cursor_position)),
            write(3, 0, f"{_('Reset')}  ↓ →"),
            write(3, 14, _("OK"), cond=is_timearray_valid(self.time)),
        ]


async def main():
    display = init_display()
    keys = init_keys()
    init_clock()

    menu = MenuManager(
        scenes=[IdleScene, ManualControlScene, AutoOpenTimeScene, CurrentTimeScene],
        display=display,
        keys=keys,
    )

    await menu.task()


if __name__ == "__main__":
    asyncio.run(main())
