class RC4:

    def __init__(self):
        self.key = ''

    def ksa(self, key):
        '''Initialization and initial permutation of S'''
        S = list(range(256))

        j = 0
        for i in range(256):
            j = (j + S[i] + key[i % len(key)]) % 256
            S[i], S[j] = S[j], S[i]  # swap

        return S

    def prga(self, message, S):
        i = 0
        j = 0
        K = []

        for char in message:
            i = (i + 1) % 256
            j = (j + S[i]) % 256
            S[i], S[j] = S[j], S[i]
            K.append(S[(S[i] + S[j]) % 256])

        return K

    def key2ascii(self, char):
        return [ord(c) for c in char]

    def convert_chipertext(self, ciphertext):
        return [ord(str(ch)) for ch in ciphertext]

    def define_key(self, k):
        self.key = k

    def encrypt(self, message):
        S = self.ksa(self.key2ascii(self.key))
        K = iter(self.prga(message, S))
        ciphertext = ["%02X" % (ord(c) ^ next(K)) for c in message]

        return ''.join(ciphertext)

    def decrypt(self, ciphertext):
        try:
            ciphertext = bytes.fromhex(ciphertext)
            S = self.ksa(self.key2ascii(self.key))
            K = iter(self.prga(ciphertext, S))
            plaintext = [chr(c ^ next(K)) for c in ciphertext]

            return ''.join(plaintext)
        except ValueError as e:
            print(e)
            return ''
