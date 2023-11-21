from .des import DES
from .utils import list_to_binary


class triple_DES:
    def __init__(self, keys):
        assert len(keys) == 3
        self.DES_inst_f = DES(keys[0])
        self.DES_inst_s = DES(keys[1])
        self.DES_inst_t = DES(keys[2])

    def encrypt(self, input_list):
        _, enc_lis = self.DES_inst_f.encrypt(input_list)
        _, dec_lis = self.DES_inst_s.decrypt(enc_lis)
        _, fin_enc_lis = self.DES_inst_t.encrypt(dec_lis)

        return list_to_binary(fin_enc_lis), fin_enc_lis

    def decrypt(self, input_list):
        _, dec_lis = self.DES_inst_t.decrypt(input_list)
        _, enc_lis = self.DES_inst_s.encrypt(dec_lis)
        _, fin_enc_lis = self.DES_inst_f.decrypt(enc_lis)

        return list_to_binary(fin_enc_lis), fin_enc_lis
