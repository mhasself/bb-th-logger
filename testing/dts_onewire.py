TEMPLATE_BASE = """
/dts-v1/;
/plugin/;

/ {
  compatible = "ti,beaglebone", "ti,beaglebone-black", "ti,beaglebone-green";

  part-number = "PARTNAME";
  version = "00A0";

  /* state the resources this cape uses */
  exclusive-use =
    /* the pin header uses */
PINNAMES
    /* the hardware IP uses */
HARDWARE
  
DALLAS_FRAGS

  fragment@ONEWIREFRAG {
    target = <&ocp>;
    __overlay__ {
ONEWIRELETS
    };
  };
};
"""

DALLAS_FRAG = """
  fragment@FRAGNUM {
    target = <&am33xx_pinmux>;
    __overlay__ {
      dallas_w1_pinsFRAGNUM: pinmux_dallas_w1_pins {
        pinctrl-single,pins = < HWADDR 0x37 >;
      };
    };
  };"""

ONEWIRELET = """
      onewire@FRAGNUM {
        compatible = "w1-gpio";
        pinctrl-names   = "default";
        pinctrl-0       = <&dallas_w1_pinsFRAGNUM>;
        status          = "okay";
        gpios = <&GPIOCODE FRAGNUM>;
      };"""


## replace in the template:
# PARTNAME BB-W1
# PINNAME  P8.8
# HARDWARE GPIO2_3
# HWADDR 0x094
# GPIOCODE gpio3 3

## Use the pin database to get pin configs.  But they'll look like this:
##    ('BB-W1', 'P8.7', (2,2),    '0x090'),


import bbb_pins
pin_specs = [
     ('P8', 42), #L1
     ('P9', 41), #L2
     ('P9', 42), #L3
     ('P9', 24), #L4
     ('P9', 30), #L5
     ('P9', 27), #L6
     ('P8', 38), #L7
     ('P8', 18), #L8
     ('P9', 14), #L9
#    ('P9', 00), #L10
#    ('P8', 00), #L11   
     ('P8', 9), #L12
]

data = {'PARTNAME': 'BB-W30',
        'PINNAMES': [],
        'HARDWARE': [],
        'DALLAS_FRAGS': []}

drvs = []
for hdr, pin in pin_specs:
    dat = bbb_pins.get_pin(hdr, pin)
    drvs.append(('',
                 '%s.%i' % (hdr,dat['pin']),
                 (dat['gpio_bus'], dat['gpio_buspin']),
                 dat['addr']))

n_frag = len(drvs)
onews = []
for i, drv in enumerate(drvs):
    data['PINNAMES'].append(drv[1])
    data['HARDWARE'].append('gpio%d_%d' % drv[2])
    data['DALLAS_FRAGS'].append(DALLAS_FRAG\
            .replace('FRAGNUM', str(i))\
            .replace('HWADDR', drv[3]))
    onews.append(ONEWIRELET\
                     .replace('FRAGNUM', str(i))\
                     .replace('GPIOCODE', 'gpio%d %d' % (drv[2][0] + 1, drv[2][1])))

data['PINNAMES'] = ''.join(['    "%s",\n' % x for x in data['PINNAMES']])
data['HARDWARE'] = ',\n'.join(['    "%s"' % x for x in data['HARDWARE']]) + ';\n'
data['DALLAS_FRAGS'] = '\n'.join(data['DALLAS_FRAGS'])
data['ONEWIREFRAG'] = str(n_frag)
data['ONEWIRELETS'] = '\n'.join(onews)

fout = open('{PARTNAME}-00A0.dts'.format(**data), 'w')
output = TEMPLATE_BASE
for k, v in data.items():
    output = output.replace(k, v)

fout.write(output)
fout.close()
