import random
from picozk import *


def bitlist_to_int(_list):
    res = 0
    for p in range(len(_list)):
        res += _list[p] * (2 ** (len(_list) - 1 - p))
    return res


def int_to_bitlist(num, size=None):
    if size is None:
        return [int(x) for x in bin(num)[2:]]
    else:
        res = []
        for p in range(size - 1, -1, -1):
            scale = 2**p
            elem = mux(scale <= num, 1, 0)
            res.append(elem)
            num = mux(scale <= num, num - scale, num)
        return res


def xor(one, two):
    if len(one) > len(two):
        two = [0 for _ in range(len(one) - len(two))] + two
    elif len(one) < len(two):
        one = [0 for _ in range(len(two) - len(one))] + one
    assert len(one) == len(two)

    xor_ed = [0 for _ in range(len(one))]
    for i, (x, k) in enumerate(zip(one, two)):
        xor_ed[i] = mux(x - k == 0, 0, 1)
    return xor_ed


# Generate 'size' bits
def generate_bit(size):
    bit = random.randint(0, 2**size)
    bit_list = int_to_bitlist(bit, size)
    return bit, bit_list
