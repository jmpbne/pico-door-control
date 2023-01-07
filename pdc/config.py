import board

BUTTON_A = board.GP18
BUTTON_B = board.GP19
BUTTON_C = board.GP20
BUTTON_D = board.GP21
BUTTONS = [BUTTON_A, BUTTON_B, BUTTON_C, BUTTON_D]
BUTTONS_VALUE_WHEN_PRESSED = False  # True = VCC, False = GND

DISPLAY_ADDRESS = 0x3C
DISPLAY_HEIGHT = 64
DISPLAY_SCL = board.GP17
DISPLAY_SDA = board.GP16
DISPLAY_OFFSET_X = 2
DISPLAY_WIDTH = 128

FONT_FILENAME = "/bizcat.pcf"
FONT_HEIGHT = 16
FONT_WIDTH = 8

LOCALE = "pl"

MOTOR_PHASE1 = board.GP26
MOTOR_PHASE2 = board.GP27

# This is the application state variable.
# Change this setting only for debugging purposes.
OPENING_TIME = None
