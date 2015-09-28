import time
from flightgear import FGTelnet, FlightGear

def conn(func):
    def wrapped():
        with FGTelnet("localhost", "5401") as telnet:
            func(FlightGear(telnet))
    return wrapped

@conn
def read_data(fg):
    print(fg.indicated_roll_deg)
    print(fg.indicated_pitch_deg)
    print(fg.indicated_heading_deg)
    print(fg.engine_running)

@conn
def main(fg):
    fg.starter = True
    time.sleep(3)
    fg.starter = False
    fg.flaps = 0.5
    fg.rudder = 0.1
    fg.throttle = 1.0

if __name__ == "__main__":
    read_data()
