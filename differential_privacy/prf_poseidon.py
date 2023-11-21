from picozk import *
from picozk.poseidon_hash import PoseidonHash
from .utils import get_beacon

class Poseidon_prf:
    def __init__(self, keys, p):
        self.p = p
        self.keys = ZKList(keys)
        self.poseidon_hash = PoseidonHash(p, alpha=17, input_rate=3)


    # Generate a seed
    def generate_seed(self):
        seed = []
        for i, key in enumerate(self.keys):
            num1 = key.to_binary()
            num2 = get_beacon(self.p)
            seed.append((num1 ^ num2).to_arithmetic())
        return seed

    def run(self, i):
        seed = self.generate_seed()
        seed_h = self.poseidon_hash.hash(seed + [i])
        x = seed_h.to_binary()
        shifted_x = x >> 114
        return shifted_x.to_arithmetic()
