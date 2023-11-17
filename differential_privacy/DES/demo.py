from picozk import *
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
print(a0)
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

assert len(n_list) == input_size

p = pow(2, 127) - 1
with PicoZKCompiler("irs/picozk_test", field=[p], options=["ram"]):

    # Initiate DEC
    n_list = ZKList(n_list)
    bit_list_key = ZKList(list(bit_list_key))
    DES = DES(n_list, bit_list_key)


    # DEC encryption
    enc_val, enc_lis = DES.encrypt()
    assert len(enc_lis) == 64
    print(f"\nencrypted value :{val_of(enc_val)}")


    # DEC decryption
    dec_val, dec_list = DES.decrypt()
    print(f"\ninput value     :{input_val}")
    print(f"decrypted value :{val_of(dec_val)}")
    assert input_val == val_of(dec_val)
    # fmt: on
