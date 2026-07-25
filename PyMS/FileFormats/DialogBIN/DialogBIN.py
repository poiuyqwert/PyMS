
from __future__ import annotations

from .BINWidget import BINWidget
from .BINSMK import BINSMK
from .Serialize import WidgetDef, WidgetRemasteredDef, SMKDef

from ...Utilities.PyMSError import PyMSError
from ...Utilities import IO
from ...Utilities import Serialize

import struct

from typing import cast

# Legacy (pre-Remastered) BINs store strings in the Windows ANSI code page,
# Remastered BINs store UTF-8. UTF-8 is tried first since valid UTF-8 is
# almost never valid meaningful ANSI, but not vice versa.
def _decode_string(raw: bytes) -> str:
	try:
		return raw.decode('utf-8')
	except UnicodeDecodeError:
		return raw.decode('cp1252')

class DialogBIN:
	def __init__(self, remastered: bool = False) -> None:
		self.remastered = remastered
		dialog = BINWidget()
		dialog.identifier = 0
		dialog.x2 = 639
		dialog.y2 = 479
		dialog.width = 640
		dialog.height = 480
		self.widgets = [dialog]
		self.smks: list[BINSMK] = []

	def add_widget(self, widget: BINWidget) -> None:
		self.widgets.append(widget)

	def load(self, any_input: IO.AnyInputBytes) -> None:
		with IO.InputBytes(any_input) as input_bytes:
			data = input_bytes.read()
		try:
			self._load_data(data)
		except PyMSError as e:
			raise e
		except Exception as exc:
			raise PyMSError('Load', "Unsupported Dialog BIN file, could possibly be corrupt") from exc

	def _load_data(self, data: bytes) -> None:
		widgets: list[BINWidget] = []
		smk_map: dict[int, BINSMK] = {}
		smks: list[BINSMK] = []
		def load_smk(offset: int) -> None:
			smk_info = list(struct.unpack('<LH3LHHLL',data[offset:offset+BINSMK.BYTE_SIZE]))
			filename_offset = smk_info[3]
			end_offset = data.find(b'\0', filename_offset)
			smk_info[3] = _decode_string(data[filename_offset:end_offset])
			smk = BINSMK()
			smk_map[offset] = smk
			smks.append(smk)
			overlay_smk_offset = smk_info[0]
			if overlay_smk_offset:
				if not overlay_smk_offset in smk_map:
					load_smk(overlay_smk_offset)
				smk_info[0] = smk_map[overlay_smk_offset]
			else:
				smk_info[0] = None
			attrs = BINSMK.ATTR_NAMES
			for attr,value in zip(attrs,smk_info):
				setattr(smk, attr, value)
		def load_widget(offset: int, remastered: bool) -> None:
			widget_struct = BINWidget.STRUCT_REMASTERED if remastered else BINWidget.STRUCT
			widget_size = BINWidget.BYTE_SIZE_REMASTERED if remastered else BINWidget.BYTE_SIZE
			attrs = BINWidget.ATTR_NAMES_REMASTERED if remastered else BINWidget.ATTR_NAMES
			widget_max = BINWidget.TYPE_HTML if remastered else BINWidget.TYPE_HIGHLIGHT_BTN

			widget_info = list(int(v) for v in struct.unpack(widget_struct,data[offset:offset+widget_size]))
			next_widget = widget_info[0]
			widget = BINWidget()
			string_offset = 0
			smk_offset = 0
			for attr,value in zip(attrs,widget_info[1:]):
				if attr == 'string':
					string_offset = value
				elif attr == 'smk':
					smk_offset = value
				else:
					setattr(widget, attr, value)

			if widget.type > widget_max:
				raise PyMSError('Load', f"Invalid widget type '{widget_info[11]}'")

			if string_offset:
				end_offset = data.find(b'\0', string_offset)
				widget.string = _decode_string(data[string_offset:end_offset])

			if widget.type == BINWidget.TYPE_DIALOG:
				next_widget = smk_offset
			elif smk_offset:
				if not smk_offset in smk_map:
					load_smk(smk_offset)
				widget.smk = smk_map[smk_offset]

			if widget.type == BINWidget.TYPE_DIALOG:
				widget.x2 = widget.x1 + widget.responsive_x1
				widget.y2 = widget.y1 + widget.responsive_y1
			else:
				widget.x1 += widgets[0].x1
				widget.y1 += widgets[0].y1
				widget.x2 += widgets[0].x1
				widget.y2 += widgets[0].y1

			widgets.append(widget)
			if next_widget:
				load_widget(next_widget, remastered)
		try:
			load_widget(0, False)
		except Exception:
			widgets = []
			smk_map = {}
			smks = []
			load_widget(0, True)
			self.remastered = True
		self.widgets = widgets
		self.smks = smks

	def save(self, output: IO.AnyOutputBytes, remastered: bool | None = None) -> None:
		data = self._save_data(remastered)
		with IO.OutputBytes(output) as f:
			f.write(data)

	def _save_data(self, remastered: bool | None = None) -> bytes:
		remastered = (self.remastered or self.remastered_required()) if remastered is None else remastered
		widget_struct = BINWidget.STRUCT_REMASTERED if remastered else BINWidget.STRUCT
		widget_size = BINWidget.BYTE_SIZE_REMASTERED if remastered else BINWidget.BYTE_SIZE
		attrs = BINWidget.ATTR_NAMES_REMASTERED if remastered else BINWidget.ATTR_NAMES

		smk_offsets = {}
		string_offsets = {}
		smk_offset = len(self.widgets) * widget_size
		offsets = [0, smk_offset, smk_offset + len(self.smks) * BINSMK.BYTE_SIZE]
		results: list[bytearray] = [bytearray(), bytearray(), bytearray()]
		def save_string(string: str) -> int:
			if not string:
				return 0
			if not string in string_offsets:
				try:
					encoded = string.encode('utf-8' if remastered else 'cp1252')
				except UnicodeEncodeError as exc:
					raise PyMSError('Save', f"String '{string}' contains characters that can't be encoded in a legacy Dialog BIN file (only remastered files support them)") from exc
				string_offsets[string] = offsets[2]
				offsets[2] += len(encoded) + 1
				results[2] += encoded + b'\0'
			return string_offsets[string]
		def save_smk(smk: BINSMK) -> tuple[int, bytes]:
			data = b''
			if not smk in smk_offsets:
				smk_offsets[smk] = offsets[1]
				offsets[1] += BINSMK.BYTE_SIZE
				smk_info = []
				attrs = BINSMK.ATTR_NAMES
				for attr in attrs:
					value = getattr(smk, attr)
					if attr == 'overlay_smk' and value is not None:
						value,data = save_smk(cast(BINSMK, value))
					elif attr == 'filename':
						value = save_string(value)
					if value is None:
						value = 0
					smk_info.append(value)
				data = struct.pack('<LH3LHHLL', *smk_info) + data
			return (smk_offsets[smk],data)
		def save_widget(widget: BINWidget, next_offset: int) -> None:
			widget_info = []
			if widget == last_widget or widget.type == BINWidget.TYPE_DIALOG:
				widget_info.append(0)
			else:
				widget_info.append(next_offset)
			for attr in attrs:
				value = getattr(widget, attr)
				if attr == 'string':
					value = save_string(value)
				elif attr == 'smk':
					if widget.type == BINWidget.TYPE_DIALOG:
						value = next_offset
					elif value is not None:
						value,data = save_smk(value)
						results[1] += data
				elif widget.type == BINWidget.TYPE_DIALOG:
					if attr == 'x2':
						value = widget.width-1
					elif attr == 'y2':
						value = widget.height-1
					elif attr == 'responsive_x1':
						value = widget.width
					elif attr == 'responsive_y1':
						value = widget.height
				elif attr in ('x1','x2'):
					value -= self.widgets[0].x1
				elif attr in ('y1','y2'):
					value -= self.widgets[0].y1
				if value is None:
					value = 0
				widget_info.append(value)
			offsets[0] += widget_size
			results[0] += struct.pack(widget_struct, *widget_info)
		last_widget = self.widgets[-1]
		for widget in self.widgets:
			next_offset = offsets[0] + widget_size
			if widget == last_widget:
				next_offset = 0
			save_widget(widget, next_offset)
		return b''.join(results)

	def interpret(self, any_input: IO.AnyInputText) -> None:
		with IO.InputText(any_input) as input_text:
			data = input_text.read()
		widgets: list[BINWidget] = []
		smks: list[BINSMK] = []
		def builder(_n: int, definition: Serialize.Definition) -> object:
			if definition is SMKDef:
				smk = BINSMK()
				smks.append(smk)
				return smk
			widget = BINWidget()
			# Sentinel to detect the field's presence: IntEncoder can never decode a negative
			widget.scr_unknown1 = -1
			widgets.append(widget)
			return widget
		Serialize.decode_text(data, [WidgetRemasteredDef, SMKDef], builder)
		remastered = False
		for widget in widgets:
			if widget.scr_unknown1 == -1:
				widget.scr_unknown1 = 0
			else:
				remastered = True
		for index, widget in enumerate(widgets):
			if widget.type == BINWidget.TYPE_DIALOG:
				widgets.insert(0, widgets.pop(index))
				break
		else:
			raise PyMSError('Interpreting', 'No dialog found.')
		self.widgets = widgets
		self.smks = smks
		self.remastered = remastered

	def decompile(self, output: IO.AnyOutputText, remastered: bool | None = None) -> None:
		remastered = (self.remastered or self.remastered_required()) if remastered is None else remastered
		widget_def = WidgetRemasteredDef if remastered else WidgetDef
		def get_definition(obj: object) -> (Serialize.Definition | None):
			if isinstance(obj, BINSMK):
				return SMKDef
			if isinstance(obj, BINWidget):
				return widget_def
			return None
		objs: list[tuple[object, int]] = list((smk, i) for i,smk in enumerate(self.smks))
		objs.extend((widget, i) for i,widget in enumerate(self.widgets))
		data = Serialize.encode_texts(objs, get_definition)
		with IO.OutputText(output) as f:
			f.write(data)

	def remastered_required(self) -> bool:
		for widget in self.widgets:
			if widget.type >= BINWidget.TYPE_HTML:
				return True
		return False

# if __name__ == '__main__':
# 	dialogbin = DialogBIN()
# 	dialogbin.load('/Users/zachzahos/Documents/Projects/PyMS/Libs/WORKING/rez/glumain.bin')
# 	data = IO.output_to_bytes(dialogbin.save)
# 	dialogbin.load(data)
# 	dialogbin.decompile('/Users/zachzahos/Documents/Projects/PyMS/Libs/WORKING/rez/glumain.txt')
# 	dialogbin.interpret('/Users/zachzahos/Documents/Projects/PyMS/Libs/WORKING/rez/glumain.txt')
# 	data = IO.output_to_bytes(dialogbin.save)
# 	dialogbin.load(data)
# 	dialogbin.decompile('/Users/zachzahos/Documents/Projects/PyMS/Libs/WORKING/rez/glumain2.txt')
