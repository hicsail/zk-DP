from utils import *


Sbox = [
    ["63", "7c", "77", "7b", "f2", "6b", "6f", "c5", "30", "01", "67", "2b", "fe", "d7", "ab", "76"],
    ["ca", "82", "c9", "7d", "fa", "59", "47", "f0", "ad", "d4", "a2", "af", "9c", "a4", "72", "c0"],
    ["b7", "fd", "93", "26", "36", "3f", "f7", "cc", "34", "a5", "e5", "f1", "71", "d8", "31", "15"],
    ["04", "c7", "23", "c3", "18", "96", "05", "9a", "07", "12", "80", "e2", "eb", "27", "b2", "75"],
    ["09", "83", "2c", "1a", "1b", "6e", "5a", "a0", "52", "3b", "d6", "b3", "29", "e3", "2f", "84"],
    ["53", "d1", "00", "ed", "20", "fc", "b1", "5b", "6a", "cb", "be", "39", "4a", "4c", "58", "cf"],
    ["d0", "ef", "aa", "fb", "43", "4d", "33", "85", "45", "f9", "02", "7f", "50", "3c", "9f", "a8"],
    ["51", "a3", "40", "8f", "92", "9d", "38", "f5", "bc", "b6", "da", "21", "10", "ff", "f3", "d2"],
    ["cd", "0c", "13", "ec", "5f", "97", "44", "17", "c4", "a7", "7e", "3d", "64", "5d", "19", "73"],
    ["60", "81", "4f", "dc", "22", "2a", "90", "88", "46", "ee", "b8", "14", "de", "5e", "0b", "db"],
    ["e0", "32", "3a", "0a", "49", "06", "24", "5c", "c2", "d3", "ac", "62", "91", "95", "e4", "79"],
    ["e7", "c8", "37", "6d", "8d", "d5", "4e", "a9", "6c", "56", "f4", "ea", "65", "7a", "ae", "08"],
    ["ba", "78", "25", "2e", "1c", "a6", "b4", "c6", "e8", "dd", "74", "1f", "4b", "bd", "8b", "8a"],
    ["70", "3e", "b5", "66", "48", "03", "f6", "0e", "61", "35", "57", "b9", "86", "c1", "1d", "9e"],
    ["e1", "f8", "98", "11", "69", "d9", "8e", "94", "9b", "1e", "87", "e9", "ce", "55", "28", "df"],
    ["8c", "a1", "89", "0d", "bf", "e6", "42", "68", "41", "99", "2d", "0f", "b0", "54", "bb", "16"],
]


InvSbox = [
    ["52", "09", "6a", "d5", "30", "36", "a5", "38", "bf", "40", "a3", "9e", "81", "f3", "d7", "fb"],
    ["7c", "e3", "39", "82", "9b", "2f", "ff", "87", "34", "8e", "43", "44", "c4", "de", "e9", "cb"],
    ["54", "7b", "94", "32", "a6", "c2", "23", "3d", "ee", "4c", "95", "0b", "42", "fa", "c3", "4e"],
    ["08", "2e", "a1", "66", "28", "d9", "24", "b2", "76", "5b", "a2", "49", "6d", "8b", "d1", "25"],
    ["72", "f8", "f6", "64", "86", "68", "98", "16", "d4", "a4", "5c", "cc", "5d", "65", "b6", "92"],
    ["6c", "70", "48", "50", "fd", "ed", "b9", "da", "5e", "15", "46", "57", "a7", "8d", "9d", "84"],
    ["90", "d8", "ab", "00", "8c", "bc", "d3", "0a", "f7", "e4", "58", "05", "b8", "b3", "45", "06"],
    ["d0", "2c", "1e", "8f", "ca", "3f", "0f", "02", "c1", "af", "bd", "03", "01", "13", "8a", "6b"],
    ["3a", "91", "11", "41", "4f", "67", "dc", "ea", "97", "f2", "cf", "ce", "f0", "b4", "e6", "73"],
    ["96", "ac", "74", "22", "e7", "ad", "35", "85", "e2", "f9", "37", "e8", "1c", "75", "df", "6e"],
    ["47", "f1", "1a", "71", "1d", "29", "c5", "89", "6f", "b7", "62", "0e", "aa", "18", "be", "1b"],
    ["fc", "56", "3e", "4b", "c6", "d2", "79", "20", "9a", "db", "c0", "fe", "78", "cd", "5a", "f4"],
    ["1f", "dd", "a8", "33", "88", "07", "c7", "31", "b1", "12", "10", "59", "27", "80", "ec", "5f"],
    ["60", "51", "7f", "a9", "19", "b5", "4a", "0d", "2d", "e5", "7a", "9f", "93", "c9", "9c", "ef"],
    ["a0", "e0", "3b", "4d", "ae", "2a", "f5", "b0", "c8", "eb", "bb", "3c", "83", "53", "99", "61"],
    ["17", "2b", "04", "7e", "ba", "77", "d6", "26", "e1", "69", "14", "63", "55", "21", "0c", "7d"],
]


Nk = 4  # Number of 32-bit words in CipherKey
Nr = 10  # Number of rounds
Nb = 4  # Block size in word


def SubBytes(state, Inv=False):
    sbox_to_use = InvSbox if Inv else Sbox
    for i in range(len(state)):
        bin_rep = bitlist_to_int(state[i])
        # Extract row and column number from the state's byte
        row = bin_rep // 0x10
        column = bin_rep % 0x10
        # Substitute the byte with the corresponding value from the sbox
        boxed_val = int(sbox_to_use[row][column], 16)
        state[i] = int_to_bitlist(boxed_val, 8)
    return state


def ShiftRows(state):
    if len(state) != 16:
        raise ValueError("State must have exactly 16 elements")

    shifted = []
    for shift in range(4):
        shifted_row = [state[(i + shift) % 4 + 4 * shift] for i in range(4)]
        shifted += shifted_row
    return shifted


def InvShiftRows(state):
    if len(state) != 16:
        raise ValueError("State must have exactly 16 elements")

    shifted = []
    for shift in range(4, 0, -1):
        shifted_row = [state[(i + shift) % 4 + 4 * (4 - shift)] for i in range(4)]
        shifted += shifted_row
    return shifted


def gf_mult_by_02(b):
    """
    This function returns b * 2 within GF(2^8)
    0x80 = 10000000 in binary
    0xFF = 11111111 in binary
    0x1B = 11011 in binary, which corresponds to the irreducible polynomial: x^8 + x^4 + x^3 + x + 1
    (Notice:We don't need 1000 prior to 11011 as this polynomial is defined in GF(2^8))
    """
    if b & 0x80:  # Checks if the MSB is 1
        l_shift = b << 1  # Shift by 1 (* 2)
        gf_28 = l_shift ^ 0x1B  # Reduce to GF2^8
        res = gf_28 & 0xFF  # Ensure the res is trimmed to 8 bits
        return res
    else:
        return b << 1  # Simply mult by 2 if MSB is 0 as no reduction is needed


def gf_mult_by_03(b):
    """
    This function returns b * 2 + b within GF(2^8) {03} * b is sum of {02} and {01}
    """
    return gf_mult_by_02(b) ^ b


def gf_mult_by_09(b):
    """
    This function returns b ^ 3 + b within GF(2^8)
    {09} in binary is 00001001 which is {08} (={02} ^ 3} XOR {01}
    """
    temp = gf_mult_by_02(gf_mult_by_02(gf_mult_by_02(b)))  # {08} * b
    return temp ^ b


def gf_mult_by_0B(b):
    """
    This function returns b ^ 3 + b ^ 1 + b within GF(2^8)
    {0b} in binary is 00001011 which is {08} (={02} ^ 3} XOR {02} XOR {01}
    """
    temp = gf_mult_by_02(gf_mult_by_02(gf_mult_by_02(b)))  # {08} * b
    temp2 = gf_mult_by_02(b)  # {02} * b
    return temp ^ temp2 ^ b


def gf_mult_by_0D(b):
    """
    This function returns b ^ 3 + b ^ 2 + b within GF(2^8)
    {0d} in binary is 00001101 which is {08} (={02} ^ 3) XOR {04} XOR {01}
    """
    temp = gf_mult_by_02(gf_mult_by_02(gf_mult_by_02(b)))  # {08} * b
    temp2 = gf_mult_by_02(gf_mult_by_02(b))  # {04} * b
    return temp ^ temp2 ^ b


def gf_mult_by_0E(b):
    """
    This function returns b ^ 3 + b ^ 2 + b ^ 1 within GF(2^8)
    {0e} in binary is 00001110 which is {08} (={02} ^ 3) XOR {04} XOR {02}
    """
    temp = gf_mult_by_02(gf_mult_by_02(gf_mult_by_02(b)))  # {08} * b
    temp2 = gf_mult_by_02(gf_mult_by_02(b))  # {04} * b
    temp3 = gf_mult_by_02(b)  # {02} * b
    return temp ^ temp2 ^ temp3


def gf_mult_by_constant(constant, byte):
    """
    Multiplies a byte by a constant in GF(2^8).
    """
    if constant == 0x01:
        return byte
    elif constant == 0x02:
        return gf_mult_by_02(byte)
    elif constant == 0x03:
        return gf_mult_by_03(byte)
    elif constant == 0x09:
        return gf_mult_by_09(byte)
    elif constant == 0x0B:
        return gf_mult_by_0B(byte)
    elif constant == 0x0D:
        return gf_mult_by_0D(byte)
    elif constant == 0x0E:
        return gf_mult_by_0E(byte)
    else:
        raise ValueError("Invalid constant for multiplication in GF(2^8)")


def MixColumns(state):
    mixed_state = []

    for idx in range(0, len(state), 4):
        row = state[idx : idx + 4]

        # Convert each 8 bit list into an integer to work with
        state_column = [int("".join(str(bit) for bit in byte), 2) for byte in row]

        # Placeholder for the output of the MixColumns transformation
        mixed_column = [0, 0, 0, 0]

        MixCol_mtx = [[0x02, 0x03, 0x01, 0x01], [0x01, 0x02, 0x03, 0x01], [0x01, 0x01, 0x02, 0x03], [0x03, 0x01, 0x01, 0x02]]

        # MixColumns matrix multiplication
        for i in range(4):
            """
            The following operation computes:
            s'0c = [02 03 01 01] * s0c
            s'1c = [01 02 03 01] * s1c
            s'2c = [01 01 02 03] * s2c
            s'3c = [03 01 01 02] * s3c
            (Note: Addition is XOR in the context of Galois Field arithmetic)
            """

            mixed_column[i] = (
                gf_mult_by_constant(MixCol_mtx[i][0], state_column[0])
                ^ gf_mult_by_constant(MixCol_mtx[i][1], state_column[1])
                ^ gf_mult_by_constant(MixCol_mtx[i][2], state_column[2])
                ^ gf_mult_by_constant(MixCol_mtx[i][3], state_column[3])
            )
        # Convert the mixed column back into lists of 8 bits
        mixed_state += [int_to_bitlist(byte, 8) for byte in mixed_column]

    return mixed_state


def InvMixColumns(state):
    mixed_state = []

    for idx in range(0, len(state), 4):
        row = state[idx : idx + 4]

        # Convert each 8 bit list into an integer to work with
        state_column = [int("".join(str(bit) for bit in byte), 2) for byte in row]

        # Placeholder for the output of the MixColumns transformation
        mixed_column = [0, 0, 0, 0]

        InvMixCol_mtx = [
            [0x0E, 0x0B, 0x0D, 0x09],
            [0x09, 0x0E, 0x0B, 0x0D],
            [0x0D, 0x09, 0x0E, 0x0B],
            [0x0B, 0x0D, 0x09, 0x0E],
        ]

        # MixColumns matrix multiplication
        for i in range(4):
            """
            The following operation computes:
            s'0c = [0e 0b 0d 09] * s0c
            s'1c = [09 0e 0b 0d] * s1c
            s'2c = [0d 09 0e 0b] * s2c
            s'3c = [0b 0d 09 0e] * s3c
            (Note: Addition is XOR in the context of Galois Field arithmetic)
            """

            mixed_column[i] = (
                gf_mult_by_constant(InvMixCol_mtx[i][0], state_column[0])
                ^ gf_mult_by_constant(InvMixCol_mtx[i][1], state_column[1])
                ^ gf_mult_by_constant(InvMixCol_mtx[i][2], state_column[2])
                ^ gf_mult_by_constant(InvMixCol_mtx[i][3], state_column[3])
            )
        # Convert the mixed column back into lists of 8 bits
        mixed_state += [int_to_bitlist(byte, 8) for byte in mixed_column]

    return mixed_state


def rot_word(word):
    return word[1:] + word[:1]


def sub_word(word):
    for i, w in enumerate(word):
        # Extract row and column number from the state's byte
        row = int(w) // 0x10
        column = int(w) % 0x10
        # Substitute the byte with the corresponding value from the sbox
        word[i] = int(Sbox[row][column], 16)
    return word


def key_expansion(key):
    # The key size for AES-128 is 128 bits = 16 bytes
    assert len(key) == 128

    # Convert the key from a bit list to a list of integers, each representing a byte
    key_bytes = [str(bitlist_to_int(key[i * 8 : (i + 1) * 8])) for i in range(16)]

    # AES-128 has 10 rounds, and we need 11 round keys (one for the initial round and one for each of the 10 rounds)
    # Each round key is 4 words (16 bytes), so we need a total of 44 words
    key_schedule = []
    rcon = [0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1B, 0x36]  # TODO: probably incorrect

    # The first round key is the key itself
    for i in range(Nk):
        key_schedule += key_bytes[i * Nk : (i + 1) * Nk]

    # Each subsequent round key is derived from the previous ones
    for i in range(Nk, Nb * (Nr + 1)):  # 4 words per round key * 11 round keys
        temp = key_schedule[-Nk:]
        if i % Nk == 0:
            rotated = rot_word(temp)
            temp = sub_word(rotated)
            temp[0] = temp[0] ^ rcon[i // Nk - 1]  # TODO FIXME index of temp and rcon

        temp = [temp[j] ^ int(key_schedule[-Nk * 4 + j]) for j in range(4)]
        key_schedule.extend(temp)

    key_schedule = [int_to_bitlist(int(elem), 8) for elem in key_schedule]
    # key_schedule = [key_schedule[i : i + 4] for i in range(0, len(key_schedule), 4)]
    return key_schedule


def AddRoundKey(keys, input_secret):
    cipher_text = []
    for idx, pt in enumerate(input_secret):
        cipher_text.append(xor(keys[idx], pt))
    return cipher_text


def AES(plain_text, _key):
    # Convert integer/plain text into bits list
    bin_input = int_to_bitlist(plain_text, 128)
    bin_mtx = [bin_input[i : i + 8] for i in range(0, len(bin_input), 8)]
    rev_bin_input = [item for row in bin_mtx for item in row]
    assert bin_input == rev_bin_input
    print("\ninput    ", bin_input)

    # Key Expansion: Generating 11 sets of 16 bytes keys(4 bytes x 4)
    key = int_to_bitlist(_key, 128)
    round_keys = key_expansion(key)

    # i = 0: Directly apply AddRoundKey(_round_keys, mixed)
    _round_keys = round_keys[0:16]
    bin_mtx = AddRoundKey(_round_keys, bin_mtx)

    # i = 1 to 10: All operations
    for i in range(1, Nr):
        sboxed = SubBytes(bin_mtx)
        shifted = ShiftRows(sboxed)
        mixed = MixColumns(shifted)
        _round_keys = round_keys[i * 16 : i * 16 + 16]
        bin_mtx = AddRoundKey(_round_keys, mixed)

    # i = 11: All operations except MixColumns
    sboxed = SubBytes(bin_mtx)
    shifted = ShiftRows(sboxed)
    _round_keys = round_keys[160:176]
    bin_mtx = AddRoundKey(_round_keys, shifted)

    cipher_text = [el for elem in bin_mtx for el in elem]
    assert len(bin_input) == len(cipher_text)
    return cipher_text, round_keys


def InvCipher(cipher_text, round_keys):
    
    bin_mtx = [cipher_text[i : i + 8] for i in range(0, len(cipher_text), 8)]

    # Directly apply AddRoundKey(_round_keys, mixed) for the first round
    _round_keys = round_keys[160:176]
    bin_mtx = AddRoundKey(_round_keys, bin_mtx)

    # i = 10 to 1: All operations
    for i in range(Nr - 1, 0, -1):
        InvShifted = InvShiftRows(bin_mtx)
        InvSboxed = SubBytes(InvShifted, Inv=True)
        _round_keys = round_keys[i * 16 : i * 16 + 16]
        Signed = AddRoundKey(_round_keys, InvSboxed)
        bin_mtx = InvMixColumns(Signed)

    # All operations except MixColumns for the last block
    InvShifted = InvShiftRows(bin_mtx)
    InvSboxed = SubBytes(InvShifted, Inv=True)
    _round_keys = round_keys[0:16]
    plain_text = AddRoundKey(_round_keys, InvSboxed)

    plain_text = [el for elem in plain_text for el in elem]
    assert len(plain_text) == len(cipher_text)
    return plain_text


# e2s Test for enc and dec
int_str = 1987034928369859712
_key = 1235282586324778

cipher_text, round_keys = AES(int_str, _key)
print("\ncipher_text", cipher_text)

InvPlainText = InvCipher(cipher_text, round_keys)
print("\nInvPlainText", InvPlainText)

assert InvPlainText == int_to_bitlist(int_str, 128)


# Unit Test for shiftrows and and inverse
temp_state = [i for i in range(0, 16)]
print("\nbefore", temp_state)
res = ShiftRows(temp_state)
print("\nafter", res)
assert res == [0, 1, 2, 3, 5, 6, 7, 4, 10, 11, 8, 9, 15, 12, 13, 14]

print("\nbefore", res)
InvRes = InvShiftRows(res)
print("\nafter", InvRes)
assert temp_state == InvRes


# Unit Test for mixcol and inverse
test_mx = [[0, 1, 0, 0, 1, 1, 0, 0], [0, 0, 1, 0, 1, 0, 1, 0], [0, 1, 1, 0, 0, 0, 0, 1], [0, 1, 0, 0, 1, 1, 0, 0], [0, 1, 1, 1, 1, 1, 1, 0], [1, 0, 1, 0, 0, 0, 1, 1], [1, 0, 1, 1, 1, 1, 1, 1], [1, 1, 0, 1, 1, 0, 0, 1], [1, 0, 0, 0, 1, 0, 1, 0], [0, 1, 1, 1, 1, 1, 1, 1], [0, 1, 1, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 1, 1, 1], [0, 0, 1, 0, 1, 0, 0, 0], [1, 0, 0, 1, 0, 1, 1, 0], [1, 1, 1, 1, 1, 1, 1, 0], [1, 1, 0, 0, 0, 1, 0, 0]]
res = InvMixColumns(MixColumns(test_mx))
assert test_mx == res