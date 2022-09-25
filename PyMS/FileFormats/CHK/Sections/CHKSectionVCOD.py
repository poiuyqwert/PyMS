
from ..CHKSection import CHKSection
from ..CHKRequirements import CHKRequirements

from ....Utilities.utils import pad

import struct

class CHKSectionVCOD(CHKSection):
	NAME = 'VCOD'
	REQUIREMENTS = CHKRequirements(CHKRequirements.VER_ALL, CHKRequirements.MODE_ALL)

	DEFAULT_CODE = '4\x19\xcaw\x99\xdchq\n`\xbf\xc3\xa7\xe7u\xa7\x1f)}\xa6\xd7\xb0:\xbb\xcc1$\xed\x17L\x13\x0be \xa2\xb7\x91\xbd\x18k\x8d\xc3]\xdd\xe2z\xd57\xf6Yd\xd4c\x9a\x12\x0fC\\.F\xe3t\xf8*\x08j7\x067\xf6\xd6;\x0e\x94c\x16Eg\\\xec\xd7{\xf7\xb7\x1a\xfc\xd4\x9es\xfa?\x8c.\xc0\xe1\x0f\xd1t\t\x07\x95\xe3d\xd7u\x16ht\x99\xa7O\xda\xd5 \x18\x1f\xe7\xe6\xa0\xbe\xa6\xb6\xe3\x1f\xca\x0c\xefp1\xd5\x1a1M\xb8$5\xe3\xf8\xc7}\xe1\x1aX\xde\xf4\x05\'C\xba\xac\xdb\x07\xdci\xbe\n\xa8\x8f\xecI\xd7X\x16?\xe5\xdb\xc1\x8aA\xcf\xc0\x05\x9d\xca\x1cr\xa2\xb1_\xa5\xc4#p\x9b\x84\x04\xe1\x14\x80{\x90\xda\xfa\xdbi\x06\xa3\xf3\x0f@\xbe\xf3\xce\xd4\xe3\xc9\xcb\xd7Z@\x014\xf2h\x14\xf88\x8e\xc5\x1a\xfe\xd6=KS\x05\x05\xfa4\x10E\x8e\xdd\x91i\xfe\xaf\xe0\xee\xf0\xf3H~\xdd\x9f\xad\xdcubz\xac\xe51\x1bbg \xcd6M\xe0\x98!t\xfb\tyq6g\xcd\x7fw_\xd6<\xa2\xa2\xa6\xc6\x1a\xe3\xcejN\xcd\xa9l\x86\xba\x9d;\xb5\xf4v\xfd\xf8D\xf0\xbc.\xe9n)#%/k\x08\xab\'Dz\x12\xcc\x99\xed\xdc\xf2u\xc5<8~\xf7\x1c\x1b\xc5\xd1-\x94e\x06\xc9H\xdd\xbe2-\xac\xb5\xc92\x81fJ\xd845?\x15\xdf\xb2\xee\xeb\xb6\x04\xf6M\x965B\x94\x9cb\x8a\xd3aR\xa8{o\xdca\xfc\xf4l\x14-\xfe\x99\xea\xa4\n\xe8\xd9\xfe\x13\xd0HDY\x80f\xf3\xe34\xd9\x8d\x19\x16\xd7c\xfe0\x18~:\x9b\x8d\x0f\xb1\x12\xf0\xf5\x8c\nxX\xdb>c\xb8\x8c:\xaa\xf3\x8e7\x8a\x1a.\\1\xf9\xef\xe3m\xe3~\x9b\xbd>\x13\xc6D\xc0\xb9\xbc:\xda\x90\xa4\xad\xb0t\xf8W\'\x89G\xe6?7\xe4ByZ\xdfC\x8d\xee\xb4\nI\xe8<\xc3\x88\x1a\x88\x01kv\x8a\xc3\xfd\xa3\x16zNV\xa7\x7f\xcb\xba\x02^\x1c\xec\xb0\xb9\xc9v\x1e\x82\xb19>\xc9W\xc5\x19$8L]/T\xb8o]W\x8e0\xa1\nRm\x18q^\x13\x06\xc3Y\x1f\xdc>b\xdc\xda\xb5\xeb\x1b\x91\x95\xf9\xa7\x91\xd5\xda3S\xcek\xf5\x00p\x01\x7f\xd8\xee\xe8\xc0\n\xf1\xcec\xeb\xb6\xd3x\xef\xcc\xa5\xaa]\xbc\xa4\x96\xab\xf2\xd2a\xff\xea\x9a\xa8j\xed\xa2\xbd>\xeda9\xc1\x82\x92\x166#\xb1\xb0\xa0$\xe5\x05\x9b\xa7\xaa\r\x12\x9b3\x83\x92 \xda%\xb0\xec\xfc$\xd08#\xfc\x95\xf2t\x80s\xe5\x19\x97P}DE\x93D\xdb\xa2\xad\x1diD\x14\xee\xe7,\x7f\x87\xff8\x9e2\xf1M\xbc)\xdaB\'&\xfe\xc1\xd2+\xa9\xf6Bz\x0e\xcb\xe8|\xd1\x0f[\xecVi\xb7a1\xb4m\xf9%@4ym\xfaS\xa7\x0b\xfa\xa4\x82\xce\xc3EIa\rE,\x8f(I`\xf7\xf3}\xc9\x1e\x0f\xd0\x89\xc1&R\xf8\xd3M\x8f5\x14\xba\x9d_\x0b\x07\xa9J\x00\xf7\"&/>g\xfb\x1f\xa1\x9c\x11\xc6iO]fX4\x15\x90l\xe5TF\xaf_c\xd6\x8a\x0c\x95\xdf\xbd\r\xe4\xaf\xbf@@L\xa3\xf6Qq)\xed&\xf8\x85(\"\xd5\xbf\xbe\xcf\xfa(\xc5\x7fQ\xb8\x06c\x07\xec\xbd\x8f)\xfaU~q\x1a@2f\xe8\xd4\xde\x9d\xd4^\xfc\x93z=\xd5;\xcdu.\x80\nOt\x87\x1b\xcc\x8f\xea\x9a\xa9\xdb|\x16S\xe5\xef\xabx\xc1n\xa4r\x89Z\x98,pP\xfb\xa1\xdf\x1fk\xb7\xd9D\x07\x80\x82V\xfd\xbf\xc0\x83\x0eI\xd0[\x1ehj\x0e\x9a\xc2\x0b/\x8eC\xa0\xe1\x99\x0c\xf6\xb2\xe0z\x1c^,\xc8\xa0E<\x0b\xe9\x88\xac\xb9\x96\xc6t\xae\x83*\xbb\x13\xfae\xebO\x1f\xa6\xb0\x8a\x8a\xe1\x81\xe9\xb8\xb9\xd5U\x15NE\xf2\xad\x9b>\xc25~_\x92.r\xb6[h#n\xc6E\x0e\xe9;\x87\xd4\xf4A\xc0\xe3\xa8\x05D\xbe\xe4\x0f\x8a\x13\x1a\xc47\xf4Z@U\xef\x9dy\x1dKJy:\x9cv\x857\xcc\x82=\x0f\xb6`\xa6\x93~\xbd\\\xc2\xc4r\xc7\x7f\x90M\x1b\x96\x10\x13\x05hh5\xc0{\xffF\x85C*'
	DEFAULT_OPCODES = (1, 4, 5, 6, 2, 1, 5, 2, 0, 3, 7, 7, 5, 4, 6, 3)
	
	def __init__(self, chk):
		CHKSection.__init__(self, chk)
		self.code = CHKSectionVCOD.DEFAULT_CODE
		self.opcodes = CHKSectionVCOD.DEFAULT_OPCODES
	
	def load_data(self, data):
		self.code = data[:1024]
		self.opcodes = list(struct.unpack('<16B',data[1024:1024+16]))
	
	def save_data(self):
		return self.code + struct.pack('<16B',*self.opcodes)

	def decompile(self):
		result = '%s:\n\t%s\n' % (self.NAME, pad('Code',self.code.encode('hex')))
		for n,opcode in enumerate(self.opcodes):
			result += '\t%s\n' % (pad('Opcode%02d' % n, opcode))
		return result
