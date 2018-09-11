import binascii

key = 'Key'

def ksa(key):
    S = [i for i in range(256)]

    j = 0
    for i in range(256):
        j = (j + S[i] + key[i % len(key)]) % 256
        S[i], S[j] = S[j], S[i]  # swap

    return S

def prga(message, S):
    i = 0
    j = 0
    K = []

    for char in message:
        i = (i + 1) % 256
        j = (j + S[i]) % 256
        S[i], S[j] = S[j], S[i]
        K.append(S[(S[i] + S[j]) % 256])

    return K

def key2ascii(char):
    return [ord(c) for c in char]

def convert_chipertext(ciphertext):
    return [ord(str(ch)) for ch in ciphertext]

def define_key(k):
    global key 
    key = k

def encode(message):
    S = ksa(key2ascii(key))
    K = iter(prga(message, S))
    ciphertext = ["%02X" % (ord(c) ^ next(K)) for c in message]
    
    return ''.join(ciphertext)

def decode(ciphertext):
    ciphertext = binascii.unhexlify(ciphertext)
    S = ksa(key2ascii(key))
    K = iter(prga(ciphertext, S))
    plaintext = [chr(c ^ next(K)) for c in ciphertext]
    
    return ''.join(plaintext)
