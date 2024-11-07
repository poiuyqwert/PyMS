
from __future__ import annotations

from ..FileFormats.MPQ.SFmpq import Z_BEST_SPEED, Z_DEFAULT_COMPRESSION, Z_NO_COMPRESSION, Z_BEST_COMPRESSION, MAWA_QUALITY_LOW, MAWA_QUALITY_MEDIUM, MAWA_QUALITY_HIGH
from ..FileFormats.MPQ.MPQ import MPQCompressionFlag

from enum import Enum

class CompressionOption(Enum):
	NoCompression = 'none'
	Standard = 'standard'
	Deflate = 'deflate'
	Audio = 'audio'
	Auto = 'auto'

	def display_name(self) -> str:
		match self:
			case CompressionOption.NoCompression:
				return 'None'
			case CompressionOption.Standard:
				return 'Standard'
			case CompressionOption.Deflate:
				return 'Deflate'
			case CompressionOption.Audio:
				return 'Audio'
			case CompressionOption.Auto:
				return 'Auto'

	def compression_type(self) -> int:
		match self:
			case CompressionOption.Standard:
				return MPQCompressionFlag.pkware
			case CompressionOption.Deflate:
				return MPQCompressionFlag.zlib
			case CompressionOption.Audio:
				return MPQCompressionFlag.huffman | MPQCompressionFlag.wav_mono
			case _:
				return MPQCompressionFlag.none

	def level_count(self) -> int:
		return len(self.compression_levels())

	def compression_levels(self) -> tuple[int, ...]:
		if self == CompressionOption.Deflate:
			return tuple(range(min(Z_DEFAULT_COMPRESSION, Z_NO_COMPRESSION, Z_BEST_COMPRESSION), max(Z_DEFAULT_COMPRESSION, Z_NO_COMPRESSION, Z_BEST_COMPRESSION)+1))
		elif self == CompressionOption.Audio:
			return (MAWA_QUALITY_LOW, MAWA_QUALITY_MEDIUM, MAWA_QUALITY_HIGH)
		else:
			return ()

	def setting(self, level: int = 0) -> CompressionSetting:
		return CompressionSetting(self, max(0, min(level, self.level_count()-1)))

class CompressionSetting(object):
	def __init__(self, type: CompressionOption, level: int) -> None:
		self.type = type
		self.level = level

	def compression_level(self) -> int:
		compression_levels = self.type.compression_levels()
		if not compression_levels:
			return 0
		return compression_levels[self.level]

	def level_name(self) -> str:
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
			else: #if compression_level == MAWA_QUALITY_HIGH:
				return 'Highest (Least Space)'
		else:
			return ''

	@staticmethod
	def parse_value(menu_value: str) -> CompressionSetting:
		type_name = menu_value
		level = 0
		if ':' in menu_value:
			type_name,level_str = menu_value.split(':')
			type = CompressionOption(type_name)
			level = max(0, min(int(level_str), type.level_count()-1))
		else:
			type = CompressionOption(type_name)
		return type.setting(level)

	def __eq__(self, other: object) -> bool:
		if isinstance(other, CompressionSetting):
			return self.type == other.type and self.level == other.level
		elif isinstance(other, CompressionOption):
			return self.type == other
		else:
			return False

	def __str__(self) -> str:
		if self.type.level_count() > 0:
			return '%s:%d' % (self.type.value, self.level)
		else:
			return self.type.value
