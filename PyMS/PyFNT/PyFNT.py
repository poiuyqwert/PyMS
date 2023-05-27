# coding: utf-8

from .InfoDialog import InfoDialog

from ..FileFormats.PCX import PCX
from ..FileFormats.FNT import FNT, fnttobmp, bmptofnt
from ..FileFormats.BMP import BMP

from ..Utilities.utils import WIN_REG_AVAILABLE, register_registry
from ..Utilities.UIKit import *
from ..Utilities.analytics import ga, GAScreen
from ..Utilities.trace import setup_trace
from ..Utilities import Assets
from ..Utilities.Settings import Settings
from ..Utilities.MPQHandler import MPQHandler
from ..Utilities.UpdateDialog import UpdateDialog
from ..Utilities.PyMSError import PyMSError
from ..Utilities.ErrorDialog import ErrorDialog
from ..Utilities.SettingsDialog import SettingsDialog
from ..Utilities.AboutDialog import AboutDialog
from ..Utilities.HelpDialog import HelpDialog
from ..Utilities.fileutils import check_allow_overwrite_internal_file

LONG_VERSION = 'v%s' % Assets.version('PyFNT')

DISPLAY_CHARS = [
	'', # 0
	'', # 1
	'', # 2
	'', # 3
	'', # 4
	'', # 5
	'', # 6
	'', # 7
	'', # 8
	'', # 9
	'', # 10
	'', # 11
	'', # 12
	'', # 13
	'', # 14
	'', # 15
	'', # 16
	'', # 17
	'', # 18
	'', # 19
	'', # 20
	'', # 21
	'', # 22
	'', # 23
	'', # 24
	'', # 25
	'', # 26
	'', # 27
	'', # 28
	'', # 29
	'', # 30
	'', # 31
	' ', # 32
	'!', # 33
	'"', # 34
	'#', # 35
	'$', # 36
	'%', # 37
	'&', # 38
	"'", # 39
	'(', # 40
	')', # 41
	'*', # 42
	'+', # 43
	',', # 44
	'-', # 45
	'.', # 46
	'/', # 47
	'0', # 48
	'1', # 49
	'2', # 50
	'3', # 51
	'4', # 52
	'5', # 53
	'6', # 54
	'7', # 55
	'8', # 56
	'9', # 57
	':', # 58
	';', # 59
	'<', # 60
	'=', # 61
	'>', # 62
	'?', # 63
	'@', # 64
	'A', # 65
	'B', # 66
	'C', # 67
	'D', # 68
	'E', # 69
	'F', # 70
	'G', # 71
	'H', # 72
	'I', # 73
	'J', # 74
	'K', # 75
	'L', # 76
	'M', # 77
	'N', # 78
	'O', # 79
	'P', # 80
	'Q', # 81
	'R', # 82
	'S', # 83
	'T', # 84
	'U', # 85
	'V', # 86
	'W', # 87
	'X', # 88
	'Y', # 89
	'Z', # 90
	'[', # 91
	'\\', # 92
	']', # 93
	'^', # 94
	'_', # 95
	'`', # 96
	'a', # 97
	'b', # 98
	'c', # 99
	'd', # 100
	'e', # 101
	'f', # 102
	'g', # 103
	'h', # 104
	'i', # 105
	'j', # 106
	'k', # 107
	'l', # 108
	'm', # 109
	'n', # 110
	'o', # 111
	'p', # 112
	'q', # 113
	'r', # 114
	's', # 115
	't', # 116
	'u', # 117
	'v', # 118
	'w', # 119
	'x', # 120
	'y', # 121
	'z', # 122
	'{', # 123
	'|', # 124
	'}', # 125
	'~', # 126
	'', # 127
	'Ç', # 128
	'ü', # 129
	'é', # 130
	'ä', # 131
	'â', # 132
	'à', # 133
	'å', # 134
	'ç', # 135
	'ê', # 136
	'ë', # 137
	'è', # 138
	'ï', # 139
	'î', # 140
	'ì', # 141
	'Ä', # 142
	'Å', # 143
	'É', # 144
	'æ', # 145
	'Æ', # 146
	'ô', # 147
	'ö', # 148
	'ò', # 149
	'û', # 150
	'ù', # 151
	'ÿ', # 152
	'Ö', # 153
	'Ü', # 154
	'¢', # 155
	'£', # 156
	'¥', # 157
	'', # 158
	'ƒ', # 159
	'á', # 160
	'í', # 161
	'ó', # 162
	'ú', # 163
	'ñ', # 164
	'Ñ', # 165
	'ᵃ', # 166
	'ᵒ', # 167
	'¿', # 168
	'', # 169
	'', # 170
	'', # 171
	'', # 172
	'', # 173
	'', # 174
	'', # 175
	'', # 176
	'', # 177
	'', # 178
	'', # 179
	'', # 180
	'', # 181
	'', # 182
	'', # 183
	'', # 184
	'', # 185
	'', # 186
	'', # 187
	'', # 188
	'', # 189
	'', # 190
	'', # 191
	'', # 192
	'', # 193
	'', # 194
	'', # 195
	'', # 196
	'', # 197
	'', # 198
	'', # 199
	'', # 200
	'', # 201
	'', # 202
	'', # 203
	'', # 204
	'', # 205
	'', # 206
	'', # 207
	'', # 208
	'', # 209
	'', # 210
	'', # 211
	'', # 212
	'', # 213
	'', # 214
	'', # 215
	'', # 216
	'', # 217
	'', # 218
	'', # 219
	'', # 220
	'', # 221
	'', # 222
	'', # 223
	'', # 224
	'ß', # 225
	'', # 226
	'', # 227
	'', # 228
	'', # 229
	'', # 230
	'', # 231
	'', # 232
	'', # 233
	'', # 234
	'', # 235
	'', # 236
	'', # 237
	'', # 238
	'', # 239
	'', # 240
	'', # 241
	'', # 242
	'', # 243
	'', # 244
	'', # 245
	'', # 246
	'', # 247
	'', # 248
	'', # 249
	'', # 250
	'', # 251
	'', # 252
	'', # 253
	'', # 254
	'', # 255
]

class PyFNT(MainWindow):
	def __init__(self, guifile=None):
		self.settings = Settings('PyFNT', '1')
		self.settings.settings.files.set_defaults({'tfontgam':'MPQ:game\\tfontgam.pcx'})

		#Window
		MainWindow.__init__(self)
		self.set_icon('PyFNT')
		self.protocol('WM_DELETE_WINDOW', self.exit)
		ga.set_application('PyFNT', Assets.version('PyFNT'))
		ga.track(GAScreen('PyFNT'))
		setup_trace('PyFNT', self)
		Theme.load_theme(self.settings.get('theme'), self)
		self.resizable(False, False)

		self.fnt = None
		self.file = None
		self.edited = False
		self.palette = None

		self.update_title()

		#Toolbar
		self.toolbar = Toolbar()
		self.toolbar.add_button(Assets.get_image('new'), self.new, 'New', Ctrl.n)
		self.toolbar.add_button(Assets.get_image('open'), self.open, 'Open', Ctrl.o)
		self.toolbar.add_button(Assets.get_image('save'), self.save, 'Save', Ctrl.s, enabled=False, tags='file_open')
		self.toolbar.add_button(Assets.get_image('saveas'), self.saveas, 'Save As', Ctrl.Alt.a, enabled=False, tags='file_open')
		self.toolbar.add_button(Assets.get_image('close'), self.close, 'Close', Ctrl.w, enabled=False, tags='file_open')
		self.toolbar.add_gap()
		self.toolbar.add_button(Assets.get_image('exportc'), self.exports, 'Export Font', Ctrl.e, enabled=False, tags='file_open')
		self.toolbar.add_button(Assets.get_image('importc'), self.imports, 'Import Font', Ctrl.i, enabled=False, tags='file_open')
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('asc3topyai'), self.special, "Manage MPQ's and Special Palette", Ctrl.m)
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('register'), self.register, 'Set as default *.fnt editor (Windows Only)', enabled=WIN_REG_AVAILABLE)
		self.toolbar.add_button(Assets.get_image('help'), self.help, 'Help', Key.F1)
		self.toolbar.add_button(Assets.get_image('about'), self.about, 'About PyFNT')
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('exit'), self.exit, 'Exit', Shortcut.Exit)
		self.toolbar.pack(side=TOP, padx=1, pady=1, fill=X)

		frame = Frame(self)
		leftframe = Frame(frame)
		#Listbox
		Label(leftframe, text='Characters:', anchor=W).pack(side=TOP, fill=X)
		self.listbox = ScrolledListbox(leftframe, width=15, height=17)
		self.listbox.bind(WidgetEvent.Listbox.Select, lambda *e: self.preview())
		self.listbox.pack(side=TOP, padx=1, pady=1, fill=BOTH, expand=1)
		leftframe.pack(side=LEFT, padx=1, pady=1, fill=Y)

		rightframe = Frame(frame)

		#Canvas
		Label(rightframe, text='Display:', anchor=W).pack(side=TOP, fill=X)
		t = Frame(rightframe)
		self.canvas = Canvas(t, width=0, height=0, background='#000000', theme_tag='preview')
		self.canvas.pack(side=TOP, padx=2, pady=2)
		t.pack(side=LEFT, fill=Y)
		rightframe.pack(side=LEFT, fill=BOTH, expand=1, padx=1, pady=1)

		frame.pack(fill=BOTH, expand=1)

		#Statusbar
		self.status = StringVar()
		self.status.set('Load or create a Font.')
		statusbar = StatusBar(self)
		statusbar.add_label(self.status, width=35)
		self.editstatus = statusbar.add_icon(Assets.get_image('save'))
		statusbar.add_spacer()
		statusbar.pack(side=BOTTOM, fill=X)

		self.mpqhandler = MPQHandler(self.settings.get('mpqs',[]))
		if (not 'mpqs' in self.settings or not len(self.settings['mpqs'])) and self.mpqhandler.add_defaults():
			self.settings['mpqs'] = self.mpqhandler.mpq_paths()
		e = self.open_files()

		if guifile:
			self.open(file=guifile)

		self.settings.windows.load_window_size('main', self)

		UpdateDialog.check_update(self, 'PyFNT')

		if e:
			self.special(err=e)

	def open_files(self):
		self.mpqhandler.open_mpqs()
		err = None
		try:
			palette = PCX()
			palette.load_file(self.mpqhandler.get_file(self.settings.settings.files.tfontgam))
		except PyMSError as e:
			err = e
		else:
			self.palette = palette
			self.palette.palette[self.palette.image[0][0]] = [50,100,50]
		self.mpqhandler.close_mpqs()
		return err

	def unsaved(self):
		if self.fnt and self.edited:
			file = self.file
			if not file:
				file = 'Unnamed.fnt'
			save = MessageBox.askquestion(parent=self, title='Save Changes?', message="Save changes to '%s'?" % file, default=MessageBox.YES, type=MessageBox.YESNOCANCEL)
			if save != MessageBox.NO:
				if save == MessageBox.CANCEL:
					return True
				if self.file:
					self.save()
				else:
					self.saveas()

	def is_file_open(self):
		return not not self.fnt

	def action_states(self):
		self.toolbar.tag_enabled('file_open', self.is_file_open())

	def updatelist(self):
		self.listbox.delete(0,END)
		for l in range(len(self.fnt.letters)):
			self.listbox.insert(END, '%s (%s)' % (self.fnt.start+l,DISPLAY_CHARS[self.fnt.start+l]))
		self.listbox.select_set(0)

	def resize(self):
		self.canvas['width'] = self.fnt.width * 4 + 1
		self.canvas['height'] = self.fnt.height * 4 + 1
		self.canvas.delete(ALL)
		for y in range(self.fnt.height):
			for x in range(self.fnt.width):
				self.canvas.create_rectangle(3+x*4,3+y*4,6+x*4,6+y*4, fill='#%02X%02X%02X' % tuple(self.palette.palette[self.palette.image[0][0]]), outline='', tag='%d,%d' % (x,y))

	def preview(self, e=None):
		if self.listbox.size():
			l = int(self.listbox.curselection()[0])
			for y,yd in enumerate(self.fnt.letters[l]):
				for x,c in enumerate(yd):
					item = self.canvas.find_withtag('%d,%d' % (x,y))
					self.canvas.itemconfigure(item, fill='#%02X%02X%02X' % tuple(self.palette.palette[self.palette.image[0][c]]))

	def update_title(self):
		file_path = self.file
		if not file_path and self.is_file_open():
			file_path = 'Untitled.fnt'
		if not file_path:
			self.title('PyFNT %s' % LONG_VERSION)
		else:
			self.title('PyFNT %s (%s)' % (LONG_VERSION, file_path))

	def mark_edited(self, edited=True):
		self.edited = edited
		self.editstatus['state'] = NORMAL if edited else DISABLED

	def new(self, key=None):
		if not self.unsaved():
			s = InfoDialog(self,True)
			if s.size is not None:
				self.fnt = FNT()
				self.fnt.width,self.fnt.height,self.fnt.start = s.width.get(),s.height.get(),s.lowi.get()
				for _ in range(s.letters.get()):
					self.fnt.letters.append([[0]*self.fnt.width for __ in range(self.fnt.height)])
				self.updatelist()
				self.file = None
				self.status.set('Editing new Font.')
				self.mark_edited(False)
				self.update_title()
				self.action_states()
				self.resize()
				self.preview()

	def open(self, key=None, file=None):
		if not self.unsaved():
			if file is None:
				file = self.settings.lastpath.fnt.select_open_file(self, title='Open FNT', filetypes=[FileType.fnt()])
				if not file:
					return
			if isinstance(file, FNT):
				fnt = file
			else:
				fnt = FNT()
				try:
					fnt.load_file(file)
				except PyMSError as e:
					ErrorDialog(self, e)
					return
				self.file = file
			self.fnt = fnt
			self.updatelist()
			self.update_title()
			self.status.set('Load Successful!')
			self.mark_edited(False)
			self.action_states()
			self.resize()
			self.preview()

	def save(self, key=None):
		self.saveas(file_path=self.file)

	def saveas(self, key=None, file_path=None):
		if not file_path:
			file_path = self.settings.lastpath.fnt.select_save_file(self, title='Save FNT As', filetypes=[FileType.fnt()])
			if not file_path:
				return
		elif not check_allow_overwrite_internal_file(file_path):
			return
		try:
			self.fnt.save_file(file_path)
		except PyMSError as e:
			ErrorDialog(self, e)
			return
		self.file = file_path
		self.status.set('Save Successful!')
		self.mark_edited(False)
		self.update_title()
		self.action_states()

	def close(self, key=None):
		if not self.unsaved():
			self.fnt = None
			self.file = None
			self.update_title()
			self.status.set('Load or create a FNT.')
			self.mark_edited(False)
			self.action_states()
			self.listbox.delete(0, END)
			self.canvas.delete(ALL)
			self.canvas['width'] = 0
			self.canvas['height'] = 0
			self.firstbox = None

	def exports(self, key=None):
		file = self.settings.lastpath.bmp.select_save_file(self, key='export', title='Export BMP', filetypes=[FileType.bmp()])
		if file:
			self.status.set('Extracting font, please wait...')
			self.update_idletasks()
			try:
				fnttobmp(self.fnt,[self.palette.palette[i] for i in self.palette.image[0]] + [[50,100,50] for _ in range(256 - len(self.palette.image[0]))],file)
			except PyMSError as e:
				ErrorDialog(self, e)
			self.status.set('Font exported successfully!')

	def imports(self, key=None):
		file = self.settings.lastpath.bmp.select_open_file(self, key='import', title='Import BMP', filetypes=[FileType.bmp()])
		if file:
			s = InfoDialog(self)
			if s.size is not None:
				self.status.set('Importing FNT, please wait...')
				b = BMP()
				try:
					b.load_file(file)
					fnt = bmptofnt(b,s.lowi.get(),s.letters.get())
				except PyMSError as e:
					ErrorDialog(self, e)
				else:
					self.open(file=fnt)
					self.mark_edited()
					self.status.set('Font imported successfully!')

	def special(self, key=None, err=None):
		SettingsDialog(self, [('Palette Settings',[('tfontgam.pcx','The special palette which holds the text color.','tfontgam','PCX')]),('Theme',)], (550,380), err, settings=self.settings, mpqhandler=self.mpqhandler)

	def register(self, e=None):
		try:
			register_registry('PyFNT', 'fnt', 'Font')
		except PyMSError as e:
			ErrorDialog(self, e)

	def help(self, e=None):
		HelpDialog(self, self.settings, 'Help/Programs/PyFNT.md')

	def about(self, key=None):
		thanks = [
			('FaRTy1billion','Help with file format and example FNT previewer'),
			('StormCost-Fortress.net','FNT specs')
		]
		AboutDialog(self, 'PyFNT', LONG_VERSION, thanks)

	def exit(self, e=None):
		if not self.unsaved():
			self.settings.windows.save_window_size('main', self)
			self.settings.save()
			self.destroy()
