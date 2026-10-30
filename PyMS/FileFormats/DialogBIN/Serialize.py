
from .BINWidget import BINWidget
from .BINSMK import BINSMK

from .. import TBL

from ...Utilities.PyMSError import PyMSError
from ...Utilities import Serialize
from ...Utilities import JSON

class WidgetField:
	x1 = 'x1'
	y1 = 'y1'
	x2 = 'x2'
	y2 = 'y2'
	width = 'width'
	height = 'height'
	unknown1 = 'unknown1'
	string = 'string'
	flags = 'flags'
	unknown2 = 'unknown2'
	scr_unknown1 = 'scr_unknown1'
	identifier = 'identifier'
	type = 'type'
	unknown3 = 'unknown3'
	unknown4 = 'unknown4'
	unknown5 = 'unknown5'
	unknown6 = 'unknown6'
	responsive_x1 = 'responsive_x1'
	responsive_y1 = 'responsive_y1'
	responsive_x2 = 'responsive_x2'
	responsive_y2 = 'responsive_y2'
	unknown7 = 'unknown7'
	smk = 'smk'
	text_offset_x = 'text_offset_x'
	text_offset_y = 'text_offset_y'
	responsive_width = 'responsive_width'
	responsive_height = 'responsive_height'
	unknown8 = 'unknown8'
	unknown9 = 'unknown9'

	class Flag:
		unknown1 = 'unknown1'
		disabled = 'disabled'
		unknown2 = 'unknown2'
		visible = 'visible'
		responsive = 'responsive'
		unknown3 = 'unknown3'
		cancel_btn = 'cancel_btn'
		no_hover_snd = 'no_hover_snd'
		virtual_hotkey = 'virtual_hotkey'
		has_hotkey = 'has_hotkey'
		font_size_10 = 'font_size_10'
		font_size_16 = 'font_size_16'
		unknown4 = 'unknown4'
		transparency = 'transparency'
		font_size_16x = 'font_size_16x'
		unknown5 = 'unknown5'
		font_size_14 = 'font_size_14'
		unknown6 = 'unknown6'
		translucent = 'translucent'
		default_btn = 'default_btn'
		on_top = 'on_top'
		text_align_center = 'text_align_center'
		text_align_right = 'text_align_right'
		text_align_center2 = 'text_align_center2'
		align_top = 'align_top'
		align_middle = 'align_middle'
		align_bottom = 'align_bottom'
		unknown7 = 'unknown7'
		unknown8 = 'unknown8'
		unknown9 = 'unknown9'
		no_click_snd = 'no_click_snd'
		unknown10 = 'unknown10'

class SMKField:
	overlay_smk = 'overlay_smk'
	flags = 'flags'
	unknown1 = 'unknown1'
	filename = 'filename'
	unknown2 = 'unknown2'
	offset_x = 'offset_x'
	offset_y = 'offset_y'
	unknown3 = 'unknown3'
	unknown4 = 'unknown4'

	class Flag:
		fade_in = 'fade_in'
		dark = 'dark'
		repeats = 'repeats'
		show_on_hover = 'show_on_hover'
		unknown1 = 'unknown1'
		unknown2 = 'unknown2'
		unknown3 = 'unknown3'
		unknown4 = 'unknown4'
		unknown_0100 = 'unknown_0100'
		unknown_0200 = 'unknown_0200'
		unknown_0400 = 'unknown_0400'
		unknown_0800 = 'unknown_0800'
		unknown_1000 = 'unknown_1000'
		unknown_2000 = 'unknown_2000'
		unknown_4000 = 'unknown_4000'
		unknown_8000 = 'unknown_8000'

class TBLStringEncoder(Serialize.Encoder[str, str]):
	# `/` is escaped so a string containing `//` can't be eaten as a comment,
	# and outermost spaces are escaped since the parser strips each line.
	def encode(self, value: str) -> JSON.Value:
		result = TBL.decompile_string(value, include='/')
		if result.startswith(' '):
			result = '<32>' + result[1:]
		if result.endswith(' '):
			result = result[:-1] + '<32>'
		return result

	def decode(self, value: JSON.Value) -> str:
		if not isinstance(value, str):
			raise PyMSError('Decode', f"Expected a string, got '{value}'")
		return TBL.compile_string(value)

	def apply(self, value: str, current: str) -> str:
		return value

TYPE_KEYS = (
	'dialog',
	'default_button',
	'button',
	'option_button',
	'checkbox',
	'image',
	'slider',
	'unknown',
	'textbox',
	'label_left_align',
	'label_center_align',
	'label_right_align',
	'listbox',
	'combobox',
	'highlight_button',
	'html',
)
_TYPE_KEY_MAP = {key: value for value,key in enumerate(TYPE_KEYS)}

class WidgetTypeEncoder(Serialize.Encoder[int, int]):
	def encode(self, value: int) -> JSON.Value:
		if 0 <= value < len(TYPE_KEYS):
			return TYPE_KEYS[value]
		return value

	def decode(self, value: JSON.Value) -> int:
		if isinstance(value, str):
			if value in _TYPE_KEY_MAP:
				return _TYPE_KEY_MAP[value]
			if value.isdigit():
				return int(value)
		elif isinstance(value, int) and not isinstance(value, bool):
			return value
		raise PyMSError('Decode', f"'{value}' is not a valid widget type")

	def apply(self, value: int, current: int) -> int:
		return value

def _widget_structure(remastered: bool) -> Serialize.Structure:
	structure: Serialize.Structure = {
		WidgetField.x1: Serialize.IntEncoder(),
		WidgetField.y1: Serialize.IntEncoder(),
		WidgetField.x2: Serialize.IntEncoder(),
		WidgetField.y2: Serialize.IntEncoder(),
		WidgetField.width: Serialize.IntEncoder(),
		WidgetField.height: Serialize.IntEncoder(),
		WidgetField.unknown1: Serialize.IntEncoder(),
		WidgetField.string: TBLStringEncoder(),
		WidgetField.flags: Serialize.IntFlagEncoder({
			WidgetField.Flag.unknown1: BINWidget.FLAG_UNK1,
			WidgetField.Flag.disabled: BINWidget.FLAG_DISABLED,
			WidgetField.Flag.unknown2: BINWidget.FLAG_UNK2,
			WidgetField.Flag.visible: BINWidget.FLAG_VISIBLE,
			WidgetField.Flag.responsive: BINWidget.FLAG_RESPONSIVE,
			WidgetField.Flag.unknown3: BINWidget.FLAG_UNK3,
			WidgetField.Flag.cancel_btn: BINWidget.FLAG_CANCEL_BTN,
			WidgetField.Flag.no_hover_snd: BINWidget.FLAG_NO_HOVER_SND,
			WidgetField.Flag.virtual_hotkey: BINWidget.FLAG_VIRTUAL_HOTKEY,
			WidgetField.Flag.has_hotkey: BINWidget.FLAG_HAS_HOTKEY,
			WidgetField.Flag.font_size_10: BINWidget.FLAG_FONT_SIZE_10,
			WidgetField.Flag.font_size_16: BINWidget.FLAG_FONT_SIZE_16,
			WidgetField.Flag.unknown4: BINWidget.FLAG_UNK4,
			WidgetField.Flag.transparency: BINWidget.FLAG_TRANSPARENCY,
			WidgetField.Flag.font_size_16x: BINWidget.FLAG_FONT_SIZE_16x,
			WidgetField.Flag.unknown5: BINWidget.FLAG_UNK5,
			WidgetField.Flag.font_size_14: BINWidget.FLAG_FONT_SIZE_14,
			WidgetField.Flag.unknown6: BINWidget.FLAG_UNK6,
			WidgetField.Flag.translucent: BINWidget.FLAG_TRANSLUCENT,
			WidgetField.Flag.default_btn: BINWidget.FLAG_DEFAULT_BTN,
			WidgetField.Flag.on_top: BINWidget.FLAG_ON_TOP,
			WidgetField.Flag.text_align_center: BINWidget.FLAG_TEXT_ALIGN_CENTER,
			WidgetField.Flag.text_align_right: BINWidget.FLAG_TEXT_ALIGN_RIGHT,
			WidgetField.Flag.text_align_center2: BINWidget.FLAG_TEXT_ALIGN_CENTER2,
			WidgetField.Flag.align_top: BINWidget.FLAG_ALIGN_TOP,
			WidgetField.Flag.align_middle: BINWidget.FLAG_ALIGN_MIDDLE,
			WidgetField.Flag.align_bottom: BINWidget.FLAG_ALIGN_BOTTOM,
			WidgetField.Flag.unknown7: BINWidget.FLAG_UNK7,
			WidgetField.Flag.unknown8: BINWidget.FLAG_UNK8,
			WidgetField.Flag.unknown9: BINWidget.FLAG_UNK9,
			WidgetField.Flag.no_click_snd: BINWidget.FLAG_NO_CLICK_SND,
			WidgetField.Flag.unknown10: BINWidget.FLAG_UNK10,
		}),
		WidgetField.unknown2: Serialize.IntEncoder(),
	}
	if remastered:
		structure[WidgetField.scr_unknown1] = Serialize.IntEncoder()
	structure[WidgetField.identifier] = Serialize.IntEncoder()
	structure[WidgetField.type] = WidgetTypeEncoder()
	structure[WidgetField.unknown3] = Serialize.IntEncoder()
	structure[WidgetField.unknown4] = Serialize.IntEncoder()
	structure[WidgetField.unknown5] = Serialize.IntEncoder()
	structure[WidgetField.unknown6] = Serialize.IntEncoder()
	structure[WidgetField.responsive_x1] = Serialize.IntEncoder()
	structure[WidgetField.responsive_y1] = Serialize.IntEncoder()
	structure[WidgetField.responsive_x2] = Serialize.IntEncoder()
	structure[WidgetField.responsive_y2] = Serialize.IntEncoder()
	structure[WidgetField.unknown7] = Serialize.IntEncoder()
	structure[WidgetField.smk] = Serialize.ReferenceEncoder('SMK')
	structure[WidgetField.text_offset_x] = Serialize.IntEncoder()
	structure[WidgetField.text_offset_y] = Serialize.IntEncoder()
	structure[WidgetField.responsive_width] = Serialize.IntEncoder()
	structure[WidgetField.responsive_height] = Serialize.IntEncoder()
	structure[WidgetField.unknown8] = Serialize.IntEncoder()
	structure[WidgetField.unknown9] = Serialize.IntEncoder()
	return structure

WidgetDef = Serialize.Definition('Widget', Serialize.IDMode.none, _widget_structure(False))
WidgetRemasteredDef = Serialize.Definition('Widget', Serialize.IDMode.none, _widget_structure(True))

SMKDef = Serialize.Definition('SMK', Serialize.IDMode.header, {
	SMKField.overlay_smk: Serialize.ReferenceEncoder('SMK'),
	SMKField.flags: Serialize.IntFlagEncoder({
		SMKField.Flag.fade_in: BINSMK.FLAG_FADE_IN,
		SMKField.Flag.dark: BINSMK.FLAG_DARK,
		SMKField.Flag.repeats: BINSMK.FLAG_REPEATS,
		SMKField.Flag.show_on_hover: BINSMK.FLAG_SHOW_ON_HOVER,
		SMKField.Flag.unknown1: BINSMK.FLAG_UNK1,
		SMKField.Flag.unknown2: BINSMK.FLAG_UNK2,
		SMKField.Flag.unknown3: BINSMK.FLAG_UNK3,
		SMKField.Flag.unknown4: BINSMK.FLAG_UNK4,
		SMKField.Flag.unknown_0100: 0x0100,
		SMKField.Flag.unknown_0200: 0x0200,
		SMKField.Flag.unknown_0400: 0x0400,
		SMKField.Flag.unknown_0800: 0x0800,
		SMKField.Flag.unknown_1000: 0x1000,
		SMKField.Flag.unknown_2000: 0x2000,
		SMKField.Flag.unknown_4000: 0x4000,
		SMKField.Flag.unknown_8000: 0x8000,
	}),
	SMKField.unknown1: Serialize.IntEncoder(),
	SMKField.filename: TBLStringEncoder(),
	SMKField.unknown2: Serialize.IntEncoder(),
	SMKField.offset_x: Serialize.IntEncoder(),
	SMKField.offset_y: Serialize.IntEncoder(),
	SMKField.unknown3: Serialize.IntEncoder(),
	SMKField.unknown4: Serialize.IntEncoder(),
})
