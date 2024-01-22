from picozk import *
from aes_module.utils import *
from aes_module.aes import AES, ShiftRows, InvShiftRows

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

p = pow(2, 127) - 1
with PicoZKCompiler("irs/picozk_test", field=[p], options=["ram"]):
    # e2s Test for enc and dec
    int_str = 1987034928369859712
    _key = 1235282586324778

    aes = AES(_key)
    cipher_text = aes.encrypt(int_str)
    _cipher_text = [val_of(ct) for ct in cipher_text]
    print("\ncipher_text", _cipher_text)

    InvPlainText = aes.decrypt(cipher_text)
    _InvPlainText = [val_of(pt) for pt in InvPlainText]
    print("\nInvPlainText", _InvPlainText)

    assert _InvPlainText == int_to_bitlist(int_str, 128)
