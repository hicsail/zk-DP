from picozk import *
from picozk.poseidon_hash import PoseidonHash
from nistbeacon import NistBeacon
from datetime import datetime


def add_noise(df, col, p, hashed_df, zk_lap_table, prf_func):
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
    # Confirm the authenticity of the data
    poseidon_hash = PoseidonHash(p, alpha=17, input_rate=3)
    digest = poseidon_hash.hash(list(sdf))
    assert0(digest - hashed_df)

    def get_beacon():
        beaconVal = NistBeacon.get_last_record()
        beacon_hex = beaconVal.output_value
        beacon = int(beacon_hex, 16) % p  # Convert hexadecimal string to integer
        now = datetime.now()
        print(" ", now, ":", beacon)
        beacon = [int(x) for x in bin(beacon)[2:]]  # To binary list
        if len(beacon) < 64:
            beacon = [0 for _ in range(64 - len(beacon))] + beacon
        else:
            beacon = beacon[:64]
        assert len(beacon) == 64
        return beacon

    def shrink_bits(bit_list, size):
        bin_list = bit_list[:size]

        reduced_bits = 0
        for i in range(size - 1, -1, -1):
            reduced_bits += 2 ** (i) * bin_list[i]

        return reduced_bits

    def prf(beacon):
        _, enc_lis = prf_func.encrypt(beacon)
        return shrink_bits(enc_lis, 13)

    for i in range(len(sdf)):
        print(i, end="\r")
        # look up laplace sample in the table
        U = prf(get_beacon())

        # Draw from lap distribution
        lap_draw = zk_lap_table[U]

        # Add noise to data
        sdf_copy = df.loc[i, col]
        df.loc[i, col] = df.loc[i, col] + lap_draw
        check = df.loc[i, col] - sdf_copy - lap_draw
        assert0(check)
        assert val_of(check) == 0
