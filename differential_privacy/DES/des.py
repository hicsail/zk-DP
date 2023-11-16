from permKey import key_perm
from tables import s_box, init_perm_table, final_perm_table
from utils import *

class DES():

    def __init__(self, input_list, bit_list_key):
      self.input_list = input_list
      self.enc_list = []
      key_size = 48
      n_keys = 16
      self.key_set = self.key_expansion(key_size, bit_list_key, n_keys, key_perm)
      assert len(self.key_set) == n_keys


    # Key expansion from 56 bits key to n_keys sets of 48 bits key
    #TODO PC-1 and PC-2 permutations to generate 16 48-bit keys from the original 56-bit key.
    def key_expansion(self, key_size, bit_list_key, n_keys, key_perm):
        def generate_key(i):
            sub_key_idx = key_perm[i]
            sub_key = ''
            for idx in sub_key_idx:
              sub_key += str(bit_list_key[idx])

            assert len(sub_key) == key_size
            return sub_key

        res = []
        for i in range(n_keys):
          res.append(generate_key(i))
        assert len(res) == n_keys
        return res

    
    def init_perm(self, n_list):
        n_list = [n_list[x-1] for x in init_perm_table]
        return n_list


    def last_perm(self, n_list):
        n_list = [n_list[x-1] for x in final_perm_table]
        return n_list


    def lookup_s_box(self, outer_bits, middle_bits, s_box):
        row = int(outer_bits, 2)
        column = int(middle_bits, 2)
        return s_box[row][column]


    def get_outer_middle_bits(self, s_input):
        outer_bits = str(s_input[0]) + str(s_input[-1])
        middle_bits = str(s_input[1]) + str(s_input[2]) + str(s_input[3]) + str(s_input[4])
        return outer_bits, middle_bits


    #TODO Research and follow a specific permutation method
    def s_boxify(self, split_signed_x):
      out_sbox = []
      for i in range(len(split_signed_x)):
        s_input = split_signed_x[i]
        outer, middle = self.get_outer_middle_bits(s_input)
        res = self.lookup_s_box(outer, middle, s_box)
        out_sbox+=res
      assert len(out_sbox) == 32
      return out_sbox

    #TODO Research and follow a specific pattern
    def expand_bits(self, x):
      _x = x[:16]
      expanded_x = x + _x
      return expanded_x


    def feistel_net(self, n_list, decrypt=False):
      
      for it in range(16):
        ## Half 64 bits into 2 sets of 32 bits (x and y)
        left = n_list[0:32]
        right = n_list[32:]
        assert len(left) == 32 and len(right) == 32

        ## Expand y from 32 to 48
        expanded_r = self.expand_bits(right)
        assert(len(expanded_r) == 48)

        ## Sign with 48 bits Key of the step 1
        if decrypt == False:
            sub_key=self.key_set[it]
        else:
            sub_key=self.key_set[15-it]
        signed_r = sign(expanded_r, sub_key)
        assert len(signed_r) == 48

        ## Split the 48 bits into 8 sets (6 bits each)
        split_signed_r = [signed_r[i : i + 6] for i in range(0, 48, 6)]
        temp = [item for sublist in split_signed_r for item in sublist]
        assert temp == signed_r

        ## S-Box: Look up table to shrink 6 bits to 4 bits
        out_sbox = self.s_boxify(split_signed_r)

        ## sign x and _y
        _left = sign(out_sbox, right)

        ## Swap side between output x and y from step 3-1 and consolidate them to make 64 bits

        n_list = right + _left
        assert len(n_list) == 64
      
      return n_list 

    
    def encrypt(self):
      # Initial Permutation of input
      self.enc_list = self.init_perm(self.input_list)

      # Feistel Net ** Repeat 16 times of this round function
      self.enc_list = self.feistel_net(self.enc_list, decrypt=False)
      
      # Final Permutation (Reverse of Initial Permutation)
      self.enc_list = self.last_perm(self.enc_list)
      
      return list_to_binary(self.enc_list), self.enc_list


    def decrypt(self):
      # Initial Permutation of input
      dec_list = self.init_perm(self.enc_list)
      
      # Reverse Feistel Net
      dec_list = self.feistel_net(dec_list, decrypt=True)
      
      # Final Permutation
      dec_list = self.last_perm(dec_list)
      
      return list_to_binary(dec_list), dec_list
