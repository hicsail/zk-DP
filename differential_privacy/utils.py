from picozk import *
from nistbeacon import NistBeacon
from datetime import datetime


def get_beacon(p):
    beaconVal = NistBeacon.get_last_record()
    beacon_hex = beaconVal.output_value
    beacon = int(beacon_hex, 16) % p  # Convert hexadecimal string to integer
    now = datetime.now()
    print(" ", now, ":", beacon)
    return beacon

def xor(one, two):
    if len(one) > len(two):
        two = [0 for _ in range(len(one) - len(two))] + two
    elif len(one) < len(two):
        one = [0 for _ in range(len(two) - len(one))] + one
    assert len(one) == len(two)

    xor_ed = [0 for _ in range(len(one))]
    for i, (x, k) in enumerate(zip(one, two)):
        xor_ed[i] = mux(x - k == 0, 0, 1)
    return xor_ed