from picozk import *
from picozk.poseidon_hash import PoseidonHash
from .laplase import gen_laplace_table
from nistbeacon import NistBeacon
from datetime import datetime


def add_noise(df, col, p, hashed_df, key):
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

    sdf = df[col]
    # Commit data and key
    poseidon_hash = PoseidonHash(p, alpha=17, input_rate=3)
    digest = poseidon_hash.hash(list(sdf))
    assert0(digest - hashed_df)

    def get_beacon():
        beaconVal = NistBeacon.get_last_record()
        num2_hex = beaconVal.output_value
        num2 = int(num2_hex, 16) % p  # Convert hexadecimal string to integer
        now = datetime.now()
        print(" ", now, ":", num2)
        return num2

    # Generate a seed
    def generate_seed(key):
        num1 = key
        num2 = get_beacon()
        result = num1 ^ num2
        return SecretInt(result)

    # Add Laplace noise
    table = gen_laplace_table(sensitivity=1, p=p)
    zk_lap_table = ZKList(table)

    def prf(seed):
        seed_h = poseidon_hash.hash([seed, i])
        x = seed_h.to_binary()
        shifted_x = x >> 114

        # create a uniform draw in [0, 1023]
        U = shifted_x.to_arithmetic()
        return zk_lap_table[U]

    seed = generate_seed(key)

    for i in range(len(sdf)):
        # look up laplace sample in the table
        lap_draw = prf(seed)
        sdf_copy = df.loc[i, col]
        df.loc[i, col] = df.loc[i, col] + lap_draw
        check = df.loc[i, col] - sdf_copy - lap_draw
        assert0(check)
        assert val_of(check) == 0
