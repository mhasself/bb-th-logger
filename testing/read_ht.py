import time, os, sys
import subprocess as sp

def get_output(cmd):
    p = sp.Popen(cmd.split(), stdout=sp.PIPE, stderr=sp.PIPE)
    return p.communicate()

def method1():
    CMD = '/usr/sbin/i2cdump -y  1 0x27 i'
    out, err = get_output(CMD)
    lines = out.split('\n')
    data = lines[1].split()
    return [int(d, 16) for d in data[1:5]]

def method2():
    #CMD = './read_i2c'
    CMD = 'python bang_i2c.py %i %i' % (CLK, DAT)
    out, err = get_output(CMD)
    lines = out.split('\n')
    data = lines[1].split()
    return [int(d, 16) for d in data]

def go():
    bytes = method2()
    for b in bytes:
        print '{:08b}'.format(b),
    S = bytes[0] >> 6
    H0 = bytes[1]
    H1 = (bytes[0] & 0x3f) << 8
    T1 = bytes[2] << 6
    T0 = bytes[3] >> 2
    H = H0 | H1
    T = T0 | T1
    h = 100. * H / (2**14-2)
    t = 165. * T / (2**14-2) - 40
    print ' stat=%i  H=%3i   T=%3i  h=%.3f t=%.3f' % (S, H1, T1, h, t)
    return bytes


import optparse as o
o = o.OptionParser()
opts, args = o.parse_args()
CLK, DAT = int(args[0]), int(args[1])

go()
