import board
import neopixel
from hardware_support import HardwareSupport
from led import LEDManager, NeoPixelLED


class S3DevKitSupport(HardwareSupport):

    def __init__(self):
        # Status led
        self._neopixel = neopixel.NeoPixel(board.NEOPIXEL,
                                           1,
                                           brightness=1.0,
                                           auto_write=True,
                                           pixel_order=neopixel.GRB)
        self._status_led = LEDManager(NeoPixelLED(self._neopixel))
        super().__init__()

    def status_led(self):
        return self._status_led

    def status_led_power(self):
        return True

    def batt_voltage(self):
        return -1

    def vbus_present(self):
        return False
