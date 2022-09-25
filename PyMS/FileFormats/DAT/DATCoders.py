
from .DATFormat import DATTypeSize, DATTypePosition, DATTypeExtents, DATTypeHitPoints, DATTypeSupply

from ...Utilities.PyMSError import PyMSError

import re
from collections import OrderedDict

class DATPropertyCoder(object):
	def encode(self, value):
		raise NotImplementedError(self.__class__.__name__ + '.encode()')

	def decode(self, value):
		raise NotImplementedError(self.__class__.__name__ + '.decode()')

class DATFlagsCoder(DATPropertyCoder):
	def __init__(self, bit_count, flag_mapping): # type: (int, dict[int, str]) -> DATFlagsCoder
		self.bit_count = bit_count
		self.flag_mapping = flag_mapping

	def encode(self, flags): # type: (int) -> OrderedDict[str, bool]
		values = OrderedDict()
		for bit in range(self.bit_count):
			flag = (1 << bit)
			flag_name = self.flag_mapping.get(flag)
			if not flag_name:
				flag_name = 'flag_0x%02X' % (flag)
			values[flag_name] = (flags & flag) == flag
		return values

	RE_FLAG = re.compile(r'^flag_0x([0-9a-fA-F]{2})$')
	def decode(self, values): # type: (dict[str, bool]) -> int
		flags = 0
		flag_list = self.flag_mapping.keys()
		name_list = self.flag_mapping.values()
		for (name, enabled) in values.items():
			if not enabled:
				continue
			if name in name_list:
				flag = flag_list[name_list.index(name)]
			else:
				match = DATFlagsCoder.RE_FLAG.match(name)
				if not match:
					raise PyMSError('Decode', 'Invalid flag name %s' % name)
				flag = int(match.group(1), 16)
			flags |= flag
		return flags

class DATSizeCoder(DATPropertyCoder):
	def encode(self, size): # type: (DATTypeSize) -> OrderedDict[str, int]
		values = OrderedDict()
		values['width'] = size.width
		values['height'] = size.height
		return values

	def decode(self, values): # type: (dict[str, int]) -> DATTypeSize
		if not 'width' in values:
			raise PyMSError('Decode', 'Size missing `width` value')
		if not 'height' in values:
			raise PyMSError('Decode', 'Size missing `height` value')
		size = DATTypeSize()
		size.width = values['width']
		size.height = values['height']
		return size

class DATPositionCoder(DATPropertyCoder):
	def encode(self, position): # type: (DATTypePosition) -> OrderedDict[str, int]
		values = OrderedDict()
		values['x'] = position.x
		values['y'] = position.y
		return values

	def decode(self, values): # type: (dict[str, int]) -> DATTypePosition
		if not 'x' in values:
			raise PyMSError('Decode', 'Position missing `x` value')
		if not 'y' in values:
			raise PyMSError('Decode', 'Position missing `y` value')
		position = DATTypePosition()
		position.x = values['x']
		position.y = values['y']
		return position

class DATExtentsCoder(DATPropertyCoder):
	def encode(self, extents): # type: (DATTypeExtents) -> OrderedDict[str, int]
		values = OrderedDict()
		values['left'] = extents.left
		values['up'] = extents.up
		values['right'] = extents.right
		values['down'] = extents.down
		return values

	def decode(self, values): # type: (dict[str, int]) -> DATTypeExtents
		if not 'left' in values:
			raise PyMSError('Decode', 'Extents missing `left` value')
		if not 'up' in values:
			raise PyMSError('Decode', 'Extents missing `up` value')
		if not 'right' in values:
			raise PyMSError('Decode', 'Extents missing `right` value')
		if not 'down' in values:
			raise PyMSError('Decode', 'Extents missing `down` value')
		extents = DATTypeExtents()
		extents.left = values['left']
		extents.up = values['up']
		extents.right = values['right']
		extents.down = values['down']
		return extents

class DATHitPointsCoder(DATPropertyCoder):
	def encode(self, hit_points): # type: (DATTypeHitPoints) -> OrderedDict[str, int]
		values = OrderedDict()
		values['whole'] = hit_points.whole
		values['fraction'] = hit_points.fraction
		return values

	def decode(self, values): # type: (dict[str, int]) -> DATTypeHitPoints
		if not 'whole' in values:
			raise PyMSError('Decode', 'Hit Points missing `whole` value')
		if not 'fraction' in values:
			raise PyMSError('Decode', 'Hit Points missing `fraction` value')
		hit_points = DATTypeHitPoints()
		hit_points.whole = values['whole']
		hit_points.fraction = values['fraction']
		return hit_points

class DATSupplyCoder(DATPropertyCoder):
	def encode(self, supply): # type: (DATTypeSupply) -> OrderedDict[str, Any]
		values = OrderedDict()
		values['whole'] = supply.whole
		values['half'] = True if supply.half else False
		return values

	def decode(self, values): # type: (dict[str, int]) -> DATTypeSupply
		if not 'whole' in values:
			raise PyMSError('Decode', 'Supply missing `whole` value')
		if not 'half' in values:
			raise PyMSError('Decode', 'Supply missing `half` value')
		supply = DATTypeSupply()
		supply.whole = values['whole']
		supply.half = True if values['half'] else False
		return supply

class DATBoolCoder(DATPropertyCoder):
	def encode(self, value): # type: (int) -> Any
		if value == 0:
			return False
		elif value == 1:
			return True
		return value

	def decode(self, value): # type: (Any) -> int
		if value == False:
			return 0
		elif value == True:
			return 1
		return value
