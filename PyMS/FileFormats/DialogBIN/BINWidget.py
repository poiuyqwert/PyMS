
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from .BINSMK import BINSMK

class BINWidget:
	BYTE_SIZE = 86
	STRUCT =            '<L6H4LH5L4HLL4HLL'
	BYTE_SIZE_REMASTERED = 88
	STRUCT_REMASTERED = '<L6H4L2H5L4HLL4HLL'

	ATTR_NAMES = ('x1','y1','x2','y2','width','height','unknown1','string','flags','unknown2','identifier','type','unknown3','unknown4','unknown5','unknown6','responsive_x1','responsive_y1','responsive_x2','responsive_y2','unknown7','smk','text_offset_x','text_offset_y','responsive_width','responsive_height','unknown8','unknown9')
	ATTR_NAMES_REMASTERED = ('x1','y1','x2','y2','width','height','unknown1','string','flags','unknown2','scr_unknown1','identifier','type','unknown3','unknown4','unknown5','unknown6','responsive_x1','responsive_y1','responsive_x2','responsive_y2','unknown7','smk','text_offset_x','text_offset_y','responsive_width','responsive_height','unknown8','unknown9')

	FLAG_UNK1 = 0x00000001
	FLAG_DISABLED = 0x00000002
	FLAG_UNK2 = 0x00000004
	FLAG_VISIBLE = 0x00000008
	FLAG_RESPONSIVE = 0x00000010
	FLAG_UNK3 = 0x00000020
	FLAG_CANCEL_BTN = 0x00000040
	FLAG_NO_HOVER_SND = 0x00000080
	FLAG_VIRTUAL_HOTKEY = 0x00000100
	FLAG_HAS_HOTKEY = 0x00000200
	FLAG_FONT_SIZE_10 = 0x00000400
	FLAG_FONT_SIZE_16 = 0x00000800
	FLAG_UNK4 = 0x00001000
	FLAG_TRANSPARENCY = 0x00002000
	FLAG_FONT_SIZE_16x = 0x00004000
	FLAG_UNK5 = 0x00008000
	FLAG_FONT_SIZE_14 = 0x00010000
	FLAG_UNK6 = 0x00020000
	FLAG_TRANSLUCENT = 0x00040000
	FLAG_DEFAULT_BTN = 0x00080000
	FLAG_ON_TOP = 0x00100000
	FLAG_TEXT_ALIGN_CENTER = 0x00200000
	FLAG_TEXT_ALIGN_RIGHT = 0x00400000
	FLAG_TEXT_ALIGN_CENTER2 = 0x00800000
	FLAG_ALIGN_TOP = 0x01000000
	FLAG_ALIGN_MIDDLE = 0x02000000
	FLAG_ALIGN_BOTTOM = 0x04000000
	FLAG_UNK7 = 0x08000000
	FLAG_UNK8 = 0x10000000
	FLAG_UNK9 = 0x20000000
	FLAG_NO_CLICK_SND = 0x40000000
	FLAG_UNK10 = 0x80000000

	FLAGS_TEXT_ALIGN = (FLAG_TEXT_ALIGN_CENTER | FLAG_TEXT_ALIGN_RIGHT | FLAG_TEXT_ALIGN_CENTER2)

	TYPE_DIALOG = 0
	TYPE_DEFAULT_BTN = 1
	TYPE_BUTTON = 2
	TYPE_OPTION_BTN = 3
	TYPE_CHECKBOX = 4
	TYPE_IMAGE = 5
	TYPE_SLIDER = 6
	TYPE_UNK = 7
	TYPE_TEXTBOX = 8
	TYPE_LABEL_LEFT_ALIGN = 9
	TYPE_LABEL_CENTER_ALIGN = 10
	TYPE_LABEL_RIGHT_ALIGN = 11
	TYPE_LISTBOX = 12
	TYPE_COMBOBOX = 13
	TYPE_HIGHLIGHT_BTN = 14
	# Remastered
	TYPE_HTML = 15

	TYPE_NAMES = [
		'Dialog',
		'Default Button',
		'Button',
		'Option Button',
		'CheckBox',
		'Image',
		'Slider',
		'Unknown',
		'TextBox',
		'Label (Left Align)',
		'Label (Center Align)',
		'Label (Right Align)',
		'ListBox',
		'ComboBox',
		'Highlight Button',
		'HTML'
	]

	def __init__(self, ctrl_type: int = TYPE_DIALOG) -> None:
		self.x1 = 0
		self.y1 = 0
		self.x2 = 0
		self.y2 = 0
		self.width = 0
		self.height = 0
		self.unknown1 = 0
		self.string = ''
		self.flags = BINWidget.FLAG_VISIBLE
		self.unknown2 = 0
		self.identifier = 65535
		self.scr_unknown1 = 0
		self.type = ctrl_type
		self.unknown3 = 0
		self.unknown4 = 0
		self.unknown5 = 0
		self.unknown6 = 0
		self.responsive_x1 = 0
		self.responsive_y1 = 0
		self.responsive_x2 = 0
		self.responsive_y2 = 0
		self.unknown7 = 0
		self.smk: BINSMK | None = None
		self.text_offset_x = 0
		self.text_offset_y = 0
		self.responsive_width = 0
		self.responsive_height = 0
		self.unknown8 = 0
		self.unknown9 = 0
		if self.type in (BINWidget.TYPE_DEFAULT_BTN, BINWidget.TYPE_BUTTON, BINWidget.TYPE_OPTION_BTN, BINWidget.TYPE_CHECKBOX, BINWidget.TYPE_SLIDER, BINWidget.TYPE_TEXTBOX, BINWidget.TYPE_LISTBOX, BINWidget.TYPE_COMBOBOX, BINWidget.TYPE_HIGHLIGHT_BTN, BINWidget.TYPE_HTML):
			self.flags |= BINWidget.FLAG_RESPONSIVE

	def copy(self) -> BINWidget:
		clone = BINWidget(self.type)
		clone.restore(self)
		return clone

	def restore(self, other: BINWidget) -> None:
		self.x1 = other.x1
		self.y1 = other.y1
		self.x2 = other.x2
		self.y2 = other.y2
		self.width = other.width
		self.height = other.height
		self.unknown1 = other.unknown1
		self.string = other.string
		self.flags = other.flags
		self.unknown2 = other.unknown2
		self.identifier = other.identifier
		self.scr_unknown1 = other.scr_unknown1
		self.type = other.type
		self.unknown3 = other.unknown3
		self.unknown4 = other.unknown4
		self.unknown5 = other.unknown5
		self.unknown6 = other.unknown6
		self.responsive_x1 = other.responsive_x1
		self.responsive_y1 = other.responsive_y1
		self.responsive_x2 = other.responsive_x2
		self.responsive_y2 = other.responsive_y2
		self.unknown7 = other.unknown7
		self.smk = other.smk
		self.text_offset_x = other.text_offset_x
		self.text_offset_y = other.text_offset_y
		self.responsive_width = other.responsive_width
		self.responsive_height = other.responsive_height
		self.unknown8 = other.unknown8
		self.unknown9 = other.unknown9

	def bounding_box(self) -> tuple[int, int, int, int]:
		x1 = (self.x1 if self.x1 < self.x2 else self.x2)
		y1 = (self.y1 if self.y1 < self.y2 else self.y2)
		x2 = (self.x2 if self.x2 > self.x1 else self.x1)
		y2 = (self.y2 if self.y2 > self.y1 else self.y1)
		return (x1,y1,x2,y2)

	def has_responsive(self) -> bool:
		return (self.flags & BINWidget.FLAG_RESPONSIVE == BINWidget.FLAG_RESPONSIVE) #(self.responsive_x1 or self.responsive_y1 or self.responsive_x2 or self.responsive_y2)

	def responsive_box(self) -> tuple[int, int, int, int]:
		box = self.bounding_box()
		return (box[0] + self.responsive_x1, box[1] + self.responsive_y1, box[0] + self.responsive_x2, box[1] + self.responsive_y2)

	def is_button(self) -> bool:
		return self.type in (BINWidget.TYPE_BUTTON, BINWidget.TYPE_HIGHLIGHT_BTN, BINWidget.TYPE_OPTION_BTN, BINWidget.TYPE_DEFAULT_BTN)

	def display_text(self) -> (str | None):
		if self.type not in (BINWidget.TYPE_DIALOG, BINWidget.TYPE_IMAGE, BINWidget.TYPE_HTML):
			if self.is_button() and self.flags & (BINWidget.FLAG_VIRTUAL_HOTKEY | BINWidget.FLAG_HAS_HOTKEY):
				return self.string[1:]
			else:
				return self.string
		return None
