from utils import *
from tables import Sbox, InvSbox, Enc_mtx, Inv_mtx
from picozk import *

Nk = 4  # Number of 32-bit words in CipherKey
Nr = 10  # Number of rounds
Nb = 4  # Block size in word
p = pow(2, 257) - 1


def SubBytes(state, Inv=False):
    sbox_to_use = InvSbox if Inv else Sbox
    for i in range(len(state)):
        bin_rep = bitlist_to_int(state[i])
        # Substitute the byte with the corresponding value from the sbox
        boxed_val = ZKList(sbox_to_use)[bin_rep]
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
    Checks if the MSB is 1
    If yes: Shift by 1 (* 2), Reduce to GF2^8, and Ensure the res is trimmed to 8 bits
    Else: Simply mult by 2 if MSB is 0 as no reduction is needed

    """
    print(val_of((b & 0x80).to_arithmetic()))
    return mux((b & 0x80) == 1, ((b << 1) ^ 0x1B) & 0xFF, b << 1)


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
    byte = byte.to_binary()
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


def MixColumns(state, Inv = False):
    mixed_state = []

    for idx in range(0, len(state), 4):
        row = state[idx : idx + 4]

        # Convert each 8 bit list into an integer to work with
        state_column = [bitlist_to_int(byte) for byte in row]

        # Placeholder for the output of the MixColumns transformation
        mixed_column = [0, 0, 0, 0]

        MixCol_mtx = Inv_mtx if Inv else Enc_mtx

        # MixColumns matrix multiplication
        for i in range(4):
            """
            The encryption computes:
                s'0c = [02 03 01 01] * s0c
                s'1c = [01 02 03 01] * s1c
                s'2c = [01 01 02 03] * s2c
                s'3c = [03 01 01 02] * s3c

            Decryption computes:
            The following operation computes:
                s'0c = [0e 0b 0d 09] * s0c
                s'1c = [09 0e 0b 0d] * s1c
                s'2c = [0d 09 0e 0b] * s2c
                s'3c = [0b 0d 09 0e] * s3c

            (Note: Addition is XOR in the context of Galois Field arithmetic)
            """

            mixed_column[i] = (
                gf_mult_by_constant(MixCol_mtx[i][0], state_column[0])
                ^ gf_mult_by_constant(MixCol_mtx[i][1], state_column[1])
                ^ gf_mult_by_constant(MixCol_mtx[i][2], state_column[2])
                ^ gf_mult_by_constant(MixCol_mtx[i][3], state_column[3])
            ).to_arithmetic()
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
        idx = row * 16 + column
        # Substitute the byte with the corresponding value from the sbox
        word[i] = Sbox[idx]
    return word


def key_expansion(key):
    # The key size for AES-128 is 128 bits = 16 bytes
    assert len(key) == 128

    # Convert the key from a bit list to a list of integers, each representing a byte
    key_bytes = [str(bitlist_to_int(key[i * 8 : (i + 1) * 8])) for i in range(16)]

    # AES-128 has 10 rounds, and we need 11 round keys (one for the initial round and one for each of the 10 rounds)
    # Each round key is 4 words (16 bytes), so we need a total of 44 words
    key_schedule = []
    rcon = [0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1B, 0x36]

    # The first round key is the key itself
    for i in range(Nk):
        key_schedule += key_bytes[i * Nk : (i + 1) * Nk]

    # Each subsequent round key is derived from the previous ones
    for i in range(Nk, Nb * (Nr + 1)):  # 4 words per round key * 11 round keys
        temp = key_schedule[-Nk:]
        if i % Nk == 0:
            rotated = rot_word(temp)
            temp = sub_word(rotated)
            temp[0] = temp[0] ^ rcon[i // Nk - 1]

        temp = [temp[j] ^ int(key_schedule[-Nk * 4 + j]) for j in range(4)]
        key_schedule.extend(temp)

    key_schedule = [int_to_bitlist(int(elem), 8) for elem in key_schedule]
    return [ZKList(schedule) for schedule in key_schedule]


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
        if i == 1: #TODO: Check on this
            obj = [[0, 1, 1, 0, 0, 0, 1, 1], [0, 1, 1, 0, 0, 0, 1, 1], [0, 1, 1, 0, 0, 0, 1, 1], [0, 1, 1, 0, 0, 0, 1, 1], [0, 1, 1, 0, 0, 0, 1, 1], [0, 1, 1, 0, 0, 0, 1, 1], [0, 1, 1, 0, 0, 0, 1, 1], [0, 1, 1, 0, 0, 0, 1, 1], [1, 0, 0, 1, 1, 1, 1, 1], [1, 0, 1, 0, 0, 0, 1, 1], [1, 1, 0, 0, 0, 0, 0, 0], [1, 1, 0, 1, 1, 1, 0, 1], [0, 0, 1, 0, 1, 0, 0, 1], [0, 1, 0, 1, 1, 0, 1, 0], [0, 1, 1, 0, 1, 1, 1, 0], [0, 1, 0, 1, 1, 1, 1, 1]]
            for i, mix in enumerate(mixed):
                for j, s in enumerate(mix):
                    print(i, "-", j, val_of(s), obj[i][j])
                    assert val_of(s) == obj[i][j]
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
        bin_mtx = MixColumns(Signed, Inv=True)

    # All operations except MixColumns for the last block
    InvShifted = InvShiftRows(bin_mtx)
    InvSboxed = SubBytes(InvShifted, Inv=True)
    _round_keys = round_keys[0:16]
    plain_text = AddRoundKey(_round_keys, InvSboxed)

    plain_text = [el for elem in plain_text for el in elem]
    assert len(plain_text) == len(cipher_text)
    return plain_text


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
# test_mx = [[0, 1, 0, 0, 1, 1, 0, 0], [0, 0, 1, 0, 1, 0, 1, 0], [0, 1, 1, 0, 0, 0, 0, 1], [0, 1, 0, 0, 1, 1, 0, 0], [0, 1, 1, 1, 1, 1, 1, 0], [1, 0, 1, 0, 0, 0, 1, 1], [1, 0, 1, 1, 1, 1, 1, 1], [1, 1, 0, 1, 1, 0, 0, 1], [1, 0, 0, 0, 1, 0, 1, 0], [0, 1, 1, 1, 1, 1, 1, 1], [0, 1, 1, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 1, 1, 1], [0, 0, 1, 0, 1, 0, 0, 0], [1, 0, 0, 1, 0, 1, 1, 0], [1, 1, 1, 1, 1, 1, 1, 0], [1, 1, 0, 0, 0, 1, 0, 0]]
# res = InvMixColumns(MixColumns(test_mx), Inv=True)
# assert test_mx == res

with PicoZKCompiler("irs/picozk_test", field=[p], options=["ram"]):
    # e2s Test for enc and dec
    int_str = 1987034928369859712
    _key = 1235282586324778

    cipher_text, round_keys = AES(int_str, _key)
    _cipher_text = [val_of(ct) for ct in cipher_text]
    print("\ncipher_text", _cipher_text)

    InvPlainText = InvCipher(cipher_text, round_keys)
    _InvPlainText = [val_of(pt) for pt in InvPlainText]
    print("\nInvPlainText", _InvPlainText)

    assert _InvPlainText == int_to_bitlist(int_str, 128)
