
from __future__ import annotations

from .PyMSError import PyMSError
from . import Struct

import struct

from typing import Any, Type, TypeVar, TypeAlias, overload

AnyStruct = str | struct.Struct

S = TypeVar('S', bound=Struct.Struct)
AnyFormat: TypeAlias = str | struct.Struct | Struct.Field | Type[Struct.Struct]

class BytesScanner:
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
	def can_scan(self, data_format: str) -> tuple[Any, ...]: ...
	@overload
	def can_scan(self, data_format: struct.Struct) -> tuple[Any, ...]: ...
	@overload
	def can_scan(self, data_format: Struct.IntField) -> int: ...
	@overload
	def can_scan(self, data_format: Struct.FloatField) -> float: ...
	@overload
	def can_scan(self, data_format: Struct.StringField) -> str: ...
	@overload
	def can_scan(self, data_format: Struct.IntArrayField) -> list[int]: ...
	@overload
	def can_scan(self, data_format: Struct.FloatArrayField) -> list[float]: ...
	@overload
	def can_scan(self, data_format: Struct.Field) -> Any: ...
	@overload
	def can_scan(self, data_format: Type[S]) -> S: ...
	def can_scan(self, data_format: AnyFormat) -> Any:
		size = 0
		if isinstance(data_format, str):
			size = struct.calcsize(data_format)
		elif isinstance(data_format, struct.Struct):
			size = data_format.size
		elif isinstance(data_format, Struct.Field):
			size = data_format.size
		else: # if is Type[S]
			size = data_format.calcsize()
		return self.remaining_len() >= size

	@overload
	def peek(self, data_format: str) -> tuple[Any, ...]: ...
	@overload
	def peek(self, data_format: struct.Struct) -> tuple[Any, ...]: ...
	@overload
	def peek(self, data_format: Struct.IntField) -> int: ...
	@overload
	def peek(self, data_format: Struct.FloatField) -> float: ...
	@overload
	def peek(self, data_format: Struct.StringField) -> str: ...
	@overload
	def peek(self, data_format: Struct.IntArrayField) -> list[int]: ...
	@overload
	def peek(self, data_format: Struct.FloatArrayField) -> list[float]: ...
	@overload
	def peek(self, data_format: Struct.Field) -> Any: ...
	@overload
	def peek(self, data_format: Type[S]) -> S: ...
	def peek(self, data_format: AnyFormat) -> Any:
		if isinstance(data_format, str):
			return struct.unpack_from(data_format, self.data, self.address)
		elif isinstance(data_format, struct.Struct):
			return data_format.unpack_from(self.data, self.address)
		elif isinstance(data_format, Struct.Field):
			return data_format.unpack(self.data, self.address)
		else: # if is Type[S]
			return data_format.unpack(self.data, self.address)

	@overload
	def scan(self, data_format: str) -> tuple[Any, ...]: ...
	@overload
	def scan(self, data_format: struct.Struct) -> tuple[Any, ...]: ...
	@overload
	def scan(self, data_format: Struct.IntField) -> int: ...
	@overload
	def scan(self, data_format: Struct.FloatField) -> float: ...
	@overload
	def scan(self, data_format: Struct.StringField) -> str: ...
	@overload
	def scan(self, data_format: Struct.IntArrayField) -> list[int]: ...
	@overload
	def scan(self, data_format: Struct.FloatArrayField) -> list[float]: ...
	@overload
	def scan(self, data_format: Struct.Field) -> Any: ...
	@overload
	def scan(self, data_format: Type[S]) -> S: ...
	def scan(self, data_format: AnyFormat) -> Any:
		result = self.peek(data_format)
		size = 0
		if isinstance(data_format, str):
			size = struct.calcsize(data_format)
		elif isinstance(data_format, struct.Struct):
			size = data_format.size
		elif isinstance(data_format, Struct.Field):
			size = data_format.size
		else: # if is Type[S]
			size = data_format.calcsize()
		self.address += size
		return result

	def can_scan_bytes(self, length: int) -> bool:
		return self.remaining_len() >= length

	def peek_bytes(self, length: int) -> bytes:
		return self.data[self.address:self.address+length]

	def scan_bytes(self, length: int) -> bytes:
		result = self.peek_bytes(length)
		self.address += length
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

	def at_end(self) -> bool:
		return self.address == len(self.data)

	def is_offset_valid(self, offset: int) -> bool:
		return offset >= 0 and offset < len(self.data)

	def jump_to(self, address: int) -> None:
		self.address = address

	def remaining_len(self) -> int:
		return len(self.data) - self.address
