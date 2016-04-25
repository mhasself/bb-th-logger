#Note that the table data were slightly reformatted so columns don't overlap.
import os
PATH = os.path.split(__file__)[0] + '/'
tables = [(1,   -2, 'P8', 'beaglebone_pins_p8'),
          (1, None, 'P9', 'beaglebone_pins_p9'),
          ]
table_format = [
    ( 0,    2,  0,    2, 'bp'),
    (-1,   10, -1,   10, 'pin'),
    (-1,   22, -1,   23, 'proc'),
    (-1,   32, -1,   36, 'addr'),
    (-1,   52, -1,   56, 'name'),
    (-1,   70, -1,   74, 'mode0'),
    (-1,   88, -1,   90, 'mode1'),
    (-1,  108, -1,  107, 'mode2'),
    (-1,  127, -1,  135, 'mode3'),
    (-1,  146, -1,  152, 'mode4'),
    (-1,  162, -1,  167, 'mode5'),
    (-1,  184, -1,  189, 'mode6'),
    (-1,   -1, -1,   -1, 'mode7'),
]

HEADERS = {}

for table_row in tables:
    line_start, line_stop, hdr, filename = table_row
    HEADERS[hdr] = {}
    lines = open(PATH + filename).readlines()
    lines = lines[line_start:line_stop]
    text_data = []
    start = 0
    for fmt in table_format:
        if hdr == 'P8':
            new_start, new_end = fmt[:2]
        else:
            new_start, new_end = fmt[2:4]
        if new_start == -1:
            start = end
        else:
            start = new_start
        if new_end == -1:
            end = None
        else:
            end = new_end
        ext = []
        for line in lines:
            if line[-1] == '\n':
                line = line[:-1]
            ext.append(line[start:end])
        text_data.append(ext)

    for fmt, data in zip(table_format, text_data):
        name = fmt[-1]
        HEADERS[hdr][name] = [d.strip() for d in data]

# Now generate metadata...
for data in HEADERS.values():
    gpio_buspin = []
    for gpio in data['mode7']:
        if gpio.startswith('gpio'):
            b = int(gpio[4])
            p = int(gpio[6:-1])
            gpio_buspin.append((b*32+p, b, p))
        else:
            gpio_buspin.append((-1, -1,-1))
    data['gpio'], data['gpio_bus'], data['gpio_buspin'] = zip(*gpio_buspin)
    # Type convert some stuff.
    for k in ['pin']:
        data[k] = map(int, data[k])

def dump(i):
    # Utility... for column debugging.
    f = '|%%-%is|' % max(map(len, text_data[i]))
    for j,x in enumerate(text_data[i]):
        print f % x,
        if (j+1) % 3 == 0:
            print
    print

# Decoding functions.

def get_pin(header, number=None):
    if number is None:
        header, number = header.split('.')
        number = int(number)
    i = HEADERS[header]['pin'].index(number)
    return dict([('header', header)] +
                [(k,v[i]) for k,v in HEADERS[header].items()])

def get_gpio(gpio):
    for hdr, data in HEADERS.items():
        if gpio in data['gpio']:
            return hdr, data['pin'][data['gpio'].index(gpio)]
    return None, None
