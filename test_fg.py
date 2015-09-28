from flightgear import *

def test_parse_property():
    assert parse_property("10.0", "double") == 10.0
    assert parse_property("13", "int") == 13
    assert parse_property("true", "bool") is True

def test_parse_property_line():
    line1 = "/controls/flight/rudder = '0.5' (double)"
    assert parse_property_line(line1) == 0.5
    line2 = "/controls/switches/starter = 'true' (bool)"
    assert parse_property_line(line2) is True
