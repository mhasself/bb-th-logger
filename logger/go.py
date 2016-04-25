import bb_th_lib as btl
import time, os, sys, glob

import optparse as o
o = o.OptionParser()
o.add_option('--managed',action='store_true')
o.add_option('-c', '--config-file', default='config.jso')
o.add_option('--test', action='store_true')
opts, args = o.parse_args()

cfg = btl.config.load_json(opts.config_file)

mgr = cfg.get('manager', {})
if not opts.managed and mgr.get('on'):
    # Relaunch myself, in a loop.
    relaunch_t = mgr.get('retry_period', 60)
    while True:
        t0 = time.time()
        os.system('python %s --managed -c %s' % (
                sys.argv[0], opts.config_file))
        t1 = time.time()
        if t1 - t0 < relaunch_t:
            time.sleep(relaunch_t - (t1-t0))

# Set up the sensor management objects.  Re-init the t_sensors every
# so often.
lcfg = cfg['logging']

t_sens = ht_sens = None
if 'onewire_t' in lcfg['modules']:
    t_sens = btl.config.TSensorSet.from_cfg_list(cfg['onewire_t'])
if 'i2c_ht' in lcfg['modules']:
    ht_sens = btl.config.HTSensorSet.from_cfg_list(cfg['i2c_ht'])

log_period = lcfg.get('log_period')
with btl.logging.LogSetManager(lcfg) as lsm:
    while True:
        # Full log cycle begins.
        lsm.tick()
        t0 = time.time()
        if ht_sens is not None:
            ht_vals = ht_sens.get_values()
            for k in ht_sens.sens_names:
                line = ('A %i %-20s' % (int(t0),k) +
                          '%i %8.3f %8.3f\n' % (ht_vals[k]))
                if opts.test:
                    print line,
                else:
                    lsm.write(line)
        if t_sens is not None:
            t_vals = t_sens.get_values()
            for k, v in t_vals:
                line = ('B %i %-20s %8.4f\n' % (int(t0), k, v))
                if opts.test:
                    print line,
                else:
                    lsm.write(line)
        t1 = time.time()
        time.sleep(max(0, log_period - (t1-t0)))
        if opts.test:
            break
