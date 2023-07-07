
from __future__ import annotations

from .PyMSError import PyMSError
from . import Struct

import struct

from typing import Any, Type, TypeVar, TypeAlias, overload

AnyStruct = str | struct.Struct

S = TypeVar('S', bound=Struct.Struct)
AnyFormat: TypeAlias = str | struct.Struct | Struct.Field | Type[Struct.Struct]

class BytesScanner(object):
	def __init__(self, data: bytes, address: int = 0) -> None:
		self.data = data
		self.address = address

	def matches(self, data: bytes, consume: bool = True) -> bool:
		matches = data.startswith(data, self.address)
		if matches and consume:
			self.address += len(data)
		return matches

	def skip(self, size: int) -> None:
		self.address += size

	@overload
	def peek(self, format: str) -> tuple[Any, ...]: ...
	@overload
	def peek(self, format: struct.Struct) -> tuple[Any, ...]: ...
	@overload
	def peek(self, format: Struct.IntField) -> int: ...
	@overload
	def peek(self, format: Struct.FloatField) -> float: ...
	@overload
	def peek(self, format: Struct.StringField) -> str: ...
	@overload
	def peek(self, format: Struct.IntArrayField) -> list[int]: ...
	@overload
	def peek(self, format: Struct.FloatArrayField) -> list[float]: ...
	@overload
	def peek(self, format: Struct.Field) -> Any: ...
	@overload
	def peek(self, format: Type[S]) -> S: ...
	def peek(self, format: AnyFormat) -> Any:
		if isinstance(format, str):
			return struct.unpack_from(format, self.data, self.address)
		elif isinstance(format, struct.Struct):
			return format.unpack_from(self.data, self.address)
		elif isinstance(format, Struct.Field):
			return format.unpack(self.data, self.address)
		else: # if is Type[S]
			return format.unpack(self.data, self.address)

	@overload
	def scan(self, format: str) -> tuple[Any, ...]: ...
	@overload
	def scan(self, format: struct.Struct) -> tuple[Any, ...]: ...
	@overload
	def scan(self, format: Struct.IntField) -> int: ...
	@overload
	def scan(self, format: Struct.FloatField) -> float: ...
	@overload
	def scan(self, format: Struct.StringField) -> str: ...
	@overload
	def scan(self, format: Struct.IntArrayField) -> list[int]: ...
	@overload
	def scan(self, format: Struct.FloatArrayField) -> list[float]: ...
	@overload
	def scan(self, format: Struct.Field) -> Any: ...
	@overload
	def scan(self, format: Type[S]) -> S: ...
	def scan(self, format: AnyFormat) -> Any:
		result = self.peek(format)
		size = 0
		if isinstance(format, str):
			size = struct.calcsize(format)
		elif isinstance(format, struct.Struct):
			size = format.size
		elif isinstance(format, Struct.Field):
			size = format.size
		else: # if is Type[S]
			size = format.calcsize()
		self.address += size
		return result

	def scan_cstr(self, encoding: str = 'utf-8') -> str:
		start_address = self.address
		while self.address < len(self.data):
			byte = self.data[self.address]
			self.address += 1
			if byte == 0:
				return self.data[start_address:self.address].decode(encoding)
		raise PyMSError('Scan', 'String has no ending')

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
