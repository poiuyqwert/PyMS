
from .PyMSError import PyMSError

import struct

class Endian:
	native = '@'
	native_standard = '='
	little = '<'
	big = '>'
	network = '!'

class Type:
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
