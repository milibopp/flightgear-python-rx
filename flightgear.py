from telnetlib import Telnet
import sys
import socket
import re
from string import split, join
import time

__all__ = ["FlightGear"]

CRLF = '\r\n'


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

    def dump(self):
        """Dump current state as XML."""
        return self.send_command('dump')

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
        _i, _match, resp = Telnet.expect(self, self.prompt, self.timeout)
        return split(resp, '\n')[:-1]


def fg_property(path, converter=None):
    """FlightGear property for a given path"""
    converter = converter or (lambda x: x)
    def getter(self):
        return self[path]
    def setter(self, value):
        self[path] = converter(value)
    return property(getter, setter)


def print_bool(value):
    return "true" if value else "false"


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

    def __getitem__(self,key):
        """Get a FlightGear property value.
        Where possible the value is converted to the equivalent Python type.
        """
        s = self.telnet.get(key)[0]
        match = re.compile('[^=]*=\s*\'([^\']*)\'\s*([^\r]*)\r').match(s)
        if not match:
            return None
        value, data_type = match.groups()
        if value == '':
            return None

        if data_type == '(double)':
            return float(value)
        elif data_type == '(int)':
            return int(value)
        elif data_type == '(bool)':
            return value == 'true'
        else:
            return value

    def __setitem__(self, key, value):
        """Set a FlightGear property value."""
        self.telnet.set(key, value)

    def view_next(self):
        #move to next view
        self.telnet.set( "/command/view/next", "true")

    def view_prev(self):
        #move to next view
        self.telnet.set( "/command/view/prev", "true")

    starter = fg_property("/controls/switches/starter", print_bool)
