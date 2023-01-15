import board

BUTTON_A = board.GP10
BUTTON_B = board.GP11
BUTTON_C = board.GP12
BUTTON_D = board.GP13
BUTTONS = [BUTTON_A, BUTTON_B, BUTTON_C, BUTTON_D]
BUTTONS_VALUE_WHEN_PRESSED = False  # True = VCC, False = GND

DISPLAY_HEIGHT = 64
DISPLAY_OFFSET_X = 2
DISPLAY_WIDTH = 128

FONT_FILENAME = "/fonts/ter-u16n.pcf"
FONT_HEIGHT = 16
FONT_WIDTH = 8

I2C_ADDRESS_DISPLAY = 0x3C
I2C_ADDRESS_EEPROM = 0x57
I2C_ADDRESS_RTC = 0x68
I2C_SCL = board.GP15
I2C_SDA = board.GP14

LOCALE = "pl"

MOTOR_DURATION_DEFAULT = 1000
MOTOR_DURATION_MAX = 10000
MOTOR_DURATION_MIN = 250
MOTOR_DURATION_STEP = 250
MOTOR_DUTY_CYCLE_DEFAULT = 80
MOTOR_DUTY_CYCLE_MAX = 100
MOTOR_DUTY_CYCLE_MIN = 10
MOTOR_DUTY_CYCLE_STEP = 10
MOTOR_PHASE1 = board.GP19
MOTOR_PHASE2 = board.GP18
MOTOR_SPEED = board.GP20
