
from __future__ import annotations

from .PyMSError import PyMSError

import struct
from enum import StrEnum

from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from typing import Self, BinaryIO

class Endian(StrEnum):
	native = '@'
	native_standard = '='
	little = '<'
	big = '>'
	network = '!'

class Type:
	@staticmethod
	def format(char, count): # type: (str, int) -> str
		if count == 1:
			return char
		return '%d%s' % (count, char)

	@staticmethod
	def pad(count=1): # type: (int) -> str
		return Type.format('x', count)

	@staticmethod
	def s8(count=1): # type: (int) -> str
		return Type.format('b', count)

	@staticmethod
	def u8(count=1): # type: (int) -> str
		return Type.format('B', count)

	@staticmethod
	def s16(count=1): # type: (int) -> str
		return Type.format('h', count)

	@staticmethod
	def u16(count=1): # type: (int) -> str
		return Type.format('H', count)

	@staticmethod
	def s32(count=1): # type: (int) -> str
		return Type.format('l', count)

	@staticmethod
	def u32(count=1): # type: (int) -> str
		return Type.format('L', count)

	@staticmethod
	def s64(count=1): # type: (int) -> str
		return Type.format('q', count)

	@staticmethod
	def u64(count=1): # type: (int) -> str
		return Type.format('Q', count)

	@staticmethod
	def float(count=1): # type: (int) -> str
		return Type.format('f', count)

	@staticmethod
	def double(count=1): # type: (int) -> str
		return Type.format('d', count)

	@staticmethod
	def char(count=1): # type: (int) -> str
		return Type.format('c', count)

	@staticmethod
	def str_pascal(count): # type: (int) -> str
		return Type.format('p', count)

	@staticmethod
	def str(count): # type: (int) -> str
		return Type.format('s', count)

class Struct(object):
	_endian = Endian.little
	_fields = () # type: tuple[tuple[str, str], ...]

	_struct = None # type: struct.Struct

	@classmethod
	def build_struct(cls): # type: () -> None
		if cls._struct is None:
			cls._struct = struct.Struct(cls._endian + ''.join(ctype for _,ctype in cls._fields))

	@classmethod
	def size(cls): # type: () -> int
		cls.build_struct()
		return cls._struct.size

	@classmethod
	def unpack(cls, data, offset=0): # type: (bytes, int) -> Self
		cls.build_struct()
		if len(data) < offset + cls._struct.size:
			raise PyMSError('Struct', 'Not enough data (expected %d, got %d)' % (cls._struct.size, len(data) - offset))
		values = cls._struct.unpack(data[offset:offset + cls._struct.size])
		obj = cls()
		for (name,_),value in zip(cls._fields, values):
			setattr(obj, name, value)
		return obj

	@classmethod
	def unpack_array(cls, data, count, offset=0): # type: (bytes, int, int) -> list[Self]
		cls.build_struct()
		if len(data) < offset + cls._struct.size * count:
			raise PyMSError('Struct', 'Not enough data (expected %d, got %d)' % (cls._struct.size * count, len(data) - offset))
		array = []
		for _ in range(count):
			array.append(cls.unpack(data, offset))
			offset += cls._struct.size
		return array

	@classmethod
	def unpack_file(cls, file_handle): # type: (BinaryIO) -> Self
		cls.build_struct()
		try:
			data = file_handle.read(cls._struct.size)
		except:
			raise PyMSError('Struct', 'Not enough data (expected %d)' % (cls._struct.size))
		return cls.unpack(data)

	def __repr__(self): # type: () -> str
		result = """<%s.%s struct = '%s'
""" % (self.__class__.__module__, self.__class__.__name__, self._struct.format)
		for (name, _) in self._fields:
			value = getattr(self, name)
			if isinstance(value, str):
				value = value.encode('string_escape')
			result += "\t%s = %s\n" % (name, value)
		return result + ">"
