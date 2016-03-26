"""
This library provides classes and "Cape Management" support for
operating an I2C bus on top of arbitrary Beaglebone gpio pins.

In the present implementation, the clock line can be shared and data
lines multiplexed.
"""

import time, sys, os

def export_gpio(n):
    if os.path.exists('/sys/class/gpio/gpio%i' % n):
        return
    print 'Exporting %i' % n
    f = open('/sys/class/gpio/export', 'w')
    f.write('%i\n' % n)
    f.close()

class Pin:
    # Operate an open collector pin, or whatever, where we either
    # output 0 to pull low, or go to input mode with external pull up
    # resistor to leave the bus high (and to sometimes read data).
    def __init__(self, filename):
        self.filename = filename
        self.vilename = filename.replace('/direction', '/value')
        self.set_hi()
    def set_direction(self, d):
        dirf = open(self.filename, 'w')
        dirf.write('%s\n' % d)
        dirf.close()
    def set_hi(self):
        self.set_direction('in')
    def set_lo(self):
        self.set_direction('low')
    def set(self, value):
        if value:
            self.set_hi()
        else:
            self.set_lo()
    def wait_hi(self):
        while self.get() == 0:
            time.sleep(.01)
    def get(self):
        return int(open(self.vilename, 'r').read())

class I2CGang:
    # Pump one or more I2C buses.  The CLK pin is shared, but each bus
    # gets its own DAT pin.
    def __init__(self, clk, *dat):
        map(export_gpio, [clk] + list(dat))
        self.clk = Pin('/sys/class/gpio/gpio%i/direction' % clk)
        self.dats = [Pin('/sys/class/gpio/gpio%i/direction' % d) for d in dat]
        self.delay_s = 1e-4
    def wait(self, n=1):
        time.sleep(self.delay_s*n)
    def bcast_hi(self):
        for d in self.dats:
            d.set_hi()
    def bcast_lo(self):
        for d in self.dats:
            d.set_lo()
    def bcast(self, val):
        if val:
            self.bcast_hi()
        else:
            self.bcast_lo()
    def gather(self):
        return [d.get() for d in self.dats]
    def start(self):
        self.bcast_hi()
        self.clk.set_hi()
        self.wait()
        self.bcast_lo()
        self.wait()
        self.clk.set_lo()
    def stop(self):
        self.bcast_lo()
        self.wait()
        self.clk.set_hi()
        self.wait()
        self.bcast_hi()
    def write_byte(self, bits):
        for i in range(8):
            b = (bits >> (7-i)) & 1
            self.clk.set_lo()
            self.wait()
            self.bcast(b)
            self.wait()
            self.clk.set_hi()
            self.wait()
        self.clk.set_lo()
        self.wait()
        self.bcast_hi()
        self.wait()
        self.clk.set_hi()
        self.wait()
        acks = self.gather()
        self.clk.set_lo()
        self.wait()
        return acks
    def read_byte(self, ack=True):
        data = [0] * len(self.dats)
        self.bcast_hi()
        for i in range(8):
            self.clk.set_hi()
            self.clk.wait_hi()
            bits = self.gather()
            for i,b in enumerate(bits):
                data[i] = (data[i] << 1) | b
            self.wait()
            self.clk.set_lo()
            self.wait()
        if ack:
            self.bcast_lo()
        else:
            self.bcast_hi()
        self.clk.set_hi()
        self.wait()
        self.clk.set_lo()
        self.bcast_hi()
        self.wait()
        return data
    def write_sequence(self, addr, mem, *data):
        self.start()
        self.write_byte((addr << 1) | 0)
        self.write_byte(mem)
        for d in data:
            self.write_byte(d)
        self.stop()
    def read_sequence(self, addr, n):
        self.start()
        # Send address + R
        self.write_byte((addr << 1) | 1)
        # Read bits
        datas = [self.read_byte(i!=(n-1)) for i in range(n)]
        datas = zip(*datas)
        self.stop()
        return datas
