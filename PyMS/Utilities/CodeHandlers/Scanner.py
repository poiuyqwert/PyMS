
from .. import Struct
from ..PyMSError import PyMSError

class Scanner(object):
	def __init__(self, data, address=0): # type: (bytes, int) -> Scanner
		self.data = data
		self.address = address

	def peek(self, type): # type: (str | Type[Struct.Struct]) -> Any
		if isinstance(type, str):
			return Struct.Value.unpack(self.data, type, self.address)
		return type.unpack(self.data, self.address)

	def scan(self, type): # type: (str | Type[Struct.Struct]) -> Any
		result = self.peek(type)
		if isinstance(type, str):
			self.address += Struct.Type.size(type)
		else:
			self.address += type.size()
		return result

	def scan_str(self): # type: () -> str
		result = ''
		while self.address < len(self.data):
			byte = self.data[self.address]
			self.address += 1
			if byte == '\x00':
				break
			result += byte
		else:
			raise PyMSError('Scan', 'String has no ending')
		return result

	def clone(self, address=None): # type: (int | None) -> Scanner
		if address == None:
			address = self.address
		return Scanner(self.data, address)

	def at_end(self):
		return self.address == len(self.data)

	def jump_to(self, address):
		self.address = address
