import time
from flightgear import FlightGear, RxFlightGear
from rx import Observable
from rx.subjects import Subject
from rx.testing import marbles

def main():
    '''
    Will connect to a local flighgear via telnet and power up the
    engines. Works best with aircraft c172p.
    '''
    
    fg = RxFlightGear(FlightGear())
    starter = Subject()
    fg.starter(starter)
    fg.starter(
        Observable.from_marbles("0-1----------0|")
            .map(lambda x: bool(int(x)))
    )
    fg.flaps(Observable.from_([0.5]))
    fg.rudder(Observable.from_([0.1]))
    fg.throttle(Observable.from_([1.0]))

if __name__ == "__main__":
    main()
