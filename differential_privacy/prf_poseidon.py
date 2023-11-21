from picozk import *
from picozk.poseidon_hash import PoseidonHash
from .des_module.utils import get_beacon, list_to_binary, int_to_bitlist, xor


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
        return seed

    def run(self, i):
        seed = self.generate_seed()

        # Encryption
        seed_h = self.poseidon_hash.hash(seed + [i])
        return self.shrink_bits(seed_h, 13)
