from picozk import *
from picozk.poseidon_hash import PoseidonHash
from .des_module.triple_des import triple_DES
from .des_module.utils import bitlist_to_int, int_to_bitlist, xor
from .aes_module.aes import AES
from nistbeacon import NistBeacon
from datetime import datetime


def get_beacon(p):
    beaconVal = NistBeacon.get_last_record()
    beacon_hex = beaconVal.output_value
    beacon = int(beacon_hex, 16) % p  # Convert hexadecimal string to integer
    # now = datetime.now()
    # print(" ", now, ":", beacon)
    return beacon


class Poseidon_prf:
    def __init__(self, keys, p):
        if type(keys) != list:
            raise ValueError("Keys for Poseidon prf must be list")

        beacon = get_beacon(p)
        self.poseidon_hash = PoseidonHash(p, alpha=17, input_rate=3)
        self._key = self.poseidon_hash.hash(keys)
        self._key ^= beacon
        self.p = p

    def shrink_bits(self, prn, size):
        return bitlist_to_int(int_to_bitlist(prn, size))

    def run(self, i):
        prn = SecretInt(self.poseidon_hash.hash([i ^ self._key]) % self.p)
        return self.shrink_bits(prn, 13)


class TripleDES_prf:
    def __init__(self, keys, p):
        if type(keys) != list:
            raise ValueError("Keys for TripleDES must be list")

        beacon = get_beacon(p)  # Public Randomness
        poseidon_hash = PoseidonHash(p, alpha=17, input_rate=3)
        _keys = []

        for key in keys:
            _key = poseidon_hash.hash([key])  # Secret Randomness
            _key ^= beacon
            _keys.append(_key)
        self.prf_func = triple_DES(_keys)

    def shrink_bits(self, bit_list, size):
        bin_list = bit_list[:size]

        reduced_bits = 0
        for i in range(size - 1, -1, -1):
            reduced_bits += 2 ** (i) * bin_list[i]

        return reduced_bits

    def run(self, i):
        i = [int(x) for x in bin(i)[2:]]  # To binary list
        if len(i) < 64:
            i = [0 for _ in range(64 - len(i))] + i
        else:
            i = i[:64]
        assert len(i) == 64

        # Encryption
        _, seed_list = self.prf_func.encrypt(i)
        return self.shrink_bits(seed_list, 13)


class AES_prf:
    def __init__(self, key, p):
        if len(key) != 1:
            raise ValueError("Key for AES must be length of 1")

        beacon = get_beacon(p)  # Public Randomness
        poseidon_hash = PoseidonHash(p, alpha=17, input_rate=3)
        _key = poseidon_hash.hash(key)  # Secret Randomness
        _key ^= beacon
        self.prf_func = AES(_key)

    def shrink_bits(self, bit_list, size):
        bin_list = bit_list[:size]

        reduced_bits = 0
        for i in range(size - 1, -1, -1):
            reduced_bits += 2 ** (i) * bin_list[i]

        return reduced_bits

    def run(self, i):
        _, seed_list = self.prf_func.encrypt(i)
        return self.shrink_bits(seed_list, 13)
