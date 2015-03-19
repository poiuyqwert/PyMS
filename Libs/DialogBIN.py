from utils import *
import TBL

import struct, re

class DialogBINWidget(object):
	BYTE_SIZE = 86
	ATTR_NAMES = ('x1','y1','x2','y2','width','height','unknown1','string','flags','unknown2','identifier','type','unknown3','unknown4','unknown5','unknown6','responsive_x1','responsive_y1','responsive_x2','responsive_y2','unknown7','smk','text_offset_x','text_offset_y','responsive_width','responsive_height','unknown8','unknown9')

	FLAG_UNK1 = 0x00000001
	FLAG_DISABLED = 0x00000002
	FLAG_UNK2 = 0x00000004
	FLAG_VISIBLE = 0x00000008
	FLAG_RESPONSIVE = 0x00000010
	FLAG_UNK3 = 0x00000020
	FLAG_CANCEL_BTN = 0x00000040
	FLAG_NO_HOVER_SND = 0x00000080
	FLAG_SPECIAL_HOTKEY = 0x00000100
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
	FLAG_NO_CLICK_SOUNG = 0x40000000
	FLAG_UNK10 = 0x80000000

	TYPE_DIALOG = 0
	TYPE_DEFAULT_BTN = 0
	TYPE_BUTTON = 2
	TYPE_OPTION_BTN = 3
	TYPE_CHECKBOX = 4
	TYPE_IMAGE = 5
	TYPE_SLIDER = 6
	TYPE_UNK = 7
	TYPE_TEXTBOX = 8
	TYPE_LABEL_LEFT_ALIGN = 9
	TYPE_LABEL_RIGHT_ALIGN = 10
	TYPE_LABEL_CENTER_ALIGN = 11
	TYPE_LISTBOX = 12
	TYPE_COMBOBOX = 13
	TYPE_HIGHLIGHT_BTN = 14

	TYPE_NAMES = ['Dialog','Deafult Button','Button','Option Button','CheckBox','Image','Slider','Unknown','TextBox','Label (left Align)','Label (Right Align)','Label (Center Align)','ListBox','ComboBox','Highlight Button']

	def __init__(self):
		self.x1 = 0
		self.y1 = 0
		self.x2 = 0
		self.y2 = 0
		self.width = 0
		self.height = 0
		self.unknown1 = 0
		self.string = None
		self.flags = 0
		self.unknown2 = 0
		self.identifier = 0
		self.type = 0
		self.unknown3 = 0
		self.unknown4 = 0
		self.unknown5 = 0
		self.unknown6 = 0
		self.responsive_x1 = 0
		self.responsive_y1 = 0
		self.responsive_x2 = 0
		self.responsive_y2 = 0
		self.unknown7 = 0
		self.smk = None
		self.text_offset_x = 0
		self.text_offset_y = 0
		self.responsive_width = 0
		self.responsive_height = 0
		self.unknown8 = 0
		self.unknown9 = 0

class DialogBINSMK(object):
	BYTE_SIZE = 30
	ATTR_NAMES = ('overlay_smk','flags','unknown1','filename','unknown2','overlay_offset_x','overlay_offset_y','unknown3','unknown4')

	FLAG_FADE_IN = 0x0001
	FLAG_DARK = 0x0002
	FLAG_REPEATS = 0x0004
	FLAG_SHOW_IF_OVER = 0x0008
	FLAG_UNK = 0x0010

	def __init__(self):
		self.overlay_smk = None
		self.flags = 0
		self.unknown1 = 0
		self.filename = ''
		self.unknown2 = 0
		self.overlay_offset_x = 0
		self.overlay_offset_y = 0
		self.unknown3 = 0
		self.unknown4 = 0


class DialogBIN:
	def __init__(self):
		self.widgets = []
		self.smks = []

	def load_file(self, file):
		try:
			if isstr(file):
				f = open(file,'rb')
				data = f.read()
				f.close()
			else:
				data = file.read()
		except:
			raise PyMSError('Load',"Could not load Dialog BIN file '%s'" % file)
		try:
			self.load_data(data)
		except PyMSError, e:
			raise e
		except:
			raise
			raise PyMSError('Load',"Unsupported Dialog BIN file '%s', could possibly be corrupt" % file)

	def load_data(self, data):
		widgets = []
		smk_map = {}
		smks = []
		def load_smk(offset):
			smk_info = list(struct.unpack('<LH3LHHLL',data[offset:offset+DialogBINSMK.BYTE_SIZE]))
			filename_offset = smk_info[3]
			end_offset = data.find('\0', filename_offset)
			smk_info[3] = data[filename_offset:end_offset]
			smk = DialogBINSMK()
			smk_map[offset] = smk
			smks.append(smk)
			overlay_smk_offset = smk_info[0]
			if overlay_smk_offset:
				if not overlay_smk_offset in smk_map:
					load_smk(overlay_smk_offset)
				smk_info[0] = smk_map[overlay_smk_offset]
			else:
				smk_info[0] = None
			attrs = DialogBINSMK.ATTR_NAMES
			for attr,value in zip(attrs,smk_info):
				setattr(smk, attr, value)
		def load_widget(offset):
			widget_info = list(struct.unpack('<L6H4LH5L4HLL4HLL',data[offset:offset+DialogBINWidget.BYTE_SIZE]))
			string_offset = widget_info[8]
			if string_offset:
				end_offset = data.find('\0', string_offset)
				widget_info[8] = data[string_offset:end_offset]
			else:
				widget_info[8] = None
			next_widget = widget_info[0]
			smk_offset = widget_info[22]
			if widget_info[11] == DialogBINWidget.TYPE_DIALOG:
				next_widget = smk_offset
				smk_offset = 0
			if smk_offset:
				if not smk_offset in smk_map:
					load_smk(smk_offset)
				widget_info[22] = smk_map[smk_offset]
			else:
				widget_info[22] = None
			widget = DialogBINWidget()
			widgets.append(widget)
			attrs = DialogBINWidget.ATTR_NAMES
			for attr,value in zip(attrs,widget_info[1:]):
				setattr(widget, attr, value)
			if next_widget:
				load_widget(next_widget)
		load_widget(0)
		self.widgets = widgets
		self.smks = smks

	def save_file(self, file):
		try:
			f = AtomicWriter(file, 'wb')
		except:
			raise
		f.write(self.save_data())
		f.close()

	def save_data(self):
		smk_offsets = {}
		string_offsets = {}
		smk_offset = len(self.widgets) * DialogBINWidget.BYTE_SIZE
		offsets = [0, smk_offset, smk_offset + len(self.smks) * DialogBINSMK.BYTE_SIZE]
		results = ['','','']
		def save_string(string):
			if not string in string_offsets:
				string_offsets[string] = offsets[2]
				offsets[2] += len(string) + 1
				results[2] += string + '\0'
			return string_offsets[string]
		def save_smk(smk):
			data = ''
			if not smk in smk_offsets:
				smk_offsets[smk] = offsets[1]
				offsets[1] += DialogBINSMK.BYTE_SIZE
				smk_info = []
				attrs = DialogBINSMK.ATTR_NAMES
				for attr in attrs:
					value = getattr(smk, attr)
					if attr == 'overlay_smk' and value != None:
						value,data = save_smk(value)
					elif attr == 'filename' and value != None:
						value = save_string(value)
					if value == None:
						value = 0
					smk_info.append(value)
				data = struct.pack('<LH3LHHLL', *smk_info) + data
			return (smk_offsets[smk],data)
		def save_widget(widget, next_offset):
			widget_info = []
			if widget == last_widget or widget.type == DialogBINWidget.TYPE_DIALOG:
				widget_info.append(0)
			else:
				widget_info.append(next_offset)
			attrs = DialogBINWidget.ATTR_NAMES
			for attr in attrs:
				value = getattr(widget, attr)
				if attr == 'string' and value != None:
					value = save_string(value)
				elif attr == 'smk':
					if widget.type == DialogBINWidget.TYPE_DIALOG:
						value = next_offset
					elif value != None:
						value,data = save_smk(value)
						results[1] += data
				if value == None:
					value = 0
				widget_info.append(value)
			offsets[0] += DialogBINWidget.BYTE_SIZE
			results[0] += struct.pack('<L6H4LH5L4HLL4HLL', *widget_info)
		last_widget = self.widgets[-1]
		for widget in self.widgets:
			next_offset = offsets[0] + DialogBINWidget.BYTE_SIZE
			if widget == last_widget:
				next_offset = 0
			save_widget(widget, next_offset)
		return ''.join(results)

	def interpret_file(self, file):
		try:
			if isstr(file):
				f = open(file,'rb')
				data = f.read()
				f.close()
			else:
				data = file.read()
		except:
			raise PyMSError('Load',"Could not load file '%s'" % file)
		self.interpret_data(data)

	def interpret_data(self, data):
		lines = re.split('(?:\r?\n)+', data)
		widgets = []
		smks = {}
		backfill_smks = {}
		working = None
		def get_smk(smk_id):
			smk = None
			if smk_id in smks:
				smk = smks[smk_id]
			else:
				if not smk_id in backfill_smks:
					backfill_smks[smk_id] = []
				backfill_smks[smk_id].append(working)
			return smk
		for n,raw_line in enumerate(lines):
			line = raw_line.split('#',1)[0].strip()
			if not line:
				continue
			if line == 'Widget:':
				working = DialogBINWidget()
				widgets.append(working)
				continue
			m = re.match('^SMK (\d+):$', line)
			if m:
				smk_id = int(m.group(1))
				if smk_id in smks:
					raise PyMSError('Interpreting',"Duplicate definition for SMK '%s'" % attr,n,line)
				working = DialogBINSMK()
				if smk_id in backfill_smks:
					for obj in backfill_smks[smk_id]:
						if isinstance(obj, DialogBINWidget):
							obj.smk = working
						else:
							obj.overlay_smk = working
					del backfill_smks[smk_id]
				smks[smk_id] = working
				continue
			if not working:
				raise PyMSError('Interpreting','Unexpected line, expected a Widget or SMK header',n,line)
			m = re.match('^(\S+)\s+(.+)$', line)
			attr = m.group(1)
			value = m.group(2)
			if isinstance(working, DialogBINWidget):
				if not attr in DialogBINWidget.ATTR_NAMES:
					raise PyMSError('Interpreting',"Invalid Widget attribute name '%s'" % attr,n,line)
				if attr == 'smk':
					if value == 'None':
						value = None
					else:
						try:
							smk_id = int(value)
						except:
							raise PyMSError('Interpreting',"Invalid SMK id '%s', expected an Integer or 'None'" % value,n,line)
						value = get_smk(smk_id)
				elif attr == 'string':
					if value == 'None':
						value = None
					else:
						value = TBL.compile_string(value)
				elif attr == 'flags':
					value = flags(value, 27)
				else:
					value = int(value)
			else:
				if not attr in DialogBINSMK.ATTR_NAMES:
					raise PyMSError('Interpreting',"Invalid SMK attribute name '%s'" % attr,n,line)
				if attr == 'overlay_smk':
					if value == 'None':
						value = None
					else:
						try:
							smk_id = int(value)
						except:
							raise PyMSError('Interpreting',"Invalid SMK id '%s', expected an Integer or 'None'" % value,n,line)
						value = get_smk(smk_id)
				elif attr == 'filename':
					value = TBL.compile_string(value)
				elif attr == 'flags':
					value = flags(value, 5)
				else:
					value = int(value)
			setattr(working, attr, value)
		if backfill_smks:
			raise PyMSError('Interpreting',"SMK %s is missing" % backfill_smks.keys()[0])
		for i in xrange(len(widgets)):
			widget = widgets[i]
			if widget.type == DialogBINWidget.TYPE_DIALOG:
				del widgets[i]
				widgets.insert(i,widget)
				break
		self.widgets = widgets
		self.smks = list(smk for i,smk in sorted(smks.iteritems(),key=lambda s: s[1]))

	def decompile_file(self, file):
		try:
			f = AtomicWriter(file, 'wb')
		except:
			raise
		f.write(self.decompile_data())
		f.close()

	def decompile_data(self):
		result = ''
		attrs = DialogBINSMK.ATTR_NAMES
		longest = sorted(len(n) for n in attrs)[-1]
		for i,smk in enumerate(self.smks):
			result += 'SMK %d:\n' % i
			for attr in attrs:
				value = getattr(smk, attr)
				hint = ''
				if attr == 'overlay_smk' and value != None:
					value = self.smks.index(value)
				elif attr == 'filename':
					value = TBL.decompile_string(value)
				elif attr == 'flags':
					value = flags(value, 5)
				result += '\t%s%s%s%s%s\n' % (attr,' ' * (longest - len(attr) + 1),value,' # ' if hint else '',hint)
			result += '\n'
		attrs = DialogBINWidget.ATTR_NAMES
		longest = sorted(len(n) for n in attrs)[-1]
		for widget in self.widgets:
			result += 'Widget:\n'
			for attr in attrs:
				value = getattr(widget, attr)
				hint = ''
				if attr == 'smk' and value != None:
					value = self.smks.index(value)
				elif attr == 'string' and value != None:
					value = TBL.decompile_string(value)
				elif attr == 'flags':
					value = flags(value, 27)
				elif attr == 'type':
					if value < len(DialogBINWidget.TYPE_NAMES):
						hint = DialogBINWidget.TYPE_NAMES[value]
					else:
						hint = 'Unknown'
				result += '\t%s%s%s%s%s\n' % (attr,' ' * (longest - len(attr) + 1),value,' # ' if hint else '',hint)
			result += '\n'
		return result

# if __name__ == '__main__':
# 	dialogbin = DialogBIN()
# 	dialogbin.load_file('/Users/zachzahos/Documents/Projects/PyMS/Libs/WORKING/rez/glumain.bin')
# 	data = dialogbin.save_data()
# 	dialogbin.load_data(data)
# 	dialogbin.decompile_file('/Users/zachzahos/Documents/Projects/PyMS/Libs/WORKING/rez/glumain.txt')
# 	dialogbin.interpret_file('/Users/zachzahos/Documents/Projects/PyMS/Libs/WORKING/rez/glumain.txt')
# 	data = dialogbin.save_data()
# 	dialogbin.load_data(data)
# 	dialogbin.decompile_file('/Users/zachzahos/Documents/Projects/PyMS/Libs/WORKING/rez/glumain2.txt')

