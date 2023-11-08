from picozk import *
from picozk.poseidon_hash import PoseidonHash
import pandas as pd
from utils.laplase import gen_laplace_table

# bitwidth is 13

if __name__ == "__main__":
    scale = 10

    p = pow(2, 61) - 1

    with PicoZKCompiler("irs/picozk_test", field=[p], options=["ram"]):
        """
        Time1: A prover commits a real data and generate a private key
        Time2: A beacon generates a random integer-string, x
        Time3: Seed = PRF(k, x)

        Proof:
            - Pub_data (Modified Sensus Data)
            - U = hash(seed)
            - noise = Lap-CDF[U]
            - for n in range(len(original)):
                assert0(data[n] + noise - Pub_data[n])
        """

        # https://media.githubusercontent.com/media/usnistgov/SDNist/main/nist%20diverse%20communities%20data%20excerpts/massachusetts/ma2019.csv
        df = pd.read_csv("ma2019.csv")

        mapping = {
            "25-00703": 0,
            "25-00503": 1,
            "25-01300": 2,
            "25-02800": 3,
            "25-01000": 4,
        }

        sdf = df["PUMA"].replace(mapping).apply(SecretInt)

        # Hash the data
        poseidon_hash = PoseidonHash(p, alpha=17, input_rate=3)
        digest = poseidon_hash.hash(list(sdf))
        reveal(digest)

        # Query the data
        histogram = ZKList([0, 0, 0, 0, 0])

        def update_hist(x):
            histogram[x] = histogram[x] + 1000

        sdf.apply(update_hist)
        print(histogram)

        # Add Laplace noise
        seed = SecretInt(1987034928369859712)

        zk_lap_table = ZKList(gen_laplace_table(sensitivity=1, p=p))
        rng_hash = PoseidonHash(p, alpha=17, input_rate=3, t=3)

        for i in range(5):
            digest = poseidon_hash.hash([seed])
            x = digest.to_binary()
            print("bit len", len(x.wires))
            shifted_x = x >> 48

            # create a uniform draw in [0, 1023]
            U = shifted_x.to_arithmetic()

            # look up laplace sample in the table
            lap_draw = zk_lap_table[U]
            histogram[i] = histogram[i] + lap_draw

        print(histogram)
        # Reveal the noisy histogram
        for i in range(5):
            reveal(histogram[i])
