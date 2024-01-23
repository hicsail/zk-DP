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
    now = datetime.now()
    print(" ", now, ":", beacon)
    return beacon


class Poseidon_prf:
    def __init__(self, keys, p):
        self.p = p
        self.keys = [SecretInt(key) for key in keys]
        self.poseidon_hash = PoseidonHash(p, alpha=17, input_rate=3)

    def shrink_bits(self, seed_h, size):
        x = seed_h.to_binary()
        shift = len(x.wires) - size
        shifted_x = x >> shift
        return shifted_x.to_arithmetic()

    def generate_seed(self):
        seed = []
        beacon = get_beacon(self.p)
        for key in self.keys:
            bi_key = key.to_binary()
            seed.append((bi_key ^ beacon).to_arithmetic())
        return seed

    def run(self, i):
        seed = self.generate_seed()

        # Encryption
        seed_h = self.poseidon_hash.hash(seed + [i])
        return self.shrink_bits(seed_h, 13)


class Poseidon_prf_no_fieldswicth:
    def __init__(self, keys, p):
        self.p = p
        self.keys = [SecretInt(key) for key in keys]
        self.poseidon_hash = PoseidonHash(p, alpha=17, input_rate=3)

    def shrink_bits(self, seed_h, size):
        pow = round(math.log(self.p + 1, 2))
        x = int_to_bitlist(seed_h, pow)
        return bitlist_to_int(x[0:size])

    def generate_seed(self):
        seed = []
        beacon = get_beacon(self.p)
        beacon = [int(x) for x in bin(beacon)[2:]]
        for key in self.keys:
            size = round(math.log(self.p + 1, 2))
            bi_key = int_to_bitlist(key, size)
            xored = xor(bi_key, beacon)
            int_xored = bitlist_to_int(xored)
            seed.append(int_xored)

            test = val_of(key)
            test_obj = val_of(bitlist_to_int(bi_key))
            assert test == test_obj
        return seed

    def run(self, i):
        seed = self.generate_seed()

        # Encryption
        seed_h = self.poseidon_hash.hash(seed + [i])
        return self.shrink_bits(seed_h, 13)


class TripleDES_prf:
    def __init__(self, keys, p):
        if type(keys) != list:
            raise ValueError("Keys for TripleDES must be list")
        self.p = p
        poseidon_hash = PoseidonHash(p, alpha=17, input_rate=3)
        _keys = []
        beacon = get_beacon(p) # Public Randomness
        for key in keys:
            _key = poseidon_hash.hash([key]) # Secret Randomness
            _key^= beacon
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
        beacon = get_beacon(p) # Public Randomness
        self.p = p
        poseidon_hash = PoseidonHash(p, alpha=17, input_rate=3) 
        _key = poseidon_hash.hash(key) # Secret Randomness
        _key^= beacon
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
