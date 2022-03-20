from scheduler import Scheduler


class LED:

    def __init__(self, supports_power=True):
        self.supports_power = supports_power
        if supports_power:
            self._powered_on = None
        else:
            self._powered_on = True

    def _set_color(self, r, g, b):
        pass

    def _turn_off(self):
        pass

    def set_color(self, r, g, b):
        if not self.powered_on():
            self.set_power(True)
        self._set_color(r, g, b)

    def turn_off(self):
        if not self.powered_on():
            self.set_power(True)
        self._turn_off()

    def _set_power(self, power):
        pass

    def set_power(self, power):
        if self.supports_power:
            self._powered_on = power
            self._set_power(power)

    def _check_power(self):
        return self._powered_on

    def powered_on(self):
        if not self.supports_power:
            return True
        if self._powered_on is not None:
            return self._powered_on
        self._powered_on = self._check_power()
        return self._powered_on


class NeoPixelLED(LED):

    def __init__(self, pixel, power_pin=None):
        """
        :param pixel
        :type pixel: neopixel.NeoPixel
        :param power_pin
        :type power_pin: digitalio.DigitalInOut
        """
        self.pixel = pixel
        self.power_pin = power_pin
        super().__init__(supports_power=power_pin is not None)

    def _set_color(self, r, g, b):
        self.pixel[0] = (r, g, b)

    def _turn_off(self):
        self.pixel[0] = (0, 0, 0)

    def _set_power(self, power):
        self.power_pin.value = power

    def _check_power(self):
        return self.power_pin.value


class LEDManager:

    def __init__(self, led):
        """
        :type led: LED
        """
        self.led = led
        self.scheduler = Scheduler()

    async def set_color(self, r, g, b):
        self.led.set_color(r, g, b)

    async def turn_off(self):
        self.led.turn_off()

    async def set_power(self, power):
        self.led.set_power(power)

    async def set_green(self):
        await self.set_color(0, 255, 0)

    async def set_red(self):
        await self.set_color(255, 0, 0)

    async def set_blue(self):
        await self.set_color(0, 0, 255)

    async def set_purple(self):
        await self.set_color(255, 0, 255)

    def blink(self, color=None, interval_on=1000, interval_off=1000, count=2):
        for _ in range(count):
            if color is None:
                self.scheduler.schedule(self.set_color, args=[255, 255, 255], interval=interval_on)
            else:
                self.scheduler.schedule(self.set_color, args=color, interval=interval_on)
            self.scheduler.schedule(self.turn_off, interval=interval_off)
        if not self.scheduler.started:
            self.scheduler.start()

    def blink_green(self, interval_on=1000, interval_off=1000, count=2):
        self.blink(color=[0, 255, 0], interval_on=interval_on, interval_off=interval_off, count=count)

    def blink_red(self, interval_on=1000, interval_off=1000, count=2):
        self.blink(color=[255, 0, 0], interval_on=interval_on, interval_off=interval_off, count=count)

    def blink_blue(self, interval_on=1000, interval_off=1000, count=2):
        self.blink(color=[0, 0, 255], interval_on=interval_on, interval_off=interval_off, count=count)

    def blink_purple(self, interval_on=1000, interval_off=1000, count=2):
        self.blink(color=[255, 0, 200], interval_on=interval_on, interval_off=interval_off, count=count)
