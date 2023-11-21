from picozk import *
from picozk.poseidon_hash import PoseidonHash
from .des_module.triple_des import triple_DES
from .des_module.utils import list_to_binary, int_to_bitlist, xor
from nistbeacon import NistBeacon
from datetime import datetime


def get_beacon(p):
    beaconVal = NistBeacon.get_last_record()
    beacon_hex = beaconVal.output_value
    beacon = int(beacon_hex, 16) % p  # Convert hexadecimal string to integer
    now = datetime.now()
    print(" ", now, ":", beacon)
    return beacon


class Poseidon_prf:
    def __init__(self, keys, p):
        self.p = p
        self.keys = ZKList(keys)
        self.poseidon_hash = PoseidonHash(p, alpha=17, input_rate=3)

    def shrink_bits(self, seed_h, size):
        pow = round(math.log(self.p + 1, 2))
        x = int_to_bitlist(seed_h, pow)
        return list_to_binary(x[0:size])

    def generate_seed(self):
        seed = []
        beacon = get_beacon(self.p)
        beacon = [int(x) for x in bin(beacon)[2:]]
        for key in self.keys:
            size = round(math.log(self.p + 1, 2))
            bi_num = int_to_bitlist(key, size)
            xored = xor(bi_num, beacon)
            int_xored = list_to_binary(xored)
            seed.append(int_xored)

            test = val_of(key)
            test_obj = val_of(list_to_binary(bi_num))
            assert test == test_obj
        return seed

    def run(self, i):
        seed = self.generate_seed()

        # Encryption
        seed_h = self.poseidon_hash.hash(seed + [i])
        return self.shrink_bits(seed_h, 13)


class TripleDES_prf:
    def __init__(self, keys, p):
        self.p = p
        self.prf_func = triple_DES(keys)

    def shrink_bits(self, bit_list, size):
        bin_list = bit_list[:size]

        reduced_bits = 0
        for i in range(size - 1, -1, -1):
            reduced_bits += 2 ** (i) * bin_list[i]

        return reduced_bits

    def generate_seed(self, i):
        return get_beacon(self.p) ^ i

    def run(self, i):
        beacon = self.generate_seed(i)
        beacon = [int(x) for x in bin(beacon)[2:]]  # To binary list
        if len(beacon) < 64:
            beacon = [0 for _ in range(64 - len(beacon))] + beacon
        else:
            beacon = beacon[:64]
        assert len(beacon) == 64

        # Encryption
        _, seed_list = self.prf_func.encrypt(beacon)
        return self.shrink_bits(seed_list, 13)
