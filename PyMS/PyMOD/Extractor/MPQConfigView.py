
from __future__ import annotations

from ...PyMPQ.CompressionSetting import CompressionOption, CompressionSetting

from ...Utilities import UIKit as UI
from ...Utilities import JSON

# Mirrors `CompileStep.PackageMPQ.FileConfig`: the only per-file packaging setting is the
# `compression` override, everything else (`max_files`, `block_size`, `autocompression`) is
# configured on the containing `.mpq` folder
class MPQConfigView(UI.LabelFrame):
	COMPRESSION_CHOICES = (
		CompressionOption.NoCompression,
		CompressionOption.Standard,
		CompressionOption.Deflate,
		CompressionOption.Audio
	)

	def __init__(self, parent: UI.Misc) -> None:
		UI.LabelFrame.__init__(self, parent, text='MPQ Config')

		self.override = UI.BooleanVar(value=False)
		self.compression_index = UI.IntVar()
		self.compression_level = UI.IntVar()

		UI.Checkbutton(self, text='Override compression', variable=self.override, command=self.update_states).pack(side=UI.TOP, anchor=UI.W, padx=3, pady=(3,0))
		UI.Label(self, text="Without an override the file uses the containing MPQ's autocompression settings.", anchor=UI.W, justify=UI.LEFT).pack(side=UI.TOP, fill=UI.X, padx=3)

		self.type_frame = UI.Frame(self)
		UI.Label(self.type_frame, text='Compression Type:', anchor=UI.W, justify=UI.LEFT).pack(side=UI.TOP, fill=UI.X)
		self.type_dropdown = UI.DropDown(self.type_frame, self.compression_index, [compression_type.display_name() for compression_type in MPQConfigView.COMPRESSION_CHOICES], self.choose_compression)
		self.type_dropdown.pack(side=UI.TOP, fill=UI.X)
		self.type_frame.pack(side=UI.TOP, fill=UI.X, padx=3, pady=(3,0))

		self.levels_frame = UI.Frame(self)
		UI.Label(self.levels_frame, text='Compression Level:', anchor=UI.W, justify=UI.LEFT).pack(side=UI.TOP, fill=UI.X)
		self.levels_dropdown = UI.DropDown(self.levels_frame, self.compression_level, [])
		self.levels_dropdown.pack(side=UI.TOP, fill=UI.X)

		self.compression_index.set(MPQConfigView.COMPRESSION_CHOICES.index(CompressionOption.Standard))
		self.update_levels(self.compression_setting())
		self.update_states()

	def compression_setting(self) -> CompressionSetting:
		compression_type = MPQConfigView.COMPRESSION_CHOICES[self.compression_index.get()]
		return compression_type.setting(self.compression_level.get())

	def choose_compression(self, compression_type_index: int) -> None:
		compression_type = MPQConfigView.COMPRESSION_CHOICES[compression_type_index]
		self.update_levels(compression_type.setting())

	def update_levels(self, compression: CompressionSetting) -> None:
		if compression.type.level_count() > 0:
			level_names = []
			for level in range(compression.type.level_count()):
				level_names.append(compression.type.setting(level).level_name())
			self.levels_dropdown.setentries(level_names)
			self.compression_level.set(compression.level)
			self.levels_frame.pack(side=UI.TOP, fill=UI.X, padx=3, pady=(3,0))
		else:
			self.compression_level.set(0)
			self.levels_frame.forget()
		self.update_states()

	def update_states(self) -> None:
		state = UI.NORMAL if self.override.get() else UI.DISABLED
		self.type_dropdown['state'] = state
		self.levels_dropdown['state'] = state

	# The keys this view contributes to the extracted item's `config.json`. Nothing is written when
	# the compression isn't overridden, so the file keeps inheriting the MPQ's autocompression
	def config_json(self) -> JSON.Object:
		if not self.override.get():
			return {}
		return {'compression': str(self.compression_setting())}
