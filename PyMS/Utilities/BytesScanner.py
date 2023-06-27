
from __future__ import annotations

from .PyMSError import PyMSError

import struct

from typing import overload, Any, Type

AnyStruct = str | struct.Struct

class BytesScanner(object):
	def __init__(self, data: bytes, address: int = 0) -> None:
		self.data = data
		self.address = address

	def matches(self, data: bytes, seek: bool = True) -> bool:
		matches = data.startswith(data, self.address)
		if matches and seek:
			self.address += len(data)
		return matches

	def peek(self, format: AnyStruct) -> tuple[Any, ...]:
		if isinstance(format, str):
			return struct.unpack_from(format, self.data, self.address)
		return format.unpack_from(self.data, self.address)

	def peek_ints(self, format: AnyStruct) -> tuple[int, ...]:
		return self.peek(format)

	def scan(self, format: AnyStruct) -> tuple[Any, ...]:
		result = self.peek(format)
		if isinstance(format, str):
			self.address += struct.calcsize(format)
		else:
			self.address += format.size
		return result

	def scan_ints(self, format: AnyStruct) -> tuple[int, ...]:
		return self.scan(format)

	def scan_cstr(self, encoding: str = 'utf-8') -> str:
		start_address = self.address
		while self.address < len(self.data):
			byte = self.data[self.address]
			self.address += 1
			if byte == 0:
				return self.data[start_address:self.address].decode(encoding)
		raise PyMSError('Scan', 'String has no ending')

	def scan_str(self, block_size: int, encoding: str = 'utf-8') -> str:
		data = self.data[self.address:self.address+block_size]
		if b'\x00' in data:
			data = data[:data.index(b'\x00')]
		self.address += block_size
		return data.decode(encoding)

	def clone(self, address: int | None = None) -> BytesScanner:
		if address is None:
			address = self.address
		return BytesScanner(self.data, address)

	def at_end(self):
		return self.address == len(self.data)

	def jump_to(self, address):
		self.address = address

	def remaining_len(self):
		return len(self.data) - self.address
