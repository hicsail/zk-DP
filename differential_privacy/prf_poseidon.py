from picozk import *
from picozk.poseidon_hash import PoseidonHash
from .utils import get_beacon


class Poseidon_prf:
    def __init__(self, keys, p):
        self.p = p
        self.keys = ZKList(keys)
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
            bi_num1 = key.to_binary()
            seed.append((bi_num1 ^ beacon).to_arithmetic())
        return seed

    def run(self, i):
        seed = self.generate_seed()

        # Encryption
        seed_h = self.poseidon_hash.hash(seed + [i])
        return self.shrink_bits(seed_h, 13)
