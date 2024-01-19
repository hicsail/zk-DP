from utils import *


sbox = [
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


mixcol_mtx = [[2, 3, 1, 1], [1, 2, 3, 1], [1, 1, 2, 3], [3, 1, 1, 2]]


Nk = 4  # Number of 32-bit words in CipherKey
Nr = 10  # Number of rounds
Nb = 4  # Block size in word

def binary_to_hex(binary_string):
    try:
        # Convert the binary string to an integer
        decimal_value = int(binary_string, 2)
        # Convert the integer to a hexadecimal string, remove the '0x' prefix
        hex_value = hex(decimal_value)[2:]
        return hex_value
    except ValueError:
        # Handle the case where the input is not a valid binary string
        return "Invalid binary input"


def hex_to_binary(hex_string):
    try:
        # Convert the hexadecimal string to an integer
        decimal_value = int(hex_string, 16)
        # Convert the integer to a binary string, remove the '0b' prefix
        binary_value = bin(decimal_value)[2:]
        return binary_value
    except ValueError:
        # Handle the case where the input is not a valid hexadecimal string
        return "Invalid hexadecimal input"


def SubBytes(state):
    for i in range(len(state)):
        bin_rep = bitlist_to_int(state[i])
        # Extract row and column number from the state's byte
        row = bin_rep // 0x10
        column = bin_rep % 0x10
        # Substitute the byte with the corresponding value from the sbox
        boxed_val = int(hex_to_binary(sbox[row][column]), 2)
        state[i] = int_to_bitlist(boxed_val, 8)
    return state


def ShiftRows(sboxed):
    if len(sboxed) != 16:
        raise ValueError("sboxed state must have exactly 16 elements")

    shifted = []
    for shift in range(4):
        shifted_row = [sboxed[(i + shift) % 4 + 4 * shift] for i in range(4)]
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
    This function returns b * 2 + b within GF(2^8) as {03} * b is sum of {02} and {01}
    """
    return gf_mult_by_02(b) ^ b


def mix_columns(shifted):
    mixed = []

    for idx in range(0, len(shifted), 4):
        shifted_row = shifted[idx : idx + 4]

        # Convert each 8 bit list into an integer to work with
        state_column = [int("".join(str(bit) for bit in byte), 2) for byte in shifted_row]

        # Prepare a list to hold the output of the MixColumns operation
        mixed_column = [0, 0, 0, 0]

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
                (
                    gf_mult_by_02(state_column[i])
                    if mixcol_mtx[i][0] == 2
                    else gf_mult_by_03(state_column[i])
                    if mixcol_mtx[i][0] == 3
                    else state_column[i]
                )
                ^ (
                    gf_mult_by_02(state_column[(i + 1) % 4])
                    if mixcol_mtx[i][1] == 2
                    else gf_mult_by_03(state_column[(i + 1) % 4])
                    if mixcol_mtx[i][1] == 3
                    else state_column[(i + 1) % 4]
                )
                ^ (
                    gf_mult_by_02(state_column[(i + 2) % 4])
                    if mixcol_mtx[i][2] == 2
                    else gf_mult_by_03(state_column[(i + 2) % 4])
                    if mixcol_mtx[i][2] == 3
                    else state_column[(i + 2) % 4]
                )
                ^ (
                    gf_mult_by_02(state_column[(i + 3) % 4])
                    if mixcol_mtx[i][3] == 2
                    else gf_mult_by_03(state_column[(i + 3) % 4])
                    if mixcol_mtx[i][3] == 3
                    else state_column[(i + 3) % 4]
                )
            )
        # Convert the mixed column back into lists of 8 bits
        mixed += [int_to_bitlist(byte, 8) for byte in mixed_column]

    return mixed


def rot_word(word):
    return word[1:] + word[:1]


def sub_word(word):
    for i, w in enumerate(word):
        # Extract row and column number from the state's byte
        row = int(w) // 0x10
        column = int(w) % 0x10
        # Substitute the byte with the corresponding value from the sbox
        word[i] = int(hex_to_binary(sbox[row][column]), 2)
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
    # Converting integer/plain text into bits list
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

        # TODO: Remove this; just a checker
        for row in range(4):
            original_row = sboxed[row * Nb : (row + 1) * Nb]
            shifted_row = shifted[row * Nb : (row + 1) * Nb]
            assert shifted_row == original_row[row:] + original_row[:row]

        # Apply the MixColumns function to the example input
        mixed = mix_columns(shifted)
        # print(f"\nmixed columns {mixed}", len(mixed))

        _round_keys = round_keys[i : i + 16]
        bin_mtx = AddRoundKey(_round_keys, mixed)
        # print("\n_Round keys:", _round_keys, len(_round_keys))

    # All operations except MixColumns in 11th iteration
    sboxed = SubBytes(bin_mtx)
    shifted = ShiftRows(sboxed)
    _round_keys = round_keys[i : i + 16]
    bin_mtx = AddRoundKey(_round_keys, shifted)

    cipher_text = [el for elem in bin_mtx for el in elem]
    assert len(bin_input) == len(cipher_text)
    return cipher_text, round_keys


def InvCipher(cipher_text, round_keys):
    # Converting integer/plain text into bits list
    bin_mtx = [cipher_text[i : i + 8] for i in range(0, len(cipher_text), 8)]
    print("bin_mtx", bin_mtx)

    # Directly apply AddRoundKey(_round_keys, mixed)
    _round_keys = round_keys[Nr * Nb:(Nr + 1)*Nb -1]
    bin_mtx = AddRoundKey(_round_keys, bin_mtx)

    # i = 10 to 1: All operations
    for i in range(Nr - 1, 1, -1):
        InvShifted = InvShiftRows(bin_mtx)
        InvSboxed = InvSubBytes(InvShifted)
        _round_keys = round_keys[i : i + 16] #TODO: FIX idx
        Signed = AddRoundKey(_round_keys, InvSboxed)
        bin_mtx = InvMixColumns(Signed)

    # All operations except MixColumns for the 0th block
    InvShifted = InvShiftRows(bin_mtx)
    InvSboxed = InvSubBytes(InvShifted)
    _round_keys = round_keys[i : i + 16] #TODO: FIX idx
    plain_text = AddRoundKey(_round_keys, InvSboxed)

    cipher_text = [el for elem in plain_text for el in elem]
    assert len(plain_text) == len(cipher_text)
    return plain_text


int_str = 1987034928369859712
_key = 1235282586324778
cipher_text, round_keys = AES(int_str, _key)
print("\ncipher_text", cipher_text)
InvPlainText = InvCipher(cipher_text, round_keys)
print("\nInvPlainText", InvPlainText)
# assert encrypted == [1, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 1, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 0, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 1, 1, 1, 0, 1, 1, 0, 1, 0, 0, 1, 0, 1, 0, 0]
