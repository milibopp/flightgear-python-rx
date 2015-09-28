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


def fg_readonly(path):
    """FlightGear read-only property for given path"""
    def getter(self):
        return self[path]
    return property(getter)


def print_bool(value):
    return "true" if value else "false"


property_line_pattern = re.compile('[^=]*=\s*\'([^\']*)\'\s*\(([^\r]*)\)')

def parse_property_line(line):
    match = property_line_pattern.match(line)
    if match:
        value, data_type = match.groups()
        return parse_property(value, data_type)


class FlightGear(object):
    """FlightGear interface class.

    An instance of this class represents a connection to a FlightGear telnet
    server.

    Properties are accessed using a dictionary style interface:
    For example:

    # Connect to flightgear telnet server.
    fg = FlightGear('myhost', 5500)
    # parking brake on
    fg['/controls/gear/brake-parking'] = 1
    # Get current heading
    heading = fg['/orientation/heading-deg']

    Other non-property related methods

    """

    def __init__(self, telnet):
        self.telnet = telnet

    def __getitem__(self, key):
        """Get a FlightGear property value"""
        return parse_property_line(self.telnet.get(key)[0])

    def __setitem__(self, key, value):
        """Set a FlightGear property value"""
        self.telnet.set(key, value)

    def view_next(self):
        #move to next view
        self.telnet.set( "/command/view/next", "true")

    def view_prev(self):
        #move to next view
        self.telnet.set( "/command/view/prev", "true")

    starter = fg_readwrite("/controls/switches/starter", print_bool)
    rudder = fg_readwrite("/controls/flight/rudder")
    flaps = fg_readwrite("/controls/flight/flaps")
    throttle = fg_readwrite("/controls/engines/engine/throttle")

    @property
    def position(self):
        return self.telnet.dump("/position")
