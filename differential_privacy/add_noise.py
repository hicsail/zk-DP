from picozk import *
from picozk.poseidon_hash import PoseidonHash
from nistbeacon import NistBeacon
from datetime import datetime

def add_noise(df, col, p, hashed_df, key, zk_lap_table):
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
        num2_hex = beaconVal.output_value
        num2 = int(num2_hex, 16) % p  # Convert hexadecimal string to integer
        now = datetime.now()
        print(" ", now, ":", num2)
        return num2

    def xor(key, beacon):
        if len(key) > len(beacon):
            beacon = [0 for _ in range(len(key) - len(beacon))] + beacon
        elif len(key) < len(beacon):
            padd = [0 for _ in range(len(beacon) - len(key))]
            for o in key:
                padd.append(o)
            key = padd
        assert len(key) == len(beacon)

        xor_ed = [0 for _ in range(len(key))]
        for i, (x, k) in enumerate(zip(key, beacon)):
            xor_ed[i] = mux(x - k == 0, 0, 1)
        return xor_ed
    
    # Generate a seed
    def generate_seed(key):
        beacon = get_beacon()
        beacon = [int(x) for x in bin(beacon)[2:]] # To binary list
        return xor(key, beacon)

    
    def shrink_bits(s_int, size):
        max_int = (2**(size+1)) - 1
        remove = s_int - max_int
        s_int -= remove

        bin_list =[]
        for i in range(size - 1, -1, -1): #TODO: Fix this as we know size of int
            bin_list.append(mux(s_int > 2**i, 1, 0))
            s_int -= 2**i
        
        reduced_bits = 0
        for i in range(size - 1, -1, -1):
            reduced_bits+=2**(i)*bin_list[i]

        return reduced_bits

    def prf(seed, i):
        seed_h = poseidon_hash.hash(list(seed + [i]))
        return shrink_bits(seed_h, 13)

    seed = generate_seed(key)

    for i in range(len(sdf)):
        print(i, end='\r')
        # look up laplace sample in the table
        U = prf(seed, i)
                
        # Draw from lap distribution
        lap_draw = zk_lap_table[U]

        # Add noise to data
        sdf_copy = df.loc[i, col]
        df.loc[i, col] = df.loc[i, col] + lap_draw
        check = df.loc[i, col] - sdf_copy - lap_draw
        assert0(check)
        assert val_of(check) == 0
