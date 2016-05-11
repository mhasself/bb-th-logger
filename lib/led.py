import glob
led_list = sorted(glob.glob('/sys/class/leds/beaglebone:*:usr*'))

class LED:
    def __init__(self, led_id):
        if not isinstance(led_id, basestring):
            led_id = led_list[led_id]
        self.led_file = led_id
    def set(self, value):
        open(self.led_file + '/brightness', 'w').write(str(value))

