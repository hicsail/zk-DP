from picozk import *
from .utils import get_beacon
from .des_module.triple_des import triple_DES


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
