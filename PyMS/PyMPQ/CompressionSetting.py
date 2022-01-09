
from ..FileFormats.MPQ.SFmpq import MAFA_COMPRESS_STANDARD, MAFA_COMPRESS_DEFLATE, MAFA_COMPRESS_WAVE, Z_BEST_SPEED, Z_DEFAULT_COMPRESSION, Z_NO_COMPRESSION, Z_BEST_COMPRESSION, MAWA_QUALITY_LOW, MAWA_QUALITY_MEDIUM, MAWA_QUALITY_HIGH

class CompressionType(object):
	def __init__(self, type):
		self.type = type

	def name(self):
		if self == CompressionType.NoCompression:
			return 'None'
		elif self == CompressionType.Standard:
			return 'Standard'
		elif self == CompressionType.Deflate:
			return 'Deflate'
		elif self == CompressionType.Audio:
			return 'Audio'
		elif self == CompressionType.Auto:
			return 'Auto'

	def mafa_type(self):
		if self == CompressionType.Standard:
			return MAFA_COMPRESS_STANDARD
		elif self == CompressionType.Deflate:
			return MAFA_COMPRESS_DEFLATE
		elif self == CompressionType.Audio:
			return MAFA_COMPRESS_WAVE
		else:
			return 0

	def level_count(self):
		return len(self.mafa_levels())

	def mafa_levels(self):
		if self == CompressionType.Deflate:
			return tuple(range(min(Z_DEFAULT_COMPRESSION, Z_NO_COMPRESSION, Z_BEST_COMPRESSION), max(Z_DEFAULT_COMPRESSION, Z_NO_COMPRESSION, Z_BEST_COMPRESSION)+1))
		elif self == CompressionType.Audio:
			return (MAWA_QUALITY_LOW, MAWA_QUALITY_MEDIUM, MAWA_QUALITY_HIGH)
		else:
			return ()

	def setting(self, level=0):
		return CompressionSetting(self, max(0, min(level, self.level_count()-1)))

	def __eq__(self, other):
		if not isinstance(other, CompressionType):
			return False
		return self.type == other.type

	def __str__(self):
		return self.type

CompressionType.NoCompression = CompressionType('none')
CompressionType.Standard = CompressionType('standard')
CompressionType.Deflate = CompressionType('deflate')
CompressionType.Audio = CompressionType('audio')
CompressionType.Auto = CompressionType('auto')

class CompressionSetting(object):
	def __init__(self, type, level):
		self.type = type
		self.level = level

	def mafa_level(self):
		mafa_levels = self.type.mafa_levels()
		if not mafa_levels:
			return 0
		return mafa_levels[self.level]

	def level_name(self):
		mafa_level = self.mafa_level()
		if self == CompressionType.Deflate:
			name = '%d' % mafa_level
			if mafa_level == Z_DEFAULT_COMPRESSION:
				name = 'Default'
			elif mafa_level == Z_NO_COMPRESSION:
				name += ' (None)'
			elif mafa_level == Z_BEST_SPEED:
				name += ' (Best Speed)'
			elif mafa_level == Z_BEST_COMPRESSION:
				name += ' (Best Compression)'
			return name
		elif self == CompressionType.Audio:
			if mafa_level == MAWA_QUALITY_LOW:
				return 'Lowest (Best Quality)'
			elif mafa_level == MAWA_QUALITY_MEDIUM:
				return 'Medium'
			elif mafa_level == MAWA_QUALITY_HIGH:
				return 'Highest (Least Space)'
		else:
			return ''

	@staticmethod
	def parse_value(menu_value):
		type = menu_value
		level = 0
		if ':' in menu_value:
			type,level = menu_value.split(':')
			type = CompressionType(type)
			level = max(0, min(int(level), type.level_count()-1))
		else:
			type = CompressionType(type)
		return type.setting(level)

	def __eq__(self, other):
		if isinstance(other, CompressionSetting):
			return self.type == other.type and self.level == other.level
		elif isinstance(other, CompressionType):
			return self.type == other
		else:
			return False

	def __str__(self):
		if self.type.level_count() > 0:
			return '%s:%d' % (self.type, self.level)
		else:
			return str(self.type)
