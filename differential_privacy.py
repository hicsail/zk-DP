import pandas as pd
from picozk import *
from picozk.poseidon_hash import PoseidonHash
from differential_privacy.add_noise import add_noise
from differential_privacy.preprocess import preprocess
from differential_privacy.prf import TripleDES_prf, Poseidon_prf

if __name__ == "__main__":
    p = pow(2, 127) - 1
    # https://media.githubusercontent.com/media/usnistgov/SDNist/main/nist%20diverse%20communities%20data%20excerpts/massachusetts/ma2019.csv
    df = pd.read_csv("ma2019.csv")

    keys = [1987034928369859712, 1987034925329849712, 15528198805165525]  # TODO: Make a proper key

    with PicoZKCompiler("irs/picozk_test", field=[p], options=["ram"]):
        # Uncomment either
        prf_func = TripleDES_prf(keys, p)
        # prf_func = Poseidon_prf(keys, p)

        # Replace negative values and N with ave.(excl. neg values)
        preprocess(df)

        col = "PUMA"
        sdf = df[col]
        poseidon_hash = PoseidonHash(p, alpha=17, input_rate=3)
        hashed_df = poseidon_hash.hash(list(sdf))
        _key = poseidon_hash.hash(keys)

        # Implementation Body
        add_noise(sdf, p, hashed_df, prf_func)
