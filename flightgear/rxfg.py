from rx.subjects import Subject
from flightgear import FlightGear

__all__ = ["RxFlightGear"]

def poll(callback, delta):
    return Observable.timer(0, delta).map(lambda _: callback())


def wire_up_controller(fg, handle):
    def setter(value):
        setattr(fg, handle, value)
    switcher = Subject()
    switcher.switch_latest().subscribe(setter)
    return switcher


def expose_setter(handle):
    def setter(self, stream):
        getattr(self, handle).on_next(stream)
    return setter


class RxFlightGear(object):

    _setter_attrs = [
        "throttle", "starter", "rudder", "aileron", "elevator", "flaps"]

    def __init__(self, fg):
        self.fg = fg
        for name in RxFlightGear._setter_attrs:
            setattr(self, "_" + name, wire_up_controller(fg, name))

    for name in _setter_attrs:
        locals()[name] = expose_setter("_" + name)
