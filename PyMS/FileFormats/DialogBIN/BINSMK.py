
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from .BINWidget import BINWidget

class BINSMK:
	BYTE_SIZE = 30
	ATTR_NAMES = ('overlay_smk','flags','unknown1','filename','unknown2','offset_x','offset_y','unknown3','unknown4')

	FLAG_FADE_IN = 0x01
	FLAG_DARK = 0x02
	FLAG_REPEATS = 0x04
	FLAG_SHOW_ON_HOVER = 0x08
	FLAG_UNK1 = 0x10
	FLAG_UNK2 = 0x20
	FLAG_UNK3 = 0x40
	FLAG_UNK4 = 0x80

	def __init__(self) -> None:
		self.widgets: list[BINWidget] = []
		self.overlay_smk: BINSMK | None = None
		self.flags = 0
		self.unknown1 = 0
		self.filename = ''
		self.unknown2 = 0
		self.offset_x = 0
		self.offset_y = 0
		self.unknown3 = 0
		self.unknown4 = 0

	def copy(self) -> BINSMK:
		clone = BINSMK()
		clone.restore(self)
		return clone

	def restore(self, other: BINSMK) -> None:
		self.widgets = other.widgets
		self.overlay_smk = other.overlay_smk
		self.flags = other.flags
		self.unknown1 = other.unknown1
		self.filename = other.filename
		self.unknown2 = other.unknown2
		self.offset_x = other.offset_x
		self.offset_y = other.offset_y
		self.unknown3 = other.unknown3
		self.unknown4 = other.unknown4

	def add_widget(self, widget: BINWidget) -> None:
		self.widgets.append(widget)

	def remove_widget(self, widget: BINWidget) -> None:
		self.widgets.remove(widget)
