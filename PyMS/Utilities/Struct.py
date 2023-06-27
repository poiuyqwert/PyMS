
from __future__ import annotations

from .PyMSError import PyMSError

import struct
from enum import StrEnum

from typing import TYPE_CHECKING, Any, Self, BinaryIO

class Endian(StrEnum):
	native = '@'
	native_standard = '='
	little = '<'
	big = '>'
	network = '!'

class Type:
	FLOAT_MIN = None # type: float
	FLOAT_MAX = None # type: float
	DOUBLE_MIN = None # type: float
	DOUBLE_MAX = None # type: float

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
	def sfloat(count=1): # type: (int) -> str
		return Type.format('f', count)

	@staticmethod
	def sdouble(count=1): # type: (int) -> str
		return Type.format('d', count)

	@staticmethod
	def char(count=1): # type: (int) -> str
		return Type.format('c', count)

	@staticmethod
	def str_pascal(count): # type: (int) -> str
		return Type.format('p', count)

	@staticmethod
	def string(count): # type: (int) -> str
		return Type.format('s', count)

	@staticmethod
	def size(type, endian=Endian.little):
		return struct.calcsize(endian + type)

	@staticmethod
	def numeric_limits(type: str) -> tuple[int | float, int | float]:
		if type == 'f':
			if Type.FLOAT_MIN == None:
				Type.FLOAT_MIN = struct.unpack('>f', b'\xff\x7f\xff\xff')[0]
				Type.FLOAT_MAX = struct.unpack('>f', b'\x7f\x7f\xff\xff')[0]
			return (Type.FLOAT_MIN, Type.FLOAT_MAX)
		elif type == 'd':
			if Type.DOUBLE_MIN == None:
				Type.DOUBLE_MAX = struct.unpack('>d', b'\x7f\xef\xff\xff\xff\xff\xff\xff')[0]
				Type.DOUBLE_MIN = struct.unpack('>d', b'\xff\xef\xff\xff\xff\xff\xff\xff')[0]
			return (Type.DOUBLE_MIN, Type.DOUBLE_MAX)
		elif type in 'sp':
			type = Type.char()
		min = 0
		max = 2 ** Type.size(type)
		if type.isupper():
			min = -max/2
			max = max/2 - 1
		else:
			max -= 1
		return (min, max)

class Value:
	@staticmethod
	def unpack(data, type, offset=0, endian=Endian.little): # type: (bytes, str, int, str) -> Any
		size = struct.calcsize(endian + type)
		if len(data) < offset + size:
			raise PyMSError('Value', 'Not enough data (expected %d, got %d)' % (size, len(data) - offset))
		result = struct.unpack(endian + type, data[offset:offset + size])
		if len(result) == 1:
			return result[-1]
		return result

	@staticmethod
	def pack(value, type, endian=Endian.little): # type: (Any, str, str) -> bytes
		if not isinstance(value, tuple):
			value = (value,)
		return struct.pack(endian + type, *value)

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
