import unittest
from flightgear.flightgear import parse_property, parse_property_line

class FlightGearTest(unittest.TestCase):

    def test_parse_property(self):
        assert parse_property("10.0", "double") == 10.0
        assert parse_property("13", "int") == 13
        assert parse_property("true", "bool") is True

    def test_parse_property_line(self):
        line1 = "setting-hpa = '13.5' (double)"
        assert parse_property_line(line1) == ("setting-hpa", 13.5)
        line2 = "/controls/switches/starter = 'true' (bool)"
        assert parse_property_line(line2) == ("/controls/switches/starter", True)
