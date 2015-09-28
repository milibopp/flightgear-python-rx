from telnetlib import Telnet
import sys
import socket
import re
from string import split, join
import time
import xml.etree.ElementTree as etree

CRLF = '\r\n'

readers = {
    "double": float,
    "int": int,
    "bool": lambda s: s == "true",
}

def parse_property(prop, type_desc):
    return readers.get(type_desc, lambda s: s)(prop)


class FGTelnet(Telnet):
    def __init__(self, host="localhost", port="5401"):
        Telnet.__init__(self, host, port)
        self.prompt = [re.compile('/[^>]*> ')]
        self.timeout = 5

    def __enter__(self):
        return self

    def __exit__(self, _type, _value, _traceback):
        self.close()

    def ls(self, directory=None):
        """Returns a list of properties"""
        return self.send_command(
            'ls {}'.format(directory) if directory else 'ls')

    def dump(self, path=None):
        """Dump current state as XML."""
        resp = self.send_command('dump ' + (path or ""))
        root = etree.fromstring("".join(resp))
        return {
            elem.tag: parse_property(elem.text, elem.attrib["type"])
            for elem in root
        }

    def cd(self, directory):
        """Change directory."""
        self.send_command('cd ' + directory)

    def pwd(self):
        """Display current path."""
        return self.send_command('pwd')

    def get(self, var):
        """Retrieve the value of a parameter."""
        return self.send_command('get %s' % var )

    def set(self, var, value):
        """Set variable to a new value"""
        self.send_command('set %s %s' % (var, value))

    def quit(self):
        """Terminate connection"""
        self.send_command('quit')
        self.close()
    
    def send_command(self, cmd):
        cmd = cmd + CRLF;
        Telnet.write(self, cmd)
        return self.get_response()

    def get_response(self):
        _i, _match, resp = self.expect(self.prompt, self.timeout)
        return split(resp, "\n")[:-1]


def fg_readwrite(path, converter=None):
    """FlightGear property for a given path"""
    converter = converter or (lambda x: x)
    def getter(self):
        return self[path]
    def setter(self, value):
        self[path] = converter(value)
    return property(getter, setter)


def fg_readonly_dump(path):
    """FlightGear read-only property for given path"""
    def getter(self):
        return self.telnet.dump(path)
    return property(getter)

def fg_readonly_ls(path, prop_name):
    def getter(self):
        for line in self.telnet.ls(path):
            match = parse_property_line(line)
            if not match:
                continue
            name, value = match
            if name == prop_name:
                return value
    return property(getter)


def print_bool(value):
    return "true" if value else "false"


property_line_pattern = re.compile('([^=]*)=\s*\'([^\']*)\'\s*\(([^\r]*)\)')

def parse_property_line(line):
    match = property_line_pattern.match(line)
    if match:
        name, value, data_type = match.groups()
        return name.strip(), parse_property(value, data_type)


class FlightGear(object):
    """Convenient FlightGear interface class"""

    def __init__(self, telnet):
        self.telnet = telnet

    def __getitem__(self, key):
        _, value = parse_property_line(self.telnet.get(key)[0])
        return value

    def __setitem__(self, key, value):
        self.telnet.set(key, value)

    def view_next(self):
        self.telnet.set("/command/view/next", "true")

    def view_prev(self):
        self.telnet.set("/command/view/prev", "true")

    starter = fg_readwrite("/controls/switches/starter", print_bool)
    rudder = fg_readwrite("/controls/flight/rudder")
    aileron = fg_readwrite("/controls/flight/aileron")
    elevator = fg_readwrite("/controls/flight/elevator")
    flaps = fg_readwrite("/controls/flight/flaps")
    throttle = fg_readwrite("/controls/engines/engine/throttle")

    position = fg_readonly_dump("/position")
    orientation = fg_readonly_dump("/orientation")
    velocities = fg_readonly_dump("/velocities")

    indicated_altitude_ft = fg_readonly_ls(
        "/instrumentation/altimeter", "indicated-altitude-ft")
    indicated_airspeed_kt = fg_readonly_ls(
        "/instrumentation/airspeed-indicator", "indicated-speed-kt")
    indicated_roll_deg = fg_readonly_ls(
        "/instrumentation/attitude-indicator", "indicated-roll-deg")
    indicated_pitch_deg = fg_readonly_ls(
        "/instrumentation/attitude-indicator", "indicated-pitch-deg")
    indicated_heading_deg = fg_readonly_ls(
        "/instrumentation/magnetic-compass", "indicated-heading-deg")
    engine_running = fg_readonly_ls("/engines/engine", "running")
