"""
  fileset: '/root/data/log_run00_%04i.txt'
"""

import os, time

class LogSetManager:
    def __init__(self, cfg):
        self.max_file_lines = cfg.get('max_file_lines', 100000)
        self.filename_format = cfg['filename_format']
        self.fout = None
        self.fout_index = None
        self.line_count = None
        self.uptime_t = None
        self.init_fout(startup=True)
    
    def write(self, text):
        if self.fout is None:
            self.init_fout()
        if self.line_count >= self.max_file_lines:
            self.init_fout(next_file=True)
        self.fout.write(text)
        self.line_count += text.count('\n')

    def tick(self):
        uptime_now = get_uptime()
        t_now = time.time()
        new_delta = t_now - uptime_now
        if self.uptime_t is None:
            self.write('X Setting uptime t_zero is %i\n' % new_delta)
        elif abs(self.uptime_t - new_delta) > 5:
                self.write('X Time shift detected; new uptime t_zero '
                           ' is %i\n' % new_delta)
        self.uptime_t = new_delta
        if t_now - self.t0 > 3600:
            self.fout.flush()
            self.t0 = t_now

    def init_fout(self, startup=False, next_file=False):
        if startup:
            # See what's already on disk here.
            last_file = None
            fout_i = 0
            while True:
                filename = self.filename_format % fout_i
                if not os.path.exists(filename):
                    break
                last_file = filename
                fout_i += 1
            self.fout_index = fout_i
        if next_file:
            self.fout_index += 1
        # Ok.
        if self.fout is not None:
            self.fout.close()
        new_file = self.filename_format % self.fout_index
        print 'New output file %s' % new_file
        if (os.path.exists(new_file)):
            print ' ... but that file exists!  Skipping forward.'
            return self.init_fout(next_file=True)
        self.fout = open(new_file, 'w')
        self.line_count = 0
        self.fout.write('X New file started at %i : %s\n' % (
                time.time(), time.asctime()))
        self.t0 = time.time()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        if self.fout is not None:
            self.fout.close()


def get_uptime():
    return float(open('/proc/uptime').readline().split()[0])
