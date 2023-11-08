import numpy as np

SCALE_FACTOR = 1000


# Generate a lookup table for Laplace noise samples
def gen_laplace_table(sensitivity, p):
    # Convert a number into bits
    def bitfield(n):
        return [int(x) for x in "{0:013b}".format(n)]

    # Convert bits into a decimal in [0,1]
    def bval(bits):
        tot = 0
        for i, b in zip(range(1, 14), bits):
            tot = tot + b / (2**i)
        return tot

    # Compute an entry in the lookup table
    def lap_draw(unif):
        U = unif - 0.5
        return sensitivity * np.sign(U) * np.log(1 - 2 * np.abs(U))

    table = []
    for n in range(1, 8191):  # 8191 == 12 bits of 1s
        v = bval(bitfield(n))
        lap = lap_draw(v)

        # Encode as fixed-point number
        scaled = lap * SCALE_FACTOR
        encoded = scaled % p
        encoded = encoded % p
        table.append(encoded)

    return table
