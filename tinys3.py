import board
from digitalio import DigitalInOut, Direction
from analogio import AnalogIn
import neopixel
from hardware_support import HardwareSupport
from led import LEDManager, NeoPixelLED


class TinyS3Support(HardwareSupport):

    def __init__(self):
        # Setup the BATTERY voltage sense pin
        self._vbat_voltage = AnalogIn(board.BATTERY)
        # Setup the VBUS sense pin
        self._vbus_sense = DigitalInOut(board.VBUS_SENSE)
        self._vbus_sense.direction = Direction.INPUT
        # Setup power control for the status led
        self._neopixel_power = DigitalInOut(board.NEOPIXEL_POWER)
        self._neopixel_power.direction = Direction.OUTPUT
        # Status led
        self._neopixel = neopixel.NeoPixel(board.NEOPIXEL,
                                           1,
                                           brightness=1.0,
                                           auto_write=True,
                                           pixel_order=neopixel.GRB)
        self._status_led = LEDManager(NeoPixelLED(self._neopixel, power_pin=self._neopixel_power))
        super().__init__()

    def status_led(self):
        return self._status_led

    def status_led_power(self):
        return self._neopixel_power

    def batt_voltage(self):
        # This formula should show the nominal 4.2V max capacity (approximately) when 5V is present and the
        # VBAT is in charge state for a 1S LiPo battery with a max capacity of 4.2V
        adc_resolution = 2 ** 16 - 1
        aref_voltagge = 3.3
        r1 = 442000
        r2 = 160000
        return self._vbat_voltage.value / adc_resolution * aref_voltagge * (r1 + r2) / r2

    def vbus_present(self):
        return self._vbus_sense.value


