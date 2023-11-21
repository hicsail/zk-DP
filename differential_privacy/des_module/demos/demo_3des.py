from picozk import *
from des_module.utils import *
from des_module.tables import *
from des_module.triple_des import triple_DES

# Generate 3 sets of max 56bits keys
keys = [8289481480542705629, 8289481480542225629, 9128814805426305629]

# Generate 64 bits input
input_size = 64
# input_val, n_list = generate_bit(input_size)
input_val = 3271167758276528483
# fmt: off
n_list = [0, 0, 1, 0, 1, 1, 0, 1, 
          0, 1, 1, 0, 0, 1, 0, 1, 
          1, 0, 0, 0, 0, 1, 0, 1, 
          1, 0, 1, 1, 1, 1, 1, 0, 
          1, 0, 1, 0, 1, 0, 0, 0, 
          1, 1, 0, 0, 1, 0, 0, 0, 
          1, 0, 0, 0, 1, 0, 0, 1, 
          0, 1, 1, 0, 0, 0, 1, 1]
# fmt: on

assert len(n_list) == input_size

p = pow(2, 127) - 1

with PicoZKCompiler("../irs/picozk_test", field=[p], options=["ram"]):
    # Initiate DEC
    n_list = ZKList(n_list)
    DES_inst = triple_DES(keys)

    # DEC encryption
    enc_val, enc_lis = DES_inst.encrypt(n_list)
    assert len(enc_lis) == 64
    print(f"\nencrypted value :{val_of(enc_val)}")

    # DEC decryption
    dec_val, dec_list = DES_inst.decrypt(enc_lis)
    print(f"\ninput value     :{input_val}")
    print(f"decrypted value :{val_of(dec_val)}")
    assert input_val == val_of(dec_val)
