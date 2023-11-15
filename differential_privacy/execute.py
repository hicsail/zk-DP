from picozk import *
from picozk.poseidon_hash import PoseidonHash
from .add_noise import add_noise
from .laplase import gen_laplace_table


def execute(df, key, p, cols=None):

    # Secrefy Key
    key = SecretInt(key)

    # Create laplase table
    table = gen_laplace_table(sensitivity=1, p=p)
    zk_lap_table = ZKList(table)
    poseidon_hash = PoseidonHash(p, alpha=17, input_rate=3)
    _key = poseidon_hash.hash([key])

    if cols is None:
        cols = df.columns

    for col in cols:
        print("\nWorking on", col)

        # Commit data and key
        poseidon_hash = PoseidonHash(p, alpha=17, input_rate=3)
        hashed_df = poseidon_hash.hash(list(df[col]))

        # Add noise to df
        add_noise(df, col, p, hashed_df, key, zk_lap_table)
