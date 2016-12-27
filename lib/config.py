import json
import time
import glob
import os
import threading

import gp_i2c
import dts_onewire

def load_json(filename):
    # This strips out lines whose first non-whitespace character is a #.
    lines = ''.join([l for l in open(filename) if (l.strip()+'#')[0] != '#'])
    try:
        cfg = json.loads(lines)
    except Exception as e:
        print lines
        raise e
    return cfg

class I2CSensorSet(object):
    @classmethod
    def from_cfg_list(cls, cfg_list):
        buses = {}
        sens_map = {}
        sens_names = []
        for c in cfg_list:
            name, clk, dat = c
            if name in sens_map:
                raise ValueError, "Duplicate signal name '%s'" % name
            if not (clk in buses):
                buses[clk] = []
            sens_names.append(name)
            sens_map[name] = (clk, len(buses[clk]))
            buses[clk].append(dat)
        for k in buses.keys():
            buses[k] = gp_i2c.I2CGang(k, buses[k])
        self = cls()
        self.buses = buses
        self.sens_map = sens_map
        self.sens_names = sens_names
        return self

class HTSensorSet(I2CSensorSet):
    def get_values(self):
        bus_keys = self.buses.keys()
        # Trigger acquisition...
        for k in bus_keys:
            self.buses[k].write_sequence(0x27, 0, 0)
        # Wait
        time.sleep(0.1)
        results = {}
        for k in bus_keys:
            # Get 4 bytes from each device...
            byte_lists = self.buses[k].read_sequence(0x27, 4)
            # Reform into 32-bit words and decode.
            results[k] = []
            for bl in byte_lists:
                w = 0
                for b in bl:
                    w = (w << 8) | b
                results[k].append(self.decode_ht(w))
        # Now associate results to sens instead of bus.
        sens_results = {}
        for sens_name in self.sens_map.keys():
            bus, idx = self.sens_map[sens_name]
            sens_results[sens_name] = results[bus][idx]
        return sens_results
        #stat, h, t = decode_ht(d)
        #write('%8i %-8s' % (time.time(), name) +  '0x%08x stat= %i h= %7.3f t= %7.3f' % (d, stat, h, t))
        
    @staticmethod
    def decode_ht(d):
        """
        Decode the 32-bit word returned by the HT sensor.
        """
        status = (d >> 30) & 0x3
        H = (d>>16) & 0x3fff
        T = (d>> 2) & 0x3fff
        h = 100. * H / (2**14-2)
        t = 165. * T / (2**14-2) - 40
        return status, h, t

class TThread(threading.Thread):
    def __init__(self, device, **kwargs):
        threading.Thread.__init__(self, **kwargs)
        self.device = device
    def run(self):
        self.data = None
        try:
            T = open(self.device+'/w1_slave').readlines()[1].split('=')[1]
            self.data = float(T)/1000.
        except:
            self.data = -100

class TSensorSet(object):
    def __init__(self, dev_glob):
        self.dev_glob = dev_glob
        
    def rescan(self):
        devs = glob.glob(self.dev_glob)
        self.devices = sorted(devs)
        self.dev_names = [x.split('/')[-1] for x in self.devices]

    @classmethod
    def from_cfg_list(cls, ow_cfg):
        capeman = CapeManagerInterface()
        dts = dts_onewire.get_overlay_text(
            ow_cfg['dts_name'], ow_cfg['pin_list'])
        capeman.load_as(dts, ow_cfg['dts_name'])
        return cls('/sys/bus/w1/devices/28-*')

    def get_values(self):
        self.rescan()
        threads = [TThread(d) for d in self.devices]
        [t.start() for t in threads]
        [t.join(1) for t in threads]
        data = [t.data for t in threads]
        return zip(self.dev_names, data)

class CapeManagerInterface(object):
    def __init__(self):
        slots = glob.glob('/sys/devices/bone_capemgr.*/slots')
        assert(len(slots) == 1)
        self.slotfile = slots[0]
    def get_parsed(self):
        data = []
        for line in open(self.slotfile):
            idx, text = line.split(':', 1)
            idx = int(idx)
            text = text.strip()
            try:
                name_i = text.index(' ')
                codes, name = text[:name_i], text[name_i:].strip()
            except:
                codes, name = text.strip(), ''
            data.append((idx, codes, name))
        return data
    def load_as(self, dts_text, fw_name, fw_ver='00A0'):
        import subprocess as sp
        output_file = '/lib/firmware/%s-%s.dtbo' % (fw_name, fw_ver)
        # Compile it 
        P = sp.Popen(['/usr/bin/dtc',
                      '-O', 'dtb',
                      '-o', output_file,
                      '-b', '0',
                      '-@'], stderr=sp.PIPE, stdin=sp.PIPE)
        P.stdin.write(dts_text)
        P.communicate()
        assert os.path.exists(output_file)
        open(self.slotfile, 'a').write(fw_name)
        
        
