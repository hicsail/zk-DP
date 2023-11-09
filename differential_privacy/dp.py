from picozk import *
from picozk.poseidon_hash import PoseidonHash
from .laplase import gen_laplace_table
import random


def run(sdf, p):
    """
    Time1: A prover commits a data and a key and generate a private key
    Time2: A beacon generates a random integer-string, x
    Time3: Seed = PRF(k, x)

    Proof:
        - Pub_data (Modified Sensus Data)
        - U = hash(seed)
        - noise = Lap-CDF[U]
        - for n in range(len(original)):
            assert0(data[n] + noise - Pub_data[n])
    """

    key = 1987034928369859712  # TODO: Fix this

    # Commit the data
    poseidon_hash = PoseidonHash(p, alpha=17, input_rate=3)
    digest = poseidon_hash.hash(list(sdf))

    # Commit the key
    digest_key = poseidon_hash.hash([key])

    # PRF to generate a key
    def prf(key):
        num1 = key
        num2 = int(random.randint(0, p))
        result = num1 ^ num2
        return SecretInt(result)

    prkey = prf(key)

    # Add Laplace noise
    table = gen_laplace_table(sensitivity=1, p=p)
    zk_lap_table = ZKList(table)

    for i in range(len(sdf)):
        seed_h = poseidon_hash.hash([prkey])
        x = seed_h.to_binary()
        shifted_x = x >> 49  # TODO: Check if 48? it overflows as shifted_x = 8191

        # create a uniform draw in [0, 1023]
        U = shifted_x.to_arithmetic()

        # look up laplace sample in the table
        lap_draw = zk_lap_table[U]
        sdf_copy = sdf[i]
        sdf[i] += lap_draw
        assert0(sdf[i] - (sdf_copy + lap_draw))
