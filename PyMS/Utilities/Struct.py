
from .PyMSError import PyMSError

import struct, sys

class Endian:
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
	def format(char, count):
		if count == 1:
			return char
		return '%d%s' % (count, char)

	@staticmethod
	def pad(count=1):
		return Type.format('x', count)

	@staticmethod
	def s8(count=1):
		return Type.format('b', count)

	@staticmethod
	def u8(count=1):
		return Type.format('B', count)

	@staticmethod
	def s16(count=1):
		return Type.format('h', count)

	@staticmethod
	def u16(count=1):
		return Type.format('H', count)

	@staticmethod
	def s32(count=1):
		return Type.format('l', count)

	@staticmethod
	def u32(count=1):
		return Type.format('L', count)

	@staticmethod
	def s64(count=1):
		return Type.format('q', count)

	@staticmethod
	def u64(count=1):
		return Type.format('Q', count)

	@staticmethod
	def float(count=1):
		return Type.format('f', count)

	@staticmethod
	def double(count=1):
		return Type.format('d', count)

	@staticmethod
	def char(count=1):
		return Type.format('c', count)

	@staticmethod
	def str(count):
		return Type.format('s', count)

	@staticmethod
	def str_pascal(count):
		return Type.format('p', count) 

	@staticmethod
	def size(type):
		return struct.calcsize(type)

	@staticmethod
	def numeric_limits(type): # type: (str) -> tuple[int, int]
		if type == 'f':
			if Type.FLOAT_MIN == None:
				Type.FLOAT_MIN = struct.unpack('>f', b'\xff\x7f\xff\xff')
				Type.FLOAT_MAX = struct.unpack('>f', b'\x7f\x7f\xff\xff')
			return (Type.FLOAT_MIN, Type.FLOAT_MAX)
		elif type == 'd':
			if Type.DOUBLE_MIN == None:
				Type.DOUBLE_MAX = struct.unpack('>d', b'\x7f\xef\xff\xff\xff\xff\xff\xff')
				Type.DOUBLE_MIN = struct.unpack('>d', b'\xff\xef\xff\xff\xff\xff\xff\xff')
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
		size = struct.calcsize(type)
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
	_fields = () # ( ('name', 'struct c type'), ... )

	_struct = None 

	@classmethod
	def build_struct(cls):
		if cls._struct == None:
			cls._struct = struct.Struct(cls._endian + ''.join(ctype for _,ctype in cls._fields))

	@classmethod
	def size(cls):
		cls.build_struct()
		return cls._struct.size

	@classmethod
	def unpack(cls, data, offset=0):
		cls.build_struct()
		if len(data) < offset + cls._struct.size:
			raise PyMSError('Struct', 'Not enough data (expected %d, got %d)' % (cls._struct.size, len(data) - offset))
		values = cls._struct.unpack(data[offset:offset + cls._struct.size])
		obj = cls()
		for (name,_),value in zip(cls._fields, values):
			setattr(obj, name, value)
		return obj

	@classmethod
	def unpack_array(cls, data, count, offset=0):
		cls.build_struct()
		if len(data) < offset + cls._struct.size * count:
			raise PyMSError('Struct', 'Not enough data (expected %d, got %d)' % (cls._struct.size * count, len(data) - offset))
		array = []
		for _ in range(count):
			array.append(cls.unpack(data, offset))
			offset += cls._struct.size
		return array

	@classmethod
	def unpack_file(cls, file_handle):
		cls.build_struct()
		try:
			data = file_handle.read(cls._struct.size)
		except:
			raise PyMSError('Struct', 'Not enough data (expected %d)' % (cls._struct.size))
		return cls.unpack(data)

	def __repr__(self):
		result = """<%s.%s struct = '%s'
""" % (self.__class__.__module__, self.__class__.__name__, self._struct.format)
		for (name, _) in self._fields:
			value = getattr(self, name)
			if isinstance(value, str):
				value = value.encode('string_escape')
			result += "\t%s = %s\n" % (name, value)
		return result + ">"
