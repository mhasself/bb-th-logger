import gp_i2c
import time, sys, os

DATA_FILE = '/root/data/HT_log.txt'

from bbb_pins import get_pin

def decode_ht(d):
    status = (d >> 30) & 0x3
    H = (d>>16) & 0x3fff
    T = (d>> 2) & 0x3fff
    h = 100. * H / (2**14-2)
    t = 165. * T / (2**14-2) - 40
    return status, h, t

# Simplest indexing scheme is (name, clock_pin, data_pin).
devices = [
    ('L1_gw' , get_pin('P8', 39)['gpio'], get_pin('P8', 40)['gpio']), #North
    ('L1_bw' , get_pin('P8', 39)['gpio'], get_pin('P8', 41)['gpio']), #North
    ('L4_gw' , get_pin('P9', 21)['gpio'], get_pin('P9', 22)['gpio']), #East
    ('L4_bw' , get_pin('P9', 21)['gpio'], get_pin('P9', 23)['gpio']), #East Middle
#    ('L7_gw' , get_pin('P8', 35)['gpio'], get_pin('P8', 36)['gpio']), #South - not working 2016/12/21
#    ('L7_bw' , get_pin('P8', 35)['gpio'], get_pin('P8', 37)['gpio']), #South - not working 2016/12/21
    ('L8_gw' , get_pin('P8', 15)['gpio'], get_pin('P8', 16)['gpio']), #West
    ('L8_bw' , get_pin('P8', 15)['gpio'], get_pin('P8', 17)['gpio']), #West
#    ('L9_gw' , get_pin('P9', 11)['gpio'], get_pin('P8', 12)['gpio']), #Roof - not working 2016/12/21
#    ('L9_bw' , get_pin('P9', 11)['gpio'], get_pin('P8', 13)['gpio']), #Roof - not working 2016/12/21
    ('L12_gw', get_pin('P8',  7)['gpio'], get_pin('P8',  8)['gpio']),
]

# Then build it into buses.
buses = {}
for name, clkpin, datpin in devices:
    if not clkpin in buses:
        buses[clkpin] = []
    buses[clkpin].append((name, datpin))

signals = {}
for clkpin in buses.keys():
    names, datpins = zip(*buses[clkpin])
    i2c = gp_i2c.I2CGang(clkpin, *datpins)
    for index, name in enumerate(names):
        signals[name] = (i2c, index)
    buses[clkpin] = i2c

# buses becomes list:
buses = buses.values()

fout = open(DATA_FILE, 'a')
def write(line):
    fout.write(line + '\n')
    print line


DELAY = 5
while True:
    # Read: get data, then write as signals.
    for bus in buses:
        bus.write_sequence(0x27, 0, 0)

    time.sleep(0.1)
    for bus in buses:
        byte_lists = bus.read_sequence(0x27, 4)
        # Form that into a uint32.
        words = []
        for byte_list in byte_lists:
            w = 0
            for b in byte_list:
                w = (w << 8) | b
            words.append(w)
        bus.last_reads = words

    # Devices: print data.
    for name,_,_ in devices:
        i2c, index = signals[name]
        d = i2c.last_reads[index]
        stat, h, t = decode_ht(d)
        write('%8i %-8s' % (time.time(), name) +  '0x%08x stat= %i h= %7.3f t= %7.3f' % (d, stat, h, t))

    time.sleep(DELAY)



