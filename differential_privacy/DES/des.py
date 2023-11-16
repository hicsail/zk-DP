from permKey import key_perm
from sbox import s_box, reverse_s_box
from utils import *

class DES():

    def __init__(self, n_list, bit_list_key):
      self.n_list = n_list
      key_size = 48
      n_keys = 16
      self.key_set = self.key_expansion(key_size, bit_list_key, n_keys, key_perm)
      assert len(self.key_set) == n_keys


    # Key expansion from 56 bits key to n_keys sets of 48 bits key
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
      size = len(n_list)
      mid = size//2
      f_half = n_list[mid:]
      l_half = n_list[:mid]
      l_half.reverse()
      n_list = [item for pair in zip(f_half, l_half) for item in pair]
      return n_list


    def last_perm(self, n_list):
      f_half = [odd_elem for idx, odd_elem in enumerate(n_list) if idx % 2 == 1]
      f_half.reverse()
      l_half = [even_elem for idx, even_elem in enumerate(n_list) if idx % 2 == 0]
      n_list = f_half + l_half
      assert len(n_list) == 64
      return n_list


    def lookup_s_box(self, outer_bits, middle_bits, s_box):
        row = int(outer_bits, 2)
        column = int(middle_bits, 2)
        return s_box[row][column]


    def get_outer_middle_bits(self, s_input):
        outer_bits = str(s_input[0]) + str(s_input[-1])
        middle_bits = str(s_input[1]) + str(s_input[2]) + str(s_input[3]) + str(s_input[4])
        return outer_bits, middle_bits


    def s_boxify(self, split_signed_x):
      out_sbox = []
      for i in range(len(split_signed_x)):
        s_input = split_signed_x[i]
        outer, middle = self.get_outer_middle_bits(s_input)
        res = self.lookup_s_box(outer, middle, s_box)
        out_sbox+=res
      assert len(out_sbox) == 32
      return out_sbox


    def un_s_boxify(self, split_x):
      rev_out_sbox = []
      for i in range(len(split_x)):
        s_input = ''.join(str(bit) for bit in split_x[i])
        val = reverse_s_box[s_input]
        res = val[0][0]+val[1]+val[0][1]
        rev_out_sbox+=res
      assert len(rev_out_sbox) == 48
      return rev_out_sbox


    def expand_x(self, x):
      _x = x[:16]
      expanded_x = x + _x
      return expanded_x


    def shrink_x(self, x):
      _x = x[:32]
      return _x


    def feistel_net(self, n_list):
      
      for it in range(16):
        ## Half 64 bits into 2 sets of 32 bits (x and y)
        x = n_list[0:32]
        y = n_list[32:]
        assert len(x) == 32 and len(y) == 32

        ## Expand x from 32 to 48
        expanded_x = self.expand_x(x)
        assert(len(expanded_x) == 48)

        ## Sign with 48 bits Key of the step 1
        sub_key=self.key_set[it]
        signed_x = sign(expanded_x, sub_key)
        assert len(signed_x) == 48
        ## Split the 48 bits into 8 sets (6 bits each)
        split_signed_x = [signed_x[i : i + 6] for i in range(0, 48, 6)]
        temp = [item for sublist in split_signed_x for item in sublist]
        assert temp == signed_x

        ## S-Box: Look up table to shrink 6 bits to 4 bits
        out_sbox = self.s_boxify(split_signed_x)

        ## sign x and y
        _x = sign(out_sbox, y)

        ## Swap side between output x and y from step 3-1 and consolidate them to make 64 bits

        n_list = y + _x
        assert len(n_list) == 64
      
      return n_list 


    def rev_feistel_net(self, n_list, key_set):
      
      for it in range(16):
        ## Half 64 bits into 2 sets of 32 bits (x and y)
        y = n_list[0:32]
        _x = n_list[32:]
        assert len(_x) == 32 and len(y) == 32

        ## Split the 32 bits into 8 sets (4 bits each)
        split_x = [_x[i : i + 4] for i in range(0, 32, 4)]

        ## S-Box: Look up dict to recover 6 bits from 4 bits
        un_sboxed = self.un_s_boxify(split_x)

        ## Sign with 48 bits Key of the step 1
        sub_key=key_set[it]
        signed_x = sign(un_sboxed, sub_key)

        ## Shrink x from 48 to 32
        shrunk_x = self.shrink_x(signed_x)
        assert(len(shrunk_x) == 32)
        
        ## sign x and y
        x = sign(shrunk_x, y)

        ## Swap side between output x and y from step 3-1 and consolidate them to make 64 bits
        n_list = x + y
        assert len(n_list) == 64
      
      return n_list

    
    def encrypt(self):
      # Initial Permutation of input
      self.n_list = self.init_perm(self.n_list)

      # Feistel Net ** Repeat 16 times of this round function
      self.n_list = self.feistel_net(self.n_list)
      
      # Final Permutation (Reverse of Initial Permutation)
      self.n_list = self.last_perm(self.n_list)
      
      return list_to_binary(self.n_list), self.n_list


    def decrypt(self, enc_lis, key_set):
      # Initial Permutation of input
      _n_list = self.init_perm(enc_lis)
      
      # Reverse Feistel Net
      _n_list = self.rev_feistel_net(_n_list, key_set)
      
      # Final Permutation
      _n_list = self.last_perm(_n_list)
      
      return list_to_binary(_n_list), _n_list
