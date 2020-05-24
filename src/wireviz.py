from graphviz import Graph

COLOR_CODES = {'DIN': ['WH','BN','GN','YE','GY','PK','BU','RD','BK','VT'], # ,'GYPK','RDBU','WHGN','BNGN','WHYE','YEBN','WHGY','GYBN','WHPK','PKBN'],
               'IEC': ['BN','RD','OG','YE','GN','BU','VT','GY','WH','BK'],
               'BW':  ['BK','WH']}

# TODO: parse and render double-colored cables ('RDBU' etc)
color_hex = {
             'BK': '#000000',
             'WH': '#ffffff',
             'GY': '#808080',
             'PK': '#ff80c0',
             'RD': '#ff0000',
             'OG': '#ff8000',
             'YE': '#ffff00',
             'GN': '#00ff00',
             'TQ': '#00ffff',
             'BU': '#0000ff',
             'VT': '#8000ff',
             'BN': '#666600',
              }

color_full = {
             'BK': 'black',
             'WH': 'white',
             'GY': 'grey',
             'PK': 'pink',
             'RD': 'red',
             'OG': 'orange',
             'YE': 'yellow',
             'GN': 'green',
             'TQ': 'turquoise',
             'BU': 'blue',
             'VT': 'violet',
             'BN': 'brown',
}

color_ger = {
             'BK': 'sw',
             'WH': 'ws',
             'GY': 'gr',
             'PK': 'rs',
             'RD': 'rt',
             'OG': 'or',
             'YE': 'ge',
             'GN': 'gn',
             'TQ': 'tk',
             'BU': 'bl',
             'VT': 'vi',
             'BN': 'br',
}

class Harness:

    def __init__(self):
        self.color_mode = 'SHORT'
        self.nodes = {}
        self.cables = {}

    def add_node(self, name, type=None, gender=None, show_name=True, num_pins=None, pinout=None, ports_left=False, ports_right=False):
        self.nodes[name] = Node(name, type, gender, show_name, num_pins, pinout, ports_left, ports_right)

    def add_cable(self, name, mm2=None, awg=None, show_equiv=False, length=0, show_name=False, show_pinout=False, num_wires=None, colors=None, color_code=None, shield=False):
        self.cables[name] = Cable(name, mm2, awg, show_equiv, length, show_name, show_pinout, num_wires, colors, color_code, shield)

    def loop(self, node_name, from_pin, to_pin, side=None):
        self.nodes[node_name].loop(from_pin, to_pin, side)

    def connect(self, cable_name, from_name, from_pin, via, to_name, to_pin):
        self.cables[cable_name].connect(from_name, from_pin, via, to_name, to_pin)

    def connect_all_straight(self, cable_name, from_name, to_name):
        self.cables[cable_name].connect_all_straight(from_name, to_name)

    def create_graph(self):
        dot = Graph()
        font = 'arial'
        dot.attr('graph', rankdir='LR', ranksep='2', bgcolor='transparent', fontname=font)
        dot.attr('node', shape='record', style='rounded,filled', fillcolor='white', fontname=font)
        dot.attr('edge', style='bold', fontname=font)

        for k in self.nodes:
            n = self.nodes[k]
            # a = attributes
            a = [n.type, n.gender, '{}-pin'.format(len(n.pinout))]
            # p = pinout
            p = [[],[],[]]
            p[1] = list(n.pinout)
            for i,x in enumerate(n.pinout, 1):
                if n.ports_left == True:
                    p[0].append('<p{portno}>{portno}'.format(portno=i))
                if n.ports_right == True:
                    p[2].append('<p{portno}>{portno}'.format(portno=i))
            # l = label
            l = [n.name if n.show_name == True else '', a, p]
            dot.node(k, label=nested(l))

            for x in n.loops:
                dot.edge('{name}:p{port_from}:{loop_side}'.format(name=n.name, port_from=x[0], port_to=x[1], loop_side=x[2]),
                         '{name}:p{port_to}:{loop_side}'.format(name=n.name, port_from=x[0], port_to=x[1], loop_side=x[2]))

        for k in self.cables:
            c = self.cables[k]
            # a = attributes
            a = ['{}x'.format(len(c.colors)),
                 '{} mm\u00B2{}'.format(c.mm2, ' ({} AWG)'.format(awg_equiv(c.mm2)) if c.show_equiv == True else ''),
                 c.awg,
                 '+ S' if c.shield == True else '',
                 '{} m'.format(c.length)]
            # p = pinout
            p = [[],[],[]]
            for i,x in enumerate(c.colors,1):
                if c.show_pinout:
                    p[0].append('<w{wireno}i>{wireno}'.format(wireno=i))
                    p[1].append('{wirecolor}'.format(wirecolor=translate_color(x, self.color_mode)))
                    p[2].append('<w{wireno}o>{wireno}'.format(wireno=i))
                else:
                    p[1].append('<w{wireno}>{wirecolor}'.format(wireno=i,wirecolor=translate_color(x, self.color_mode)))
            if c.shield == True:
                if c.show_pinout:
                    p[0].append('<wsi>')
                    p[1].append('Shield')
                    p[2].append('<wso>')
                else:
                    p[1].append('<ws>Shield')
            # l = label
            l = [c.name if c.show_name == True else '', a, p]
            dot.node(k, label=nested(l))

            # connections
            for x in c.connections:
                if isinstance(x[2], int): # check if it's an actual wire and not a shield
                    search_color = c.colors[x[2]-1]
                    if search_color in color_hex:
                        dot.attr('edge',color='#000000:{wire_color}:#000000'.format(wire_color=color_hex[search_color]))
                    else: # color name not found
                        dot.attr('edge',color='#000000')
                else: # it's a shield connection
                    dot.attr('edge',color='#000000')
                if x[1] is not None: # connect to left
                    dot.edge('{from_name}:p{from_port}'.format(from_name=x[0],from_port=x[1]),
                             '{via_name}:w{via_wire}{via_subport}'.format(via_name=c.name, via_wire=x[2], via_subport='i' if c.show_pinout == True else ''))
                if x[4] is not None: # connect to right
                    dot.edge('{via_name}:w{via_wire}{via_subport}'.format(via_name=c.name, via_wire=x[2], via_subport='o' if c.show_pinout == True else ''),
                             '{to_name}:p{to_port}'.format(to_name=x[3], to_port=x[4]))

        return dot

    def output(self, filename, format='pdf', view=True):
        d = self.create_graph()
        d.format = format
        d.render(filename, view=view)

class Node:

    def __init__(self, name, type=None, gender=None, show_name=True, num_pins=None, pinout=None, ports_left=False, ports_right=False):
        self.name = name
        self.type = type
        self.gender = gender
        self.show_name = show_name
        self.ports_left = ports_left
        self.ports_right = ports_right
        self.loops = []

        if pinout is None:
            self.pinout = ('',) * num_pins
        else:
            if num_pins is None:
                if pinout is None:
                    raise Exception('Must provide num_pins or pinout')
                else:
                    self.pinout = pinout

    def loop(self, from_pin, to_pin, side=None):
        if self.ports_left == True and self.ports_right == False:
            loop_side = 'w' # west = left
        elif self.ports_left == False and self.ports_right == True:
            loop_side = 'e' # east = right
        elif self.ports_left == True and self.ports_right == True:
            if side == None:
                raise Exception('Must specify side of loop')
            else:
                loop_side = side
        self.loops.append((from_pin, to_pin, loop_side))

class Cable:

    def __init__(self, name, mm2=None, awg=None, show_equiv=False, length=0, show_name=False, show_pinout=False, num_wires=None, colors=None, color_code=None, shield=False):
        self.name = name
        if mm2 is not None and awg is not None:
            raise Exception('You cannot define both mm2 and awg!')
        self.mm2 = mm2
        self.awg = awg
        self.show_equiv = show_equiv
        self.length = length
        self.show_name = show_name
        self.show_pinout = show_pinout
        self.shield = shield
        self.connections = []
        if color_code is None and colors is None:
            self.colors = ('',) * num_wires
        else:
            if colors is None: # no custom color pallet was specified
                if num_wires is None:
                    raise Exception('Unknown number of wires')
                else:
                    if color_code is None:
                        raise Exception('No color code')
                    # choose color code
                    if color_code not in COLOR_CODES:
                        raise Exception('Unknown color code')
                    else:
                        cc = COLOR_CODES[color_code]
                n = num_wires
            else: # custom color pallet was specified
                cc = colors
                if num_wires is None: # assume number of wires = number of items in custom pallet
                    n = len(cc)
                else: # number of wires was specified
                    n = num_wires

            cc = tuple(cc)
            if n > len(cc):
                 m = num_wires // len(cc) + 1
                 cc = cc * int(m)
            self.colors = cc[:n]

    def connect(self, from_name, from_pin, via, to_name, to_pin):
        if from_pin == 'auto':
            from_pin = tuple(x+1 for x in range(len(self.colors)))
        if via == 'auto':
            via = tuple(x+1 for x in range(len(self.colors)))
        if to_pin == 'auto':
            to_pin = tuple(x+1 for x in range(len(self.colors)))
        if len(from_pin) != len(to_pin):
            raise Exception('from_pin must have the same number of elements as to_pin')
        for i, x in enumerate(from_pin):
            self.connections.append((from_name, from_pin[i], via[i], to_name, to_pin[i]))

    def connect_all_straight(self, from_name, to_name):
        self.connect(from_name, 'auto', 'auto', to_name, 'auto')

def nested(input):
    l = []
    for x in input:
        if isinstance(x, list):
            if len(x) > 0:
                l.append('{' + nested(x) + '}')
        else:
            if x is not None:
                if x != '':
                    l.append(str(x))
    s = '|'.join(l)
    return s

def translate_color(input, color_mode):
    if input == '':
        output = ''
    else:
        if color_mode == 'full':
            output = color_full[input].lower()
        elif color_mode == 'FULL':
            output = color_hex[input].upper()
        elif color_mode == 'hex':
            output = color_hex[input].lower()
        elif color_mode == 'HEX':
            output = color_hex[input].upper()
        elif color_mode == 'ger':
            output = color_ger[input].lower()
        elif color_mode == 'GER':
            output = color_ger[input].upper()
        elif color_mode == 'short':
            output = input.lower()
        elif color_mode == 'SHORT':
            output = input.upper()
        else:
            raise Exception('Unknown color mode')
    return output

def awg_equiv(mm2):
    awg_equiv_table = {
                        '0.09': 28,
                        '0.14': 26,
                        '0.25': 24,
                        '0.34': 22,
                        '0.5': 21,
                        '0.75': 20,
                        '1': 18,
                        '1.5': 16,
                        '2.5': 14,
                        '4': 12,
                        '6': 10,
                        '10': 8,
                        '16': 6,
                        '25': 4,
                        }
    k = str(mm2)
    if k in awg_equiv_table:
        return awg_equiv_table[k]
    else:
        return None
