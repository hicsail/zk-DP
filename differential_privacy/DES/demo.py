from utils import *
from des import DES

# Generate 56bits key and expand
orig_key_size = 56
key, bit_list_key = generate_bit(orig_key_size)
assert len(bit_list_key) == orig_key_size


# Generate 64 bits input
input_size = 64
input_val, n_list = generate_bit(input_size)
print(f'input value     :{input_val}')
assert len(n_list) == input_size


# Initiate DEC
DES = DES(n_list, bit_list_key)


# DEC encryption
enc_val, enc_lis = DES.encrypt()
assert len(enc_lis) == 64
print(f'encrypted value :{enc_val}')


# DEC decryption
dec_val, dec_list= DES.decrypt()
print(f'decrypted value :{dec_val}')


# Simple tests
test_input = [i for i in range(64)]
permed = DES.init_perm(test_input)
repermed = DES.last_perm(permed)

assert test_input == repermed