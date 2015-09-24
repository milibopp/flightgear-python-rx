import time
from flightgear import FGTelnet, FlightGear

with FGTelnet("localhost", "5401") as telnet:
    fg = FlightGear(telnet)
    fg.starter = True
    time.sleep(3)
    fg.starter = False
    fg.flaps = 0.5
    fg.rudder = 0.1
    fg.throttle = 1.0
