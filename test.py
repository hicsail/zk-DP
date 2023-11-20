def shrink_bits(s_int, size):
    
    check = s_int & ((1 << (size+1)) - 1)

    max_int = (2 ** (size + 1)) - 1
    remove = s_int - max_int
    s_int = s_int - remove
    
    print(s_int, check)

    bin_list = []
    for i in range(size - 1, -1, -1):  # TODO: Fix this as we know size of int
        if s_int > 2**i:
            bin_list.append(1)
            s_int -= 2**i
        else:
            bin_list.append(0)
    print('intermediate', bin_list)

    reduced_bits = 0
    for i in range(size - 1, -1, -1):
        reduced_bits += 2 ** (i) * bin_list[i]

    return reduced_bits


def list_to_binary(_list):
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
            if scale < num:
                res.append(1)
            else:
                res.append(0)
            num -= scale
        return res

s_int = 13
size = 3

listified = int_to_bitlist(s_int)
print('original', listified)

shrinked_bits = shrink_bits(s_int, size)
listified_shr = int_to_bitlist(shrinked_bits)
print('\n new method', shrinked_bits, listified_shr)


classical_method = listified[:size]
listified_clss = list_to_binary(classical_method)
print('\n classical', listified_clss, classical_method)
assert int_to_bitlist(shrinked_bits) == classical_method