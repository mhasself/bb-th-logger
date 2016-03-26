import time, os, sys

MEAS_DELAY = 2.

DEV_PATTERN = '/sys/bus/w1/devices/{device}/w1_slave'
DEV_FILE = 'devices.txt'

DATA_FILE = '/root/data/T_data.txt'

def init_w1_cape():
    f = open('/sys/devices/bone_capemgr.9/slots', 'a')
    try:
        f.write('BB-W1:00A0')
        f.flush()
    except IOError as e:
        if e.errno != 17: # 'File Exists' is raised if the cape is already init'd.
            raise e

def get_known_devices():
    return [l.strip() for l in open('devices.txt') if len(l)>0]

def update_device_list():
    import glob
    nows = glob.glob(DEV_PATTERN.format(device='*'))
    known = get_known_devices()
    any_news = False
    for d in nows:
        dev = d.split('/')[-2]
        if not dev in known:
            known.append(dev)
            any_news = True
    if any_news:
        fout = open('devices.txt', 'w')
        for d in sorted(known):
            fout.write('%s\n' % d)
        fout.close()

#init_w1_cape()
update_device_list()        
devices = []
for d in get_known_devices():
    if os.path.exists(DEV_PATTERN.format(device=d)):
        devices.append(d)

data_out = open(DATA_FILE, 'a')

while True:
    for d in devices:
        s = open(DEV_PATTERN.format(device=d), 'r').read()
        T = float(s.split('t=')[-1])/1000.
        text = '%i %s %6.3f' % (time.time(), d, T)
        data_out.write(text + '\n')
        print text
    time.sleep(MEAS_DELAY)

