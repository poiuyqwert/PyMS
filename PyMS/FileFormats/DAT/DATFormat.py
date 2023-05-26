
import struct

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Any, Type

class DATFormat(object):
	def __init__(self, format): # type: (dict) -> None
		self.entries = format["entries"] # type: int
		self.expanded_min_entries = format.get("expanded_min_entries") # type: int | None
		self.expanded_max_entries = format.get("expanded_max_entries") # type: int | None
		self.expanded_entries_multiple = format.get("expanded_entries_multiple") # type: int | None
		self.expanded_entries_reserved = format.get("expanded_entries_reserved") # type: list[int] | None
		self.properties = list(DATProperty(prop) for prop in format["properties"])

	# Return a tuple `(<entry_count>, <is_expanded>)` if valid size, otherwise None
	def check_file_size(self, size): # type: (int) -> (tuple[int, bool] | None)
		if size == self.file_size():
			return (self.entries, False)
		expanded_entry_size = self.expanded_entry_size()
		if size % expanded_entry_size == 0:
			return (int(size / expanded_entry_size), True)
		return None

	def expanded_entry_size(self): # type: () -> int
		size = 0
		for prop in self.properties:
			size += prop.size(True)
		return size

	def file_size(self, expanded_entry_count=None): # type: (int | None) -> int
		size = 0
		for prop in self.properties:
			size += prop.total_size(expanded_entry_count or self.entries, expanded_entry_count != None)
		return size

	def get_property(self, name): # type: (str) -> (DATProperty | None)
		for prop in self.properties:
			if prop.name == name:
				return prop
		return None

class DATType(object):
	STRUCT = None # type: struct.Struct

	@classmethod
	def size(self): # type: () -> int
		return self.STRUCT.size

	def unpack_data(self, data, offset): # type: (bytes, int) -> Any
		return self.STRUCT.unpack(data[offset:offset+self.size()])

	def load_data(self, data, offset): # type: (bytes, int) -> None
		pass

	def value(self): # type: () -> Any
		return self

	def pack_data(self, values): # type: (tuple) -> bytes
		return self.STRUCT.pack(*values)

	def save_data(self): # type: () -> bytes
		return bytes()

class DATTypeScalar(DATType):
	def __init__(self, value=0): # type: (int) -> None
		self._value = value

	def load_data(self, data, offset): # type: (bytes, int) -> None
		self._value = self.unpack_data(data, offset)[0]

	def value(self): # type: () -> int
		return self._value

	def save_data(self): # type: () -> bytes
		return self.pack_data((self._value,))

class DATTypeByte(DATTypeScalar):
	STRUCT = struct.Struct('<B')

class DATTypeShort(DATTypeScalar):
	STRUCT = struct.Struct('<H')

class DATTypeLong(DATTypeScalar):
	STRUCT = struct.Struct('<L')

class DATTypeSize(DATType):
	STRUCT = struct.Struct('<2H')

	def __init__(self):
		self.width = 0
		self.height = 0

	def load_data(self, data, offset): # type: (bytes, int) -> None
		self.width, self.height = self.unpack_data(data, offset)

	def save_data(self): # type: () -> bytes
		return self.pack_data((self.width, self.height))

class DATTypePosition(DATType):
	STRUCT = struct.Struct('<2H')

	def __init__(self):
		self.x = 0
		self.y = 0

	def load_data(self, data, offset): # type: (bytes, int) -> None
		self.x, self.y = self.unpack_data(data, offset)

	def save_data(self): # type: () -> bytes
		return self.pack_data((self.x, self.y))

class DATTypeExtents(DATType):
	STRUCT = struct.Struct('<4H')

	def __init__(self):
		self.left = 0
		self.up = 0
		self.right = 0
		self.down = 0

	def load_data(self, data, offset): # type: (bytes, int) -> None
		self.left, self.up, self.right, self.down = self.unpack_data(data, offset)

	def save_data(self): # type: () -> bytes
		return self.pack_data((self.left, self.up, self.right, self.down))

class DATTypeHitPoints(DATType):
	STRUCT = struct.Struct('<L')

	def __init__(self):
		self.whole = 0
		self.fraction = 0

	def load_data(self, data, offset): # type: (bytes, int) -> None
		value = self.unpack_data(data, offset)[0]
		self.whole = value >> 8
		self.fraction = value & 0xFF

	def save_data(self): # type: () -> bytes
		value = (self.whole << 8) | self.fraction
		return self.pack_data((value,))

class DATTypeSupply(DATType):
	STRUCT = struct.Struct('<B')

	def __init__(self):
		self.whole = 0
		self.half = False

	def load_data(self, data, offset): # type: (bytes, int) -> None
		value = self.unpack_data(data, offset)[0]
		self.whole = value >> 1
		self.half = (value & 1) == 1

	def save_data(self): # type: () -> bytes
		value = (self.whole << 1) | (1 if self.half else 0)
		return self.pack_data((value,))

class DATProperty(object):
	DAT_TYPES = {
		'byte': DATTypeByte,
		'short': DATTypeShort,
		'long': DATTypeLong,

		'size': DATTypeSize,
		'position': DATTypePosition,
		'extents': DATTypeExtents,
		'hit_points': DATTypeHitPoints,
		'supply': DATTypeSupply,
	}
	def __init__(self, format): # type: (dict) -> None
		self.name = format["name"] # type: str
		self._dat_type = self.DAT_TYPES[format["type"]] # type: Type[DATType]
		if "expanded_type" in format:
			self._expanded_type = self.DAT_TYPES[format["expanded_type"]] # type: Type[DATType]
		else:
			self._expanded_type = self._dat_type
		self.entry_offset = format.get("entry_offset") # type: int | None
		self._entry_count = format.get("entry_count") # type: int | None

	def dat_type(self, is_expanded): # type: (bool) -> Type[DATType]
		if is_expanded:
			return self._expanded_type
		return self._dat_type

	def entry_count(self, total_entry_count, is_expanded): # type: (int, bool) -> int
		if not is_expanded and self._entry_count:
			return self._entry_count
		return total_entry_count

	def size(self, is_expanded): # type: (bool) -> int
		return self.dat_type(is_expanded).size()

	def total_size(self, total_entry_count, is_expanded): # type: (int, bool) -> int
		return self.entry_count(total_entry_count, is_expanded) * self.size(is_expanded)

	def load_data(self, data, offset, total_entry_count, is_expanded): # type: (bytes, int, int, bool) -> tuple[int, tuple]
		total_size = self.total_size(total_entry_count, is_expanded)
		entry_count = self.entry_count(total_entry_count, is_expanded)
		prop_data = []
		for _ in range(entry_count):
			dat_type = self.dat_type(is_expanded)()
			dat_type.load_data(data, offset)
			# DATTypeScalar will return the raw scalar value, other DATTypes will return themselves
			prop_data.append(dat_type.value())
			size = dat_type.size()
			offset += size

		# If its not an expanded DAT, we pad the data with `None` based on the `entry_offset` and `entry_count`
		if not is_expanded:
			if self.entry_offset:
				prop_data = [None] * self.entry_offset + prop_data
			if self._entry_count:
				prop_data += [None] * (total_entry_count - (self.entry_offset or 0) - self._entry_count)
		
		return (total_size, tuple(prop_data))

	def save_data(self, values, is_expanded): # type: (tuple, bool) -> bytes
		dat_type = self.dat_type(is_expanded)

		# If its not an expanded DAT, we must strip padded data based on the `entry_offset` and `entry_count`
		if not is_expanded:
			if self.entry_offset:
				values = values[self.entry_offset:]
			if self._entry_count:
				values = values[:self._entry_count]

		# If DATType is a scalar we need to convert the raw scalar back to its DATType for saving
		if issubclass(dat_type, DATTypeScalar):
			values = tuple(dat_type(value) for value in values)
		return b''.join(value.save_data() for value in values)

	# Whether this property is on an entry with `id` (non-expanded, as expanded dats have all entries)
	def is_on_entry(self, id): # type: (int) -> bool
		if not self.entry_offset or not self._entry_count:
			return True
		return (id >= self.entry_offset and id < (self.entry_offset + self._entry_count))
