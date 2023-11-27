from .tables import *
from .utils import *


# ref: https://csrc.nist.gov/files/pubs/fips/46-3/final/docs/fips46-3.pdf
class DES:
    def __init__(self, key):
        key = [int(x) for x in bin(key)[2:]]
        in_keysize = 56
        if len(key) > in_keysize:
            key = key[:in_keysize]
        elif len(key) < in_keysize:
            key = [0 for _ in range(in_keysize - len(key))] + key
        assert len(key) == in_keysize

        self.key_schedule = self.key_expansion(key)

    def from_56_to_64(self, bit_key):
        assert len(bit_key) == 56
        curr_bit = 0
        res_key = []
        for i, b in enumerate(bit_key):
            curr_bit ^= b
            res_key.append(b)

            if (i + 1) % 7 == 0:
                curr_bit ^= 1
                res_key.append(curr_bit)
                curr_bit = 0
        assert len(res_key) == 64
        return res_key

    # Key expansion from 56 bits key to n_keys sets of 48 bits key
    def key_expansion(self, bit_key):
        # Expand 56 bits key to 64 bits key every 8th bits is of odd parity of preceding 7 bits
        bit_key = self.from_56_to_64(bit_key)

        key_schedule = []

        # Permuted choice 1
        c_key = [bit_key[x - 1] for x in pc_1_c]
        d_key = [bit_key[x - 1] for x in pc_1_d]

        for i in range(16):
            curr_shift = left_shift_schedule[i + 1]
            c_key = c_key[curr_shift:] + c_key[:curr_shift]
            d_key = d_key[curr_shift:] + d_key[:curr_shift]
            concat_key = c_key + d_key
            generated_key = [concat_key[x - 1] for x in pc_2_perm_table]
            assert len(generated_key) == 48
            key_schedule.append(generated_key)
        assert len(key_schedule) == 16
        return [ZKList(schedule) for schedule in key_schedule]

    def permutate(self, input_list, perm_table):
        return [input_list[x - 1] for x in perm_table]

    def s_boxify(self, split_xored_r):
        sboxed = []
        for i in range(len(split_xored_r)):
            s_input = split_xored_r[i]
            outer = 2 * s_input[0] + s_input[-1]
            middle = 8 * s_input[1] + 4 * s_input[2] + 2 * s_input[3] + s_input[4]

            sbox_idx = i * 64 + outer * 16 + middle
            s_val = ZKList(sbox)[sbox_idx]
            res = int_to_bitlist(s_val, 4)
            sboxed += res
        return sboxed

    def feistel_net(self, n_list, decrypt=False):
        for it in range(16):
            ## Half 64 bits into 2 sets of 32 bits (x and y)
            left = n_list[0:32]
            right = n_list[32:]
            assert len(left) == 32 and len(right) == 32

            ## E: Expand y from 32 to 48
            expanded_r = self.permutate(right, e_bit_select_table)
            assert len(expanded_r) == 48

            # Ensure the key schedule is reversed in decryption
            if decrypt == False:
                sub_key = self.key_schedule[it]
            else:
                sub_key = self.key_schedule[15 - it]

            ## XOR with 48 bits Key
            xored_r = xor(expanded_r, sub_key)
            assert len(xored_r) == 48

            ## Split the 48 bits into 8 sets (6 bits each)
            split_xored_r = [xored_r[i : i + 6] for i in range(0, 48, 6)]
            assert len(split_xored_r) == 8
            assert xored_r == [item for sublist in split_xored_r for item in sublist]

            ## S-Box: Look up table to shrink 6 bits to 4 bits
            sboxed = self.s_boxify(split_xored_r)
            assert len(sboxed) == 32

            # P: Permutate outputs (8 stes of 4 bits)
            permed_sboxed = self.permutate(sboxed, p_box_perm_table)
            assert len(permed_sboxed) == 32

            ## XOR modified right and left
            _left = xor(permed_sboxed, left)

            ## Swap left & right (if not in the last round) to re-form 64 bits
            if it != 15:
                n_list = right + _left
            else:
                n_list = _left + right

            assert len(n_list) == 64

        return n_list

    def encrypt(self, input_list):
        # Initial Permutation of input
        enc_list = self.permutate(input_list, init_perm_table)

        # Feistel Net ** Repeat 16 times of this round function
        enc_list = self.feistel_net(enc_list, decrypt=False)

        # Final Permutation (Reverse of Initial Permutation)
        enc_list = self.permutate(enc_list, final_perm_table)

        return bitlist_to_int(enc_list), enc_list

    def decrypt(self, enc_list):
        # Initial Permutation of input
        dec_list = self.permutate(enc_list, init_perm_table)

        # Reverse Feistel Net
        dec_list = self.feistel_net(dec_list, decrypt=True)

        # Final Permutation
        dec_list = self.permutate(dec_list, final_perm_table)

        return bitlist_to_int(dec_list), dec_list
