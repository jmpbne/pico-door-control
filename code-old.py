from keypad import Event

import asyncio
from adafruit_datetime import datetime

from pdc import config, date, state
from pdc.hardware import display, init_hardware, motor, rtc
from pdc.hardware.display import WriteCommand, write
from pdc.hardware.motor import Motor, MotorDirection
from pdc.locale import get_locale_function
from pdc.menu import MenuManager, Scene

try:
    from typing import List, NoReturn
except ImportError:
    List = ...
    NoReturn = ...

_ = get_locale_function(config.LOCALE)


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

        if event.key_number == 0:
            display.toggle()
        elif event.key_number == 3:
            if state.is_display_awake():
                self.next_scene()

    async def update_clock(self) -> NoReturn:
        while True:
            await asyncio.sleep(5)
            if state.is_display_awake():
                self.update_display()

    @property
    def display_commands(self) -> List[WriteCommand]:
        return [
            write(0, 0, _("Now:")),
            write(0, 10, date.format_datetime(datetime.now())),
            write(1, 0, _("Open at:")),
            write(1, 10, date.format_datetime(state.get_opening_time())),
            write(3, 0, _("Opening..."), cond=self.is_opening),
            write(3, 0, _("Disp.Off"), cond=not self.is_opening),
            write(3, 12, _("Menu"), cond=not self.is_opening),
        ]


class ManualControlScene(Scene):
    def __init__(self, manager: MenuManager) -> None:
        super().__init__(manager)

        self.control_task = None
        self.percentage = state.get_opening_duty_cycle()

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

        if direction == Motor.CLOSE:
            motor.device.close(self.percentage)
        elif direction == Motor.OPEN:
            motor.device.open(self.percentage)

        await asyncio.sleep(1.0)
        motor.device.stop()

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
            if date.is_timearray_valid(self.time):
                super().on_press(event)

    def _reset_value(self) -> None:
        self.time = list(self.default_time)
        self.update_display()

    def _change_digit(self) -> None:
        # todo: move to pdc.date
        digit = self.time[self.cursor_position]
        digit += 1
        if digit > date.get_max_value_for_timearray_digit(self.cursor_position):
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

        self.time = date.datetime_to_timearray(state.get_opening_time())
        self.default_time = list(self.time)

    def on_exit(self) -> None:
        if self.time != self.default_time:
            state.set_opening_time(date.timearray_to_datetime(self.time))
            state.set_opening_cooldown(False)
            print("setting up new opening time")
        else:
            print("no opening time change")

        super().on_exit()

    @property
    def display_commands(self) -> List[WriteCommand]:
        return [
            write(0, 0, _("Opening timer")),
            write(1, 0, date.format_timearray(self.time)),
            write(2, 0, date.format_timearray_cursor(self.cursor_position)),
            write(3, 0, f"{_('Reset')}  ↑ →"),
            write(3, 14, _("OK"), cond=date.is_timearray_valid(self.time)),
        ]


class AutoOpenDurationScene(Scene):
    def __init__(self, manager: MenuManager) -> None:
        super().__init__(manager)

        self.duration = state.get_opening_duration()
        self.default_duration = state.get_opening_duration()

    def on_exit(self) -> None:
        state.set_opening_duration(self.duration)
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

        self.percentage = state.get_opening_duty_cycle()
        self.default_percentage = state.get_opening_duty_cycle()

    def on_exit(self) -> None:
        state.set_opening_duty_cycle(self.percentage)
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

        self.time = date.datetime_to_timearray(datetime.now())
        self.default_time = list(self.time)

    def on_exit(self) -> None:
        if self.time != self.default_time:
            rtc.device.datetime = date.timearray_to_datetime(self.time).timetuple()
            state.set_opening_cooldown(False)
            print("setting up new current time")
        else:
            print("no current time change")

        super().on_exit()

    @property
    def display_commands(self) -> List[WriteCommand]:
        return [
            write(0, 0, _("Current time")),
            write(1, 0, date.format_timearray(self.time)),
            write(2, 0, date.format_timearray_cursor(self.cursor_position)),
            write(3, 0, f"{_('Reset')}  ↑ →"),
            write(3, 14, _("OK"), cond=date.is_timearray_valid(self.time)),
        ]


async def control(manager: MenuManager) -> NoReturn:
    while True:
        current = datetime.now()
        opening = state.get_opening_time()

        print(current, "->", opening)

        if (
            opening
            and current.hour == opening.hour
            and current.minute == opening.minute
        ):
            if state.is_opening_cooldown():
                print("cooldown")
            elif manager.current_scene_id == 0:
                # todo: use context manager to lock keys temporarily
                manager.current_scene.is_opening = True
                manager.current_scene.update_display()

                print("opening the door automatically...", datetime.now())
                motor.device.open(state.get_opening_duty_cycle())
                await asyncio.sleep(state.get_opening_duration() / 1000.0)
                motor.device.stop()
                print("door opened", datetime.now())

                manager.current_scene.is_opening = False
                manager.current_scene.update_display()

                state.set_opening_cooldown(True)
            else:
                print("not opening door, go back to IdleScene")
        else:
            state.set_opening_cooldown(False)

        await asyncio.sleep(5)


async def main() -> NoReturn:
    init_hardware()

    menu = MenuManager(
        [
            IdleScene,
            ManualControlScene,
            AutoOpenTimeScene,
            AutoOpenDurationScene,
            AutoOpenSpeedScene,
            CurrentTimeScene,
        ]
    )

    menu_task = asyncio.create_task(menu.task())
    control_task = asyncio.create_task(control(menu))

    await asyncio.gather(menu_task, control_task)


if __name__ == "__main__":
    asyncio.run(main())