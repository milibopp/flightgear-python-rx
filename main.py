from flightgear import FGTelnet, FlightGear

with FGTelnet("localhost", "5401") as telnet:
    fg = FlightGear(telnet)
    fg.starter = True
