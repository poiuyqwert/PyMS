
from __future__ import annotations

from .PyMSError import PyMSError

import struct
from enum import StrEnum, Enum

from typing import Self, BinaryIO, Literal, Sequence, Any, Protocol, runtime_checkable, TypeVar

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

@runtime_checkable
class Processed(Protocol):
	def prepare_to_pack(self, value: Any) -> Any: ...
	def finalize_unpack(self, value: Any) -> Any: ...

class Type:
	def __init__(self, format: Format) -> None:
		self._format = format

	@property
	def is_signed(self) -> bool:
		return self._format.is_signed

	@property
	def format(self) -> str:
		return self._format.value

	def __eq__(self, other) -> bool:
		if not isinstance(other, Type):
			return False
		return other._format == self._format

class PadType(Type):
	def __init__(self, format: Literal[Format.pad], length: int):
		Type.__init__(self, format)
		self.length = length

	@property
	def format(self) -> str:
		if self.length == 1:
			return self._format.value
		return f'{self.length}{self._format}'

	def __eq__(self, other) -> bool:
		if not isinstance(other, PadType):
			return False
		if other._format != self._format:
			return False
		if other.length != self.length:
			return False
		return True

class IntType(Type):
	def __init__(self, format: Literal[Format.s8, Format.u8, Format.s16, Format.u16, Format.s32, Format.u32, Format.s64, Format.u64]):
		Type.__init__(self, format)

class BoolType(Type, Processed):
	def __init__(self, format: Literal[Format.s8, Format.u8, Format.s16, Format.u16, Format.s32, Format.u32, Format.s64, Format.u64]):
		Type.__init__(self, format)

	def prepare_to_pack(self, value: bool) -> int:
		return int(value)

	def finalize_unpack(self, value: int) -> bool:
		return bool(value)

class FloatType(Type):
	def __init__(self, format: Literal[Format.float, Format.double]):
		Type.__init__(self, format)

class Strip(Enum):
	none = 0
	right = 1
	from_first = 2
class StringType(Type, Processed):
	def __init__(self, format: Literal[Format.char, Format.pstr, Format.str], length: int, strip: Strip = Strip.from_first, encoding: str = 'utf-8'):
		Type.__init__(self, format)
		self.length = length
		self.strip = strip
		self.encoding = encoding

	@property
	def format(self) -> str:
		if self._format == Format.char and self.length == 1:
			return self._format.value
		return f'{self.length}{self._format}'

	def prepare_to_pack(self, value: str) -> bytes:
		return value.encode(self.encoding)

	def finalize_unpack(self, value: bytes) -> str:
		match self.strip:
			case Strip.none:
				pass
			case Strip.right:
				value = value.rstrip(b'\x00')
			case Strip.from_first:
				try:
					index = value.index(b'\x00')
				except:
					pass
				else:
					value = value[:index]
		return value.decode(self.encoding)

	def __eq__(self, other) -> bool:
		if not isinstance(other, StringType):
			return False
		if other._format != self._format:
			return False
		if other.length != self.length:
			return False
		if other.strip != self.strip:
			return False
		if other.encoding != self.encoding:
			return False
		return True

def t_pad(length: int = 1) -> PadType:
	return PadType(Format.pad, length)
t_s8 = IntType(Format.s8)
t_u8 = IntType(Format.u8)
t_b8 = BoolType(Format.u8)
t_s16 = IntType(Format.s16)
t_u16 = IntType(Format.u16)
t_s32 = IntType(Format.s32)
t_u32 = IntType(Format.u32)
t_s64 = IntType(Format.s64)
t_u64 = IntType(Format.u64)
t_float = FloatType(Format.float)
t_double = FloatType(Format.double)
t_char = StringType(Format.char, 1)
def t_pstr(length: int, strip: Strip = Strip.from_first, encoding: str = 'utf-8') -> StringType:
	return StringType(Format.pstr, length, strip, encoding)
def t_str(length: int, strip: Strip = Strip.from_first, encoding: str = 'utf-8') -> StringType:
	return StringType(Format.str, length, strip, encoding)

class Array(Type):
	def __init__(self, format: Format, length: int):
		Type.__init__(self, format)
		self.length = length

	@property
	def format(self) -> str:
		return f'{self.length}{self._format}'

class IntArray(Array):
	def __init__(self, format: Literal[Format.pad, Format.s8, Format.u8, Format.s16, Format.u16, Format.s32, Format.u32, Format.s64, Format.u64], length: int):
		Array.__init__(self, format, length)

class BoolArray(IntArray, Processed):
	def prepare_to_pack(self, value: list[bool]) -> list[int]:
		return [int(b) for b in value]

	def finalize_unpack(self, value: list[int]) -> list[bool]:
		return [bool(b) for b in value]

class FloatArray(Array):
	def __init__(self, format: Literal[Format.float, Format.double], length: int):
		Array.__init__(self, format, length)

def t_as8(length: int) -> IntArray:
	return IntArray(Format.s8, length)
def t_au8(length: int) -> IntArray:
	return IntArray(Format.u8, length)
def t_ab8(length: int) -> BoolArray:
	return BoolArray(Format.u8, length)
def t_as16(length: int) -> IntArray:
	return IntArray(Format.s16, length)
def t_au16(length: int) -> IntArray:
	return IntArray(Format.u16, length)
def t_as32(length: int) -> IntArray:
	return IntArray(Format.s32, length)
def t_au32(length: int) -> IntArray:
	return IntArray(Format.u32, length)
def t_as64(length: int) -> IntArray:
	return IntArray(Format.s64, length)
def t_au64(length: int) -> IntArray:
	return IntArray(Format.u64, length)
def t_afloat(length: int) -> FloatArray:
	return FloatArray(Format.float, length)
def t_adouble(length: int) -> FloatArray:
	return FloatArray(Format.double, length)

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

	def pack(self, value: Any) -> bytes:
		return struct.pack(self.format, value)

	def unpack(self, data: bytes, offset: int = 0) -> Any:
		return struct.unpack_from(self.format, data, offset)[0]

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

class BoolField(Field):
	def __init__(self, field_type: BoolType, endian: Endian = Endian.little) -> None:
		Field.__init__(self, field_type, endian)

	def pack(self, value: int) -> bytes:
		return struct.pack(self.format, value)

	def unpack(self, data: bytes, offset: int = 0) -> bool:
		return bool(struct.unpack_from(self.format, data, offset)[0])

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
	def __init__(self, field_type: StringType, endian: Endian = Endian.little) -> None:
		Field.__init__(self, field_type, endian)

	def pack(self, value: str) -> bytes:
		assert isinstance(self.field_type, Processed)
		return struct.pack(self.format, self.field_type.prepare_to_pack(value))

	def unpack(self, data: bytes, offset: int = 0) -> str:
		assert isinstance(self.field_type, Processed)
		unpacked: bytes = struct.unpack_from(self.format, data, offset)[0]
		return self.field_type.finalize_unpack(unpacked)

	@property
	def min(self) -> int:
		return 0

	@property
	def max(self) -> int:
		return 255

l_s8 = IntField(t_s8, Endian.little)
l_u8 = IntField(t_u8, Endian.little)
l_b8 = BoolField(t_b8, Endian.little)
l_s16 = IntField(t_s16, Endian.little)
l_u16 = IntField(t_u16, Endian.little)
l_s32 = IntField(t_s32, Endian.little)
l_u32 = IntField(t_u32, Endian.little)
l_s64 = IntField(t_s64, Endian.little)
l_u64 = IntField(t_u64, Endian.little)
l_float = FloatField(t_float, Endian.little)
l_double = FloatField(t_double, Endian.little)
l_char = StringField(t_char, Endian.little)
def l_pstr(length: int, strip: Strip = Strip.from_first, encoding: str = 'utf-8') -> StringField:
	return StringField(t_pstr(length, strip, encoding), Endian.little)
def l_str(length: int, strip: Strip = Strip.from_first, encoding: str = 'utf-8') -> StringField:
	return StringField(t_str(length, strip, encoding), Endian.little)

class ArrayField(Field):
	def __init__(self, field_type: Array, endian: Endian = Endian.little) -> None:
		Field.__init__(self, field_type, endian)

class IntArrayField(ArrayField):
	def __init__(self, field_type: IntArray, endian: Endian = Endian.little) -> None:
		ArrayField.__init__(self, field_type, endian)

	def pack(self, value: Sequence[int]) -> bytes:
		assert isinstance(self.field_type, Array)
		if len(value) != self.field_type.length:
			raise PyMSError('Pack', f"Array of '{self.field_type.format}' is length {self.field_type.length}, but got {len(value)}")
		return struct.pack(self.format, *value)

	def unpack(self, data: bytes, offset: int = 0) -> list[int]:
		return list(struct.unpack_from(self.format, data, offset))

class BoolArrayField(ArrayField):
	def __init__(self, field_type: IntArray, endian: Endian = Endian.little) -> None:
		ArrayField.__init__(self, field_type, endian)

	def pack(self, value: Sequence[int]) -> bytes:
		assert isinstance(self.field_type, Array)
		if len(value) != self.field_type.length:
			raise PyMSError('Pack', f"Array of '{self.field_type.format}' is length {self.field_type.length}, but got {len(value)}")
		return struct.pack(self.format, *value)

	def unpack(self, data: bytes, offset: int = 0) -> list[bool]:
		return list(struct.unpack_from(self.format, data, offset))

class FloatArrayField(ArrayField):
	def __init__(self, field_type: FloatArray, endian: Endian = Endian.little) -> None:
		ArrayField.__init__(self, field_type, endian)

	def pack(self, value: Sequence[float]) -> bytes:
		assert isinstance(self.field_type, Array)
		if len(value) != self.field_type.length:
			raise PyMSError('Pack', f"Array of '{self.field_type.format}' is length {self.field_type.length}, but got {len(value)}")
		return struct.pack(self.format, *value)

	def unpack(self, data: bytes, offset: int = 0) -> list[float]:
		return list(struct.unpack_from(self.format, data, offset))

AnyField = IntField | FloatField | StringField

def l_as8(length: int) -> IntArrayField:
	return IntArrayField(t_as8(length))
def l_au8(length: int) -> IntArrayField:
	return IntArrayField(t_au8(length))
def l_ab8(length: int) -> BoolArrayField:
	return BoolArrayField(t_ab8(length))
def l_as16(length: int) -> IntArrayField:
	return IntArrayField(t_as16(length))
def l_au16(length: int) -> IntArrayField:
	return IntArrayField(t_au16(length))
def l_as32(length: int) -> IntArrayField:
	return IntArrayField(t_as32(length))
def l_au32(length: int) -> IntArrayField:
	return IntArrayField(t_au32(length))
def l_as64(length: int) -> IntArrayField:
	return IntArrayField(t_as64(length))
def l_au64(length: int) -> IntArrayField:
	return IntArrayField(t_au64(length))
def l_afloat(length: int) -> FloatArrayField:
	return FloatArrayField(t_afloat(length))
def l_adouble(length: int) -> FloatArrayField:
	return FloatArrayField(t_adouble(length))

class MixedInts:
	_struct: struct.Struct | None = None

	def __init__(self, types: Sequence[IntType | IntArray | PadType]):
		self.types = types

	def format(self, endian: Endian) -> str:
		format = endian.value
		for type in self.types:
			format += type.format
		return format

	def size(self, endian: Endian) -> int:
		return struct.calcsize(self.format(endian))

	def pack(self, value: Sequence[int], endian: Endian) -> bytes:
		return struct.pack(self.format(endian), *value)

	def unpack(self, data: bytes, offset: int, endian: Endian) -> list[int]:
		return list(struct.unpack_from(self.format(endian), data, offset))

	def __eq__(self, other) -> bool:
		if not isinstance(other, MixedInts):
			return False
		if other.types != self.types:
			return False
		return True

class Struct:
	Format = tuple['str | type[Struct] | StructArray | MixedInts', ...]
	Processors = tuple['struct.Struct | type[Struct] | StructArray | MixedInts', ...]
	FieldInfo = tuple[str, 'Type | type[Struct] | StructArray | MixedInts']
	PaddedFieldInfo = FieldInfo | PadType

	_endian = Endian.little
	_fields: tuple[PaddedFieldInfo, ...]

	_processors: Processors | None = None
	_size: int | None = None

	@classmethod
	def format(cls) -> Struct.Format:
		format: list[str | type[Struct] | StructArray | MixedInts] = []
		format_str = ''
		for field_def in cls._fields:
			ctype: Type
			if isinstance(field_def, tuple):
				if isinstance(field_def[1], Type):
					ctype = field_def[1]
				else:
					if format_str:
						format.append(format_str)
						format_str = ''
					format.append(field_def[1])
					continue
			else:
				ctype = field_def
			if not format_str:
				format_str += cls._endian
			format_str += ctype.format
		if format_str:
			format.append(format_str)
		return tuple(format)

	@classmethod
	def get_processors(cls) -> Struct.Processors:
		if cls._processors is not None:
			return cls._processors
		processors: list[struct.Struct | type[Struct] | StructArray | MixedInts] = []
		for format in cls.format():
			if isinstance(format, str):
				processors.append(struct.Struct(format))
			else:
				processors.append(format)
		_processors = tuple(processors)
		cls._processors = _processors
		return _processors

	@classmethod
	def calcsize(cls) -> int:
		if cls._size is not None:
			return cls._size
		processors = cls.get_processors()
		size = 0
		for processor in processors:
			if isinstance(processor, struct.Struct):
				size += processor.size
			elif isinstance(processor, StructArray):
				size += processor.size
			elif isinstance(processor, MixedInts):
				size += processor.size(cls._endian)
			else:
				size += processor.calcsize()
		cls._size = size
		return size

	@property
	def size(self) -> int:
		return self.calcsize()

	def pack(self) -> bytes:
		self.pre_pack()
		result = b''
		processors = self.get_processors()
		processor_index = 0
		values = []
		for field_def in self._fields:
			if not isinstance(field_def, tuple):
				continue
			name,type = field_def
			if isinstance(type, Type):
				if isinstance(type, Array):
					values.extend(getattr(self, name))
				else:
					value = getattr(self, name)
					if isinstance(type, Processed):
						value = type.prepare_to_pack(value)
					values.append(value)
			else:
				if values:
					processor = processors[processor_index]
					processor_index += 1
					assert isinstance(processor, struct.Struct)
					result += processor.pack(*values)
					values.clear()
				value = getattr(self, name)
				if isinstance(type, StructArray):
					assert isinstance(value, list)
					result += type.pack(value)
				elif isinstance(type, MixedInts):
					assert isinstance(value, list)
					result += type.pack(value, self._endian)
				else:
					assert isinstance(value, Struct)
					result += value.pack()
				processor_index += 1
		if values:
			processor = processors[processor_index]
			assert isinstance(processor, struct.Struct)
			result += processor.pack(*values)
		self.post_pack()
		return result

	@classmethod
	def unpack(cls, data: bytes, offset: int = 0) -> Self:
		processors = cls.get_processors()
		if len(data) < offset + cls.calcsize():
			raise PyMSError('Struct', 'Not enough data (expected %d, got %d)' % (cls.calcsize(), len(data) - offset))
		obj = cls()
		field_index = 0
		def next_field() -> Struct.FieldInfo:
			nonlocal field_index
			field_info = cls._fields[field_index]
			field_index += 1
			while isinstance(field_info, PadType):
				field_info = cls._fields[field_index]
				field_index += 1
			return field_info
		for processor in processors:
			value: Any
			if isinstance(processor, struct.Struct):
				values = processor.unpack_from(data, offset)
				offset += processor.size
				value_index = 0
				while value_index < len(values):
					name,type = next_field()
					assert isinstance(type, Type)
					if isinstance(type, Array):
						value = list(values[value_index:value_index+type.length])
						value_index += type.length
					else:
						value = values[value_index]
						if isinstance(type, Processed):
							value = type.finalize_unpack(value)
						value_index += 1
					setattr(obj, name, value)
			else:
				if isinstance(processor, MixedInts):
					value = processor.unpack(data, offset, cls._endian)
					offset += processor.size(cls._endian)
				else:
					value = processor.unpack(data, offset)
					if isinstance(processor, StructArray):
						offset += processor.size
					else:
						offset += processor.calcsize()
				name,_ = next_field()
				setattr(obj, name, value)
		obj.post_unpack()
		return obj

	@classmethod
	def unpack_array(cls, data: bytes, count: int, offset: int = 0) -> list[Self]:
		if len(data) < offset + cls.calcsize() * count:
			raise PyMSError('Struct', 'Not enough data (expected %d, got %d)' % (cls.calcsize() * count, len(data) - offset))
		array = []
		for _ in range(count):
			array.append(cls.unpack(data, offset))
			offset += cls.calcsize()
		return array

	@classmethod
	def unpack_file(cls, file_handle: BinaryIO) -> Self:
		try:
			data = file_handle.read(cls.calcsize())
		except:
			raise PyMSError('Struct', 'Not enough data (expected %d)' % (cls.calcsize()))
		return cls.unpack(data)

	def __repr__(self) -> str:
		format = ''
		for format_piece in self.format():
			if format:
				format += ' '
			if isinstance(format_piece, str):
				format += format_piece
			elif isinstance(format_piece, StructArray):
				format += f'{format_piece.struct_type.__name__}[]'
			elif isinstance(format_piece, MixedInts):
				format += format_piece.format(self._endian)
			else:
				format += format_piece.__name__
		result = """<%s.%s struct = '%s'
""" % (self.__class__.__module__, self.__class__.__name__, format)
		for field_def in self._fields:
			if not isinstance(field_def, tuple):
				continue
			name = field_def[0]
			value = getattr(self, name)
			if isinstance(value, str):
				value = value.encode('unicode_escape')
			result += "\t%s = %s\n" % (name, value)
		return result + ">"

	def post_unpack(self) -> None:
		pass

	def pre_pack(self) -> None:
		pass

	def post_pack(self) -> None:
		pass

S = TypeVar('S', bound=Struct)
class StructArray:
	def __init__(self, struct_type: type[S], count: int) -> None:
		self.struct_type = struct_type
		self.count = count

	@property
	def size(self) -> int:
		return self.struct_type.calcsize() * self.count

	def pack(self, value: Sequence[S]) -> bytes:
		if len(value) != self.count:
			raise PyMSError('Pack', f"Array of '{self.struct_type.__name__}' is length {self.count}, but got {len(value)}")
		result = b''
		for struct in value:
			result += struct.pack()
		return result

	def unpack(self, data: bytes, offset: int = 0) -> list[S]:
		return self.struct_type.unpack_array(data, self.count, offset)

	def __eq__(self, other) -> bool:
		if not isinstance(other, StructArray):
			return False
		if other.struct_type != self.struct_type:
			return False
		if other.count != self.count:
			return False
		return True
