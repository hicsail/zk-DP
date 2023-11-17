from utils import *
from tables import *
from des import DES

# Generate 56bits key and expand
orig_key_size = 64  
# key, bit_list_key = generate_bit(orig_key_size)
key = 8289481480542705629
# fmt: off
bit_list_key = [0, 1, 1, 1, 0, 0, 1, 1, 
                0, 0, 0, 0, 1, 0, 1, 0, 
                0, 0, 1, 0, 0, 1, 1, 1, 
                0, 1, 1, 1, 1, 1, 0, 0, 
                1, 0, 1, 0, 1, 0, 1, 1, 
                1, 1, 1, 0, 1, 1, 0, 1, 
                0, 1, 0, 1, 0, 1, 1, 1, 
                1, 1, 0, 1, 1, 1, 0, 1]
print(f'\nkey value       :{key}')
assert len(bit_list_key) == orig_key_size


a0 = list_to_binary(bit_list_key)
assert a0 == 8289481480542705629

# Generate 64 bits input
input_size = 64
# input_val, n_list = generate_bit(input_size)
input_val = 3271167758276528483
n_list = [0, 0, 1, 0, 1, 1, 0, 1, 
          0, 1, 1, 0, 0, 1, 0, 1, 
          1, 0, 0, 0, 0, 1, 0, 1, 
          1, 0, 1, 1, 1, 1, 1, 0, 
          1, 0, 1, 0, 1, 0, 0, 0, 
          1, 1, 0, 0, 1, 0, 0, 0, 
          1, 0, 0, 0, 1, 0, 0, 1, 
          0, 1, 1, 0, 0, 0, 1, 1]
s = ''

assert len(n_list) == input_size

# Initiate DEC
DES = DES(n_list, bit_list_key)

# DEC encryption
enc_val, enc_lis = DES.encrypt()
assert len(enc_lis) == 64
print(f"\nencrypted value :{enc_val}")


# DEC decryption
dec_val, dec_list = DES.decrypt()
print(f"\ninput value     :{input_val}")
print(f"decrypted value :{dec_val}")
assert input_val == dec_val
# fmt: on
