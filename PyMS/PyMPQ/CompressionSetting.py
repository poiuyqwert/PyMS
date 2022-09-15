
from ..FileFormats.MPQ.SFmpq import Z_BEST_SPEED, Z_DEFAULT_COMPRESSION, Z_NO_COMPRESSION, Z_BEST_COMPRESSION, MAWA_QUALITY_LOW, MAWA_QUALITY_MEDIUM, MAWA_QUALITY_HIGH
from ..FileFormats.MPQ.MPQ import MPQCompressionFlag

class CompressionOption(object):
	def __init__(self, type):
		self.type = type

	def name(self):
		if self == CompressionOption.NoCompression:
			return 'None'
		elif self == CompressionOption.Standard:
			return 'Standard'
		elif self == CompressionOption.Deflate:
			return 'Deflate'
		elif self == CompressionOption.Audio:
			return 'Audio'
		elif self == CompressionOption.Auto:
			return 'Auto'

	def compression_type(self):
		if self == CompressionOption.Standard:
			return MPQCompressionFlag.pkware
		elif self == CompressionOption.Deflate:
			return MPQCompressionFlag.zlib
		elif self == CompressionOption.Audio:
			return MPQCompressionFlag.huffman | MPQCompressionFlag.wav_mono
		else:
			return MPQCompressionFlag.none

	def level_count(self):
		return len(self.compression_levels())

	def compression_levels(self):
		if self == CompressionOption.Deflate:
			return tuple(range(min(Z_DEFAULT_COMPRESSION, Z_NO_COMPRESSION, Z_BEST_COMPRESSION), max(Z_DEFAULT_COMPRESSION, Z_NO_COMPRESSION, Z_BEST_COMPRESSION)+1))
		elif self == CompressionOption.Audio:
			return (MAWA_QUALITY_LOW, MAWA_QUALITY_MEDIUM, MAWA_QUALITY_HIGH)
		else:
			return ()

	def setting(self, level=0):
		return CompressionSetting(self, max(0, min(level, self.level_count()-1)))

	def __eq__(self, other):
		if not isinstance(other, CompressionOption):
			return False
		return self.type == other.type

	def __str__(self):
		return self.type

CompressionOption.NoCompression = CompressionOption('none')
CompressionOption.Standard = CompressionOption('standard')
CompressionOption.Deflate = CompressionOption('deflate')
CompressionOption.Audio = CompressionOption('audio')
CompressionOption.Auto = CompressionOption('auto')

class CompressionSetting(object):
	def __init__(self, type, level):
		self.type = type
		self.level = level

	def compression_level(self):
		compression_levels = self.type.compression_levels()
		if not compression_levels:
			return 0
		return compression_levels[self.level]

	def level_name(self):
		compression_level = self.compression_level()
		if self == CompressionOption.Deflate:
			name = '%d' % compression_level
			if compression_level == Z_DEFAULT_COMPRESSION:
				name = 'Default'
			elif compression_level == Z_NO_COMPRESSION:
				name += ' (None)'
			elif compression_level == Z_BEST_SPEED:
				name += ' (Best Speed)'
			elif compression_level == Z_BEST_COMPRESSION:
				name += ' (Best Compression)'
			return name
		elif self == CompressionOption.Audio:
			if compression_level == MAWA_QUALITY_LOW:
				return 'Lowest (Best Quality)'
			elif compression_level == MAWA_QUALITY_MEDIUM:
				return 'Medium'
			elif compression_level == MAWA_QUALITY_HIGH:
				return 'Highest (Least Space)'
		else:
			return ''

	@staticmethod
	def parse_value(menu_value):
		type = menu_value
		level = 0
		if ':' in menu_value:
			type,level = menu_value.split(':')
			type = CompressionOption(type)
			level = max(0, min(int(level), type.level_count()-1))
		else:
			type = CompressionOption(type)
		return type.setting(level)

	def __eq__(self, other):
		if isinstance(other, CompressionSetting):
			return self.type == other.type and self.level == other.level
		elif isinstance(other, CompressionOption):
			return self.type == other
		else:
			return False

	def __str__(self):
		if self.type.level_count() > 0:
			return '%s:%d' % (self.type, self.level)
		else:
			return str(self.type)
