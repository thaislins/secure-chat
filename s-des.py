ip = [2, 6, 3, 1, 4, 8, 5, 7]
ip_1 = [4, 1, 3, 5, 7, 2, 8, 6]
ep = [4, 1, 2, 3, 2, 3, 4, 1]
p4 = [2, 4, 3, 1]
p10 = [3, 5, 2, 7, 4, 10, 1, 9, 8, 6]
p8 = [6, 3, 7, 4, 8, 5, 10, 9]
tableS0 = [[1, 0, 3, 2], [3, 2, 1, 0], [0, 2, 1, 3], [3, 1, 3, 2]]
tableS1 = [[1, 1, 2, 3], [2, 0, 1, 3], [3, 0, 1, 0], [2, 1, 0, 3]]

def permutation(bits, permutation):
	result = [bits[permutation[i] - 1] for i in range(len(permutation))]
	return ''.join(result)

def xor(bits, key):
	result = [str(int(bits [i]) ^ int(key[i])) for i in range(len(key))]
	return ''.join(result)

def sbox(bits, table):
	[i, j] = [int(bits[ii] + bits[3 - ii], 2) for ii in range(2)]
	return bin(table[i][j])[2:].zfill(2)

def rotate(bits):
	rot = [bits[i + 1] if i != len(bits) - 1 else str(bits[0]) for i in range(len(bits))]
	return ''.join(rot)

def switch(left_bits, right_bits):
	return right_bits + left_bits

def fk(left_bits, right_bits, key):
	ep_result = permutation(right_bits, ep)
	xor_result = xor(ep_result,key)
	left, right = sbox(xor_result[:4],tableS0), sbox(xor_result[4:],tableS1)
	p4_result = permutation(left + right, p4)
	left_bits = xor(p4_result, left_bits)
	
	return left_bits

def execute(message, key1, key2): 
	message_result = ''

	for i in message:
		char = char2bits(i)
		ip_result = permutation(char, ip)
		left_bits, right_bits = ip_result[:4], ip_result[4:]
		left_bits = fk(left_bits,right_bits,key1)
		switch_result = switch(left_bits,right_bits)
		#-------------------------------------------------------
		left_bits = fk(switch_result[:4],switch_result[4:],key2)
		bits = left_bits + switch_result[4:]
		message_result += permutation(bits,ip_1)

	return message_result

def generate_keys(key):
	ip_result = permutation(key, p10)
	ls1 = rotate(ip_result[:5]) + rotate(ip_result[5:])
	ls2 = rotate(rotate(ls1[:5])) + rotate(rotate(ls1[5:]))

	return permutation(ls1,p8), permutation(ls2,p8)

def char2bits(s=''):
    return bin(ord(s))[2:].zfill(8)

def bits2string(b):
    return ''.join([chr(int(b[i*8:(i*8)+8], 2)) for i in range(len(b)//8)])

def encode(message, k1, k2):
	return execute(message,k1,k2)

def decode(message, k2, k1):
	return execute(bits2string(message),k2,k1)

def run():
	message = "Hello, how are you?"
	key = '1010000010'

	k1, k2 = generate_keys(key)
	encrypted_message = encode(message,k1,k2)
	decrypted_message = decode(encrypted_message,k2,k1)
	print(bits2string(decrypted_message))

if __name__ == '__main__':
    run()
