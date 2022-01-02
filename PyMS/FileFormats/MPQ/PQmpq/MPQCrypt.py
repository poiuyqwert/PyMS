
# `crypt_table`, `hash_string`, `encrypt`, and `decrypt` are
# based off of SFmpq (by Quantam and ShadowFlare), which is based off StormLib (by Ladislav Zezula)

import struct

_crypt_table = None
def crypt_table():
	global _crypt_table
	if _crypt_table == None:
		table = [0] * 0x500
		seed = 0x00100001
		for index1 in range(0x100):
			for index2 in range(index1, index1 + 5 * 0x100, 0x100):
				seed = (seed * 125 + 3) % 0x2AAAAB
				temp1 = (seed & 0xFFFF) << 0x10
				seed = (seed * 125 + 3) % 0x2AAAAB
				temp2 = (seed & 0xFFFF)
				table[index2] = (temp1 | temp2)
		_crypt_table = tuple(table)
	return _crypt_table

class HashType:
	position = 0
	name_a = 1
	name_b = 2
	key = 3

def hash_string(string, hash_type):
	seed1 = 0x7FED7FED
	seed2 = 0xEEEEEEEE
	if hash_type == HashType.key:
		while '\\' in string:
			string = string[string.index('\\')+1:]
	chrs = (ord(c) for c in string.upper())
	for c in chrs:
		seed1 = (crypt_table()[(hash_type << 8) + c] ^ (seed1 + seed2)) & 0xFFFFFFFF
		seed2 = (c + seed1 + seed2 + (seed2 << 5) + 3) & 0xFFFFFFFF
	return seed1

LONG = struct.Struct('<L')

def decrypt(data, key):
	result = b''
	seed = 0xEEEEEEEE
	offset = 0
	max_offset = int(len(data) / 4.0) * 4
	while offset < max_offset:
		seed = (seed + crypt_table()[0x400 + (key & 0xFF)]) & 0xFFFFFFFF
		c = (LONG.unpack(data[offset:offset+4])[0] ^ (key + seed)) & 0xFFFFFFFF

		key = (((~key << 0x15) + 0x11111111) | (key >> 0x0B)) & 0xFFFFFFFF
		seed = (c + seed + (seed << 5) + 3) & 0xFFFFFFFF

		result += LONG.pack(c)
		offset += 4
	
	remaining = len(data) % 4
	if remaining:
		result += data[-remaining:]

	return result
