
from __future__ import annotations

from .PyMSError import PyMSError

import struct
from enum import StrEnum

from typing import Self, BinaryIO, Literal, Sequence

class Endian(StrEnum):
	native = '@'
	native_standard = '='
	little = '<'
	big = '>'
	network = '!'

class Format(StrEnum):
	pad = 'x'
	s8 = 'b'
	u8 = 'B'
	s16 = 'h'
	u16 = 'H'
	s32 = 'l'
	u32 = 'L'
	s64 = 'q'
	u64 = 'Q'
	float = 'f'
	double = 'd'
	char = 'c'
	pstr = 'p'
	str = 's'

	@property
	def is_signed(self) -> bool:
		match self:
			case Format.pad:
				return False
			case Format.s8:
				return True
			case Format.u8:
				return False
			case Format.s16:
				return True
			case Format.u16:
				return False
			case Format.s32:
				return True
			case Format.u32:
				return False
			case Format.s64:
				return True
			case Format.u64:
				return False
			case Format.float:
				return True
			case Format.double:
				return True
			case Format.char:
				return False
			case Format.pstr:
				return False
			case Format.str:
				return False

class Type:
	def __init__(self, format: Format) -> None:
		self._format = format

	@property
	def is_signed(self) -> bool:
		return self._format.is_signed

	@property
	def format(self) -> str:
		return self._format.value

class PadType(Type):
	def __init__(self, format: Literal[Format.pad], size: int):
		Type.__init__(self, format)
		self.size = size

	@property
	def format(self) -> str:
		if self.size == 1:
			return self._format.value
		return f'{self.size}{self._format}'

class IntType(Type):
	def __init__(self, format: Literal[Format.s8, Format.u8, Format.s16, Format.u16, Format.s32, Format.u32, Format.s64, Format.u64]):
		Type.__init__(self, format)

class FloatType(Type):
	def __init__(self, format: Literal[Format.float, Format.double]):
		Type.__init__(self, format)

class StringType(Type):
	def __init__(self, format: Literal[Format.char, Format.pstr, Format.str], size: int):
		Type.__init__(self, format)
		self.size = size

	@property
	def format(self) -> str:
		if self._format == Format.char and self.size == 1:
			return self._format.value
		return f'{self.size}{self._format}'

def t_pad(size: int = 1) -> PadType:
	return PadType(Format.pad, size)
t_s8 = IntType(Format.s8)
t_u8 = IntType(Format.u8)
t_s16 = IntType(Format.s16)
t_u16 = IntType(Format.u16)
t_s32 = IntType(Format.s32)
t_u32 = IntType(Format.u32)
t_s64 = IntType(Format.s64)
t_u64 = IntType(Format.u64)
t_float = FloatType(Format.float)
t_double = FloatType(Format.double)
t_char = StringType(Format.char, 1)
def t_pstr(size: int) -> StringType:
	return StringType(Format.pstr, size)
def t_str(size: int) -> StringType:
	return StringType(Format.str, size)

class Array(Type):
	def __init__(self, format: Format, size: int):
		Type.__init__(self, format)
		self.size = size

	@property
	def format(self) -> str:
		return f'{self.size}{self._format}'

class IntArray(Array):
	def __init__(self, format: Literal[Format.pad, Format.s8, Format.u8, Format.s16, Format.u16, Format.s32, Format.u32, Format.s64, Format.u64], size: int):
		Array.__init__(self, format, size)

class FloatArray(Array):
	def __init__(self, format: Literal[Format.float, Format.double], size: int):
		Array.__init__(self, format, size)

def t_as8(size: int) -> IntArray:
	return IntArray(Format.s8, size)
def t_au8(size: int) -> IntArray:
	return IntArray(Format.u8, size)
def t_as16(size: int) -> IntArray:
	return IntArray(Format.s16, size)
def t_au16(size: int) -> IntArray:
	return IntArray(Format.u16, size)
def t_as32(size: int) -> IntArray:
	return IntArray(Format.s32, size)
def t_au32(size: int) -> IntArray:
	return IntArray(Format.u32, size)
def t_as64(size: int) -> IntArray:
	return IntArray(Format.s64, size)
def t_au64(size: int) -> IntArray:
	return IntArray(Format.u64, size)
def t_afloat(size: int) -> FloatArray:
	return FloatArray(Format.float, size)
def t_adouble(size: int) -> FloatArray:
	return FloatArray(Format.double, size)

class Field:
	def __init__(self, field_type: Type, endian: Endian = Endian.little) -> None:
		self.field_type = field_type
		self.endian = endian

	@property
	def is_signed(self) -> bool:
		return self.field_type.is_signed

	@property
	def size(self) -> int:
		return struct.calcsize(self.format)

	@property
	def format(self) -> str:
		return f'{self.endian}{self.field_type.format}'

	# _FLOAT_LIMITS: tuple[float, float] | None = None
	# _DOUBLE_LIMITS: tuple[float, float] | None = None
	# @overload
	# @staticmethod
	# def field_limits(field: IntField) -> tuple[int, int]: ...
	# @overload
	# @staticmethod
	# def field_limits(field: FloatField) -> tuple[float, float]: ...
	# @overload
	# @staticmethod
	# def field_limits(field: StringField) -> tuple[int, int]: ...
	# @staticmethod
	# def field_limits(field: IntField | FloatField | StringField) -> tuple[int | float, int | float]:
	# 	if field.field_type.format == _Format.float:
	# 		if FloatField._FLOAT_LIMITS is not None:
	# 			return FloatField._FLOAT_LIMITS
	# 		min = float(struct.unpack('>f', b'\xff\x7f\xff\xff')[0])
	# 		max = float(struct.unpack('>f', b'\x7f\x7f\xff\xff')[0])
	# 		FloatField._FLOAT_LIMITS = (min, max)
	# 		return (min, max)
	# 	elif field.field_type.format == _Format.double:
	# 		if FloatField._DOUBLE_LIMITS is not None:
	# 			return FloatField._DOUBLE_LIMITS
	# 		min = float(struct.unpack('>d', b'\xff\xef\xff\xff\xff\xff\xff\xff')[0])
	# 		max = float(struct.unpack('>d', b'\x7f\xef\xff\xff\xff\xff\xff\xff')[0])
	# 		FloatField._DOUBLE_LIMITS = (min, max)
	# 		return (min, max)
	# 	elif isinstance(field, StringField):
	# 		char_field = IntField(t_char, field.endian)
	# 		return (0, 2 ** char_field.size - 1)
	# 	else:
	# 		min = 0
	# 		max = 2 ** field.size
	# 		if field.is_signed:
	# 			min = -(max // 2)
	# 			max = (max // 2)
	# 		max -= 1
	# 		return (min, max)

class IntField(Field):
	def __init__(self, field_type: IntType, endian: Endian = Endian.little) -> None:
		Field.__init__(self, field_type, endian)

	def pack(self, value: int) -> bytes:
		return struct.pack(self.format, value)

	def unpack(self, data: bytes, offset: int = 0) -> int:
		return int(struct.unpack_from(self.format, data, offset)[0])

	@property
	def min(self) -> int:
		min = 0
		if self.is_signed:
			min = -((2 ** (self.size * 8)) // 2)
		return min
	
	@property
	def max(self) -> int:
		max = 2 ** (self.size * 8)
		if self.is_signed:
			max = (max // 2)
		max -= 1
		return max

class FloatField(Field):
	def __init__(self, field_type: FloatType, endian: Endian = Endian.little) -> None:
		Field.__init__(self, field_type, endian)

	def pack(self, value: float) -> bytes:
		return struct.pack(self.format, value)

	def unpack(self, data: bytes, offset: int = 0) -> float:
		return float(struct.unpack_from(self.format, data, offset)[0])

	_FLOAT_MIN: float | None = None
	_DOUBLE_MIN: float | None = None
	@property
	def min(self) -> float:
		if self.field_type.format == Format.float:
			if FloatField._FLOAT_MIN is not None:
				return FloatField._FLOAT_MIN
			min = float(struct.unpack('>f', b'\xff\x7f\xff\xff')[0])
			FloatField._FLOAT_MIN = min
			return min
		else:
			if FloatField._DOUBLE_MIN is not None:
				return FloatField._DOUBLE_MIN
			min = float(struct.unpack('>d', b'\xff\xef\xff\xff\xff\xff\xff\xff')[0])
			FloatField._DOUBLE_MIN = min
			return min

	_FLOAT_MAX: float | None = None
	_DOUBLE_MAX: float | None = None
	@property
	def max(self) -> float:
		if self.field_type.format == Format.float:
			if FloatField._FLOAT_MAX is not None:
				return FloatField._FLOAT_MAX
			max = float(struct.unpack('>f', b'\x7f\x7f\xff\xff')[0])
			FloatField._FLOAT_MAX = max
			return max
		else:
			if FloatField._DOUBLE_MAX is not None:
				return FloatField._DOUBLE_MAX
			max = float(struct.unpack('>d', b'\x7f\xef\xff\xff\xff\xff\xff\xff')[0])
			FloatField._DOUBLE_MAX = max
			return max

class StringField(Field):
	def __init__(self, field_type: StringType, endian: Endian = Endian.little, strip: bool = True) -> None:
		Field.__init__(self, field_type, endian)
		self.strip = strip

	def pack(self, value: str, encoding: str = 'utf-8') -> bytes:
		return struct.pack(self.format, value.encode(encoding))

	def unpack(self, data: bytes, offset: int = 0, encoding: str = 'utf-8') -> str:
		unpacked: bytes = struct.unpack_from(self.format, data, offset)[0]
		if self.strip:
			unpacked = unpacked.rstrip(b'\x00')
		return unpacked.decode(encoding)

	@property
	def min(self) -> int:
		return 0

	@property
	def max(self) -> int:
		return 255

l_s8 = IntField(t_s8, Endian.little)
l_u8 = IntField(t_u8, Endian.little)
l_s16 = IntField(t_s16, Endian.little)
l_u16 = IntField(t_u16, Endian.little)
l_s32 = IntField(t_s32, Endian.little)
l_u32 = IntField(t_u32, Endian.little)
l_s64 = IntField(t_s64, Endian.little)
l_u64 = IntField(t_u64, Endian.little)
l_float = FloatField(t_float, Endian.little)
l_double = FloatField(t_double, Endian.little)
l_char = StringField(t_str(1), Endian.little)
def l_pstr(count: int, strip: bool = True) -> StringField:
	return StringField(t_pstr(count), Endian.little, strip)
def l_str(count: int, strip: bool = True) -> StringField:
	return StringField(t_str(count), Endian.little, strip)

class ArrayField(Field):
	def __init__(self, field_type: Array, endian: Endian = Endian.little) -> None:
		Field.__init__(self, field_type, endian)

class IntArrayField(ArrayField):
	def __init__(self, field_type: IntArray, endian: Endian = Endian.little) -> None:
		ArrayField.__init__(self, field_type, endian)

	def pack(self, value: Sequence[int]) -> bytes:
		return struct.pack(self.format, *value)

	def unpack(self, data: bytes, offset: int = 0) -> list[int]:
		return list(struct.unpack_from(self.format, data, offset))

class FloatArrayField(ArrayField):
	def __init__(self, field_type: FloatArray, endian: Endian = Endian.little) -> None:
		ArrayField.__init__(self, field_type, endian)

	def pack(self, value: Sequence[float]) -> bytes:
		return struct.pack(self.format, *value)

	def unpack(self, data: bytes, offset: int = 0) -> list[float]:
		return list(struct.unpack_from(self.format, data, offset))

def l_as8(size: int) -> IntArrayField:
	return IntArrayField(t_as8(size))
def l_au8(size: int) -> IntArrayField:
	return IntArrayField(t_au8(size))
def l_as16(size: int) -> IntArrayField:
	return IntArrayField(t_as16(size))
def l_au16(size: int) -> IntArrayField:
	return IntArrayField(t_au16(size))
def l_as32(size: int) -> IntArrayField:
	return IntArrayField(t_as32(size))
def l_au32(size: int) -> IntArrayField:
	return IntArrayField(t_au32(size))
def l_as64(size: int) -> IntArrayField:
	return IntArrayField(t_as64(size))
def l_au64(size: int) -> IntArrayField:
	return IntArrayField(t_au64(size))
def l_afloat(size: int) -> FloatArrayField:
	return FloatArrayField(t_afloat(size))
def l_adouble(size: int) -> FloatArrayField:
	return FloatArrayField(t_adouble(size))

class Struct(object):
	_endian = Endian.little
	_fields: tuple[tuple[str, Type] | PadType, ...] = ()

	_struct: struct.Struct | None = None

	@classmethod
	def format(cls) -> str:
		format: str = cls._endian
		for field_def in cls._fields:
			ctype: Type
			if isinstance(field_def, tuple):
				ctype = field_def[1]
			else:
				ctype = field_def
			format += ctype.format
		return format

	@classmethod
	def build_struct(cls) -> None:
		if cls._struct is None:
			cls._struct = struct.Struct(cls.format())

	@classmethod
	def calcsize(cls) -> int:
		cls.build_struct()
		assert cls._struct is not None
		return cls._struct.size

	@property
	def size(self) -> int:
		return self.calcsize()

	def pack(self) -> bytes:
		self.build_struct()
		assert self._struct is not None
		values = []
		for field_def in self._fields:
			if not isinstance(field_def, tuple):
				continue
			name,type = field_def
			if isinstance(type, Array):
				values.extend(getattr(self, name))
			elif isinstance(type, StringType):
				string: str = getattr(self, name)
				values.append(string.encode('utf-8'))
			else:
				values.append(getattr(self, name))
		return self._struct.pack(*values)

	@classmethod
	def unpack(cls, data: bytes, offset: int = 0) -> Self:
		cls.build_struct()
		assert cls._struct is not None
		if len(data) < offset + cls._struct.size:
			raise PyMSError('Struct', 'Not enough data (expected %d, got %d)' % (cls._struct.size, len(data) - offset))
		values = cls._struct.unpack_from(data, offset)
		obj = cls()
		index = 0
		for field_def in cls._fields:
			if not isinstance(field_def, tuple):
				continue
			name,type = field_def
			if isinstance(type, Array):
				value = list(values[index:index+type.size])
				index += type.size
			else:
				value = values[index]
				index += 1
			setattr(obj, name, value)
		return obj

	@classmethod
	def unpack_array(cls, data: bytes, count: int, offset: int = 0) -> list[Self]:
		cls.build_struct()
		assert cls._struct is not None
		if len(data) < offset + cls._struct.size * count:
			raise PyMSError('Struct', 'Not enough data (expected %d, got %d)' % (cls._struct.size * count, len(data) - offset))
		array = []
		for _ in range(count):
			array.append(cls.unpack(data, offset))
			offset += cls._struct.size
		return array

	@classmethod
	def unpack_file(cls, file_handle: BinaryIO) -> Self:
		cls.build_struct()
		assert cls._struct is not None
		try:
			data = file_handle.read(cls._struct.size)
		except:
			raise PyMSError('Struct', 'Not enough data (expected %d)' % (cls._struct.size))
		return cls.unpack(data)

	def __repr__(self) -> str:
		self.build_struct()
		assert self._struct is not None
		result = """<%s.%s struct = '%s'
""" % (self.__class__.__module__, self.__class__.__name__, self._struct.format)
		for field_def in self._fields:
			if not isinstance(field_def, tuple):
				continue
			name = field_def[0]
			value = getattr(self, name)
			if isinstance(value, str):
				value = value.encode('unicode_escape')
			result += "\t%s = %s\n" % (name, value)
		return result + ">"
