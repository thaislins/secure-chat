class SDES:
    def __init__(self):
        self.ip = [2, 6, 3, 1, 4, 8, 5, 7]
        self.ip_1 = [4, 1, 3, 5, 7, 2, 8, 6]
        self.ep = [4, 1, 2, 3, 2, 3, 4, 1]
        self.p4 = [2, 4, 3, 1]
        self.p10 = [3, 5, 2, 7, 4, 10, 1, 9, 8, 6]
        self.p8 = [6, 3, 7, 4, 8, 5, 10, 9]
        self.tableS0 = [[1, 0, 3, 2], [3, 2, 1, 0], [0, 2, 1, 3], [3, 1, 3, 2]]
        self.tableS1 = [[1, 1, 2, 3], [2, 0, 1, 3], [3, 0, 1, 0], [2, 1, 0, 3]]
        self.k1 = ''
        self.k2 = ''

    def permutation(self, bits, permutation):
        bits = bits + ('0'*(len(permutation) - len(bits)))
        result = [bits[permutation[i] - 1] for i in range(len(permutation))]
        return ''.join(result)

    def xor(self, bits, key):
        result = [str(int(bits [i]) ^ int(key[i])) for i in range(len(key))]
        return ''.join(result)

    def sbox(self, bits, table):
        [i, j] = [int(bits[ii] + bits[3 - ii], 2) for ii in range(2)]
        return bin(table[i][j])[2:].zfill(2)

    def rotate(self, bits):
        rot = [bits[i + 1] if i != len(bits) - 1 else str(bits[0]) for i in range(len(bits))]
        return ''.join(rot)

    def switch(self, left_bits, right_bits):
        return right_bits + left_bits

    def fk(self, left_bits, right_bits, key):
        ep_result = self.permutation(right_bits, self.ep)
        xor_result = self.xor(ep_result,key)
        left, right = self.sbox(xor_result[:4],self.tableS0), self.sbox(xor_result[4:],self.tableS1)
        p4_result = self.permutation(left + right, self.p4)
        left_bits = self.xor(p4_result, left_bits)

        return left_bits

    def execute(self, message, key1, key2):
        message_result = ''

        for i in message:
            char = self.char2bits(i)
            ip_result = self.permutation(char, self.ip)
            left_bits, right_bits = ip_result[:4], ip_result[4:]
            left_bits = self.fk(left_bits,right_bits,key1)
            switch_result = self.switch(left_bits,right_bits)
            #-------------------------------------------------------
            left_bits = self.fk(switch_result[:4],switch_result[4:],key2)
            bits = left_bits + switch_result[4:]
            message_result += self.permutation(bits, self.ip_1)

        return message_result

    def define_key(self, key):
        key = self.string2bits(key)
        ip_result = self.permutation(key, self.p10)
        ls1 = self.rotate(ip_result[:5]) + self.rotate(ip_result[5:])
        ls2 = self.rotate(self.rotate(ls1[:5])) + self.rotate(self.rotate(ls1[5:]))

        self.k1, self.k2 = self.permutation(ls1,self.p8), self.permutation(ls2,self.p8)

    def char2bits(self, s=''):
        return bin(ord(s))[2:].zfill(8)

    def string2bits(self, s=''):
        return ''.join([bin(ord(x))[2:].zfill(8) for x in s])

    def bits2string(self, b):
        return ''.join([chr(int(b[i*8:(i*8)+8], 2)) for i in range(len(b)//8)])

    def encode(self, message):
        return self.execute(message, self.k1, self.k2)

    def decode(self, message):
        return self.bits2string(self.execute(self.bits2string(message), self.k2, self.k1))



