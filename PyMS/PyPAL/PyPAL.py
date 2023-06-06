
from ..FileFormats.Palette import Palette

from ..Utilities.utils import WIN_REG_AVAILABLE, register_registry
from ..Utilities.UIKit import *
from ..Utilities.Settings import Settings
from ..Utilities.analytics import ga, GAScreen
from ..Utilities.trace import setup_trace
from ..Utilities import Assets
from ..Utilities.UpdateDialog import UpdateDialog
from ..Utilities.PyMSError import PyMSError
from ..Utilities.ErrorDialog import ErrorDialog
from ..Utilities.AboutDialog import AboutDialog
from ..Utilities.HelpDialog import HelpDialog
from ..Utilities.fileutils import check_allow_overwrite_internal_file
from ..Utilities.SettingsDialog import SettingsDialog

import re

LONG_VERSION = 'v%s' % Assets.version('PyPAL')

class PyPAL(MainWindow):
	def __init__(self, guifile=None):
		#Config
		self.settings = Settings('PyPAL', '1')

		#Window
		MainWindow.__init__(self)
		self.set_icon('PyPAL')
		self.protocol('WM_DELETE_WINDOW', self.exit)
		ga.set_application('PyPAL', Assets.version('PyPAL'))
		ga.track(GAScreen('PyPAL'))
		setup_trace('PyPAL', self)
		Theme.load_theme(self.settings.get('theme'), self)
		self.resizable(False, False)

		self.palette = None
		self.file = None
		self.format = None
		self.edited = False
		self.selected = None

		self.update_title()

		#Toolbar
		self.toolbar = Toolbar(self)
		self.toolbar.add_button(Assets.get_image('new'), self.new, 'New', Ctrl.n)
		self.toolbar.add_button(Assets.get_image('open'), self.open, 'Open', Ctrl.o)
		self.toolbar.add_button(Assets.get_image('save'), self.save, 'Save', Ctrl.s, enabled=False, tags=('file_open', 'format_known'))
		self.toolbar.add_button(Assets.get_image('saveriff'), lambda: self.saveas(file_type=Palette.FileType.riff), 'Save as RIFF *.pal', Ctrl.r, enabled=False, tags='file_open')
		self.toolbar.add_button(Assets.get_image('savejasc'), lambda: self.saveas(file_type=Palette.FileType.jasc), 'Save as JASC *.pal', Ctrl.j, enabled=False, tags='file_open')
		self.toolbar.add_button(Assets.get_image('savepal'), lambda: self.saveas(file_type=Palette.FileType.sc_pal), 'Save as StarCraft *.pal', Ctrl.p, enabled=False, tags='file_open')
		self.toolbar.add_button(Assets.get_image('savewpe'), lambda: self.saveas(file_type=Palette.FileType.wpe), 'Save as StarCraft Terrain *.wpe', Ctrl.t, enabled=False, tags='file_open')
		self.toolbar.add_button(Assets.get_image('saveact'), lambda: self.saveas(file_type=Palette.FileType.act), 'Save as Adobe Color Table *.act', Ctrl.a, enabled=False, tags='file_open')
		self.toolbar.add_button(Assets.get_image('close'), self.close, 'Close', Ctrl.w, enabled=False, tags='file_open')
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('asc3topyai'), self.sets, "Manage Settings", Ctrl.m)
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('register'), self.register, 'Set as default *.pal and *.wpe editor (Windows Only)', enabled=WIN_REG_AVAILABLE)
		self.toolbar.add_button(Assets.get_image('help'), self.help, 'Help', Key.F1)
		self.toolbar.add_button(Assets.get_image('about'), self.about, 'About PyPAL')
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('exit'), self.exit, 'Exit', Shortcut.Exit)
		self.toolbar.pack(side=TOP, padx=1, pady=1, fill=X)

		self.palmenu = Menu(self, tearoff=0)
		self.palmenu.add_command(label='Copy', command=self.copy, shortcut=Ctrl.c)
		self.palmenu.add_command(label='Paste', command=self.paste, shortcut=Ctrl.p, tags='paste')

		#Canvas
		self.canvas = Canvas(self, width=273, height=273, background='#000000', coordinate_adjust=Canvas.coordinate_adjust_os, theme_tag='preview')
		self.canvas.pack(padx=2, pady=2)
		for n in range(256):
			x,y = 3+17*(n%16),3+17*(n//16)
			self.canvas.create_rectangle(x, y, x+15, y+15, fill='#000000', outline='#000000')
			self.canvas.tag_bind(n+1, Cursor.Enter, lambda e,i=n: self.colorstatus(e,i))
			self.canvas.tag_bind(n+1, Cursor.Leave, lambda e,i=-1: self.colorstatus(e,i))
			self.canvas.tag_bind(n+1, Mouse.Click_Left, lambda e,i=n: self.select(e,i))
			self.canvas.tag_bind(n+1, Double.Click_Left, lambda e,i=n: self.changecolor(e,i))
			self.canvas.tag_bind(n+1, ButtonRelease.Click_Right, lambda e,i=n: self.popup(e,i))
		self.sel = self.canvas.create_rectangle(0,0,0,0,outline='#FFFFFF')

		#Statusbar
		self.status = StringVar()
		self.status.set('Load or create a Palette.')
		statusbar = StatusBar(self)
		statusbar.add_label(self.status, width=40)
		self.editstatus = statusbar.add_icon(Assets.get_image('save'))
		statusbar.add_spacer()
		statusbar.pack(side=BOTTOM, fill=X)

		if guifile:
			self.open(file=guifile)

		self.settings.windows.load_window_size('main', self)

		UpdateDialog.check_update(self, 'PyPAL')

	def unsaved(self):
		if self.palette and self.edited:
			file = self.file
			if not file:
				file = 'Unnamed.pal'
			save = MessageBox.askquestion(parent=self, title='Save Changes?', message="Save changes to '%s'?" % file, default=MessageBox.YES, type=MessageBox.YESNOCANCEL)
			if save != MessageBox.NO:
				if save == MessageBox.CANCEL:
					return True
				if self.file:
					self.save()
				else:
					self.saveas()

	def is_file_open(self):
		return not not self.palette

	def action_states(self):
		self.toolbar.tag_enabled('file_open', self.is_file_open())
		self.toolbar.tag_enabled('format_known', self.format is not None)

	def popup(self, e, i):
		if self.palette:
			self.select(e,i)
			self.palmenu.tag_enabled('paste', not not self.canpaste())
			self.palmenu.post(e.x_root, e.y_root)

	def update(self):
		if self.palette:
			pal = self.palette.palette
		else:
			pal = [(0,0,0)] * 256
		for n,rgb in enumerate(pal):
			c = '#%02X%02X%02X' % tuple(rgb)
			self.canvas.itemconfigure(n+1, fill=c, outline=c)

	def colorstatus(self, e, i):
		if self.palette and i > -1:
			info = (i,) + tuple(self.palette.palette[i]) * 2
			self.status.set('Index: %s  RGB: (%s,%s,%s)  Hex: #%02X%02X%02X' % info)

	def select(self, e, i):
		if self.palette:
			self.selected = i
			x,y = 2+17*(i%16),2+17*(i//16)
			self.canvas.coords(self.sel, x, y, x+17, y+17)

	def changecolor(self, e, i):
		if self.palette:
			self.select(None,i)
			c = ColorChooser.askcolor(parent=self, initialcolor='#%02X%02X%02X' % tuple(self.palette.palette[i]), title='Select Color')
			if c[1]:
				self.mark_edited()
				self.canvas.itemconfigure(i+1, fill=c[1], outline=c[1])
				self.palette.palette[i] = c[0]

	def copy(self, key=None):
		if self.palette and self.selected is not None:
			self.clipboard_clear()
			self.clipboard_append('#%02X%02X%02X' % tuple(self.palette.palette[self.selected]))

	def canpaste(self, c=None):
		try:
			if c is None:
				c = self.selection_get(selection='CLIPBOARD')
		except:
			pass
		else:
			m = re.match(r'^#([\dA-Fa-f]{2})([\dA-Fa-f]{2})([\dA-Fa-f]{2})$', c)
			if m:
				return [int(c,16) for c in m.groups()]

	def paste(self, key=None):
		if self.palette and self.selected is not None:
			try:
				c = self.selection_get(selection='CLIPBOARD')
			except:
				pass
			else:
				rgb = self.canpaste(c)
				if rgb:
					self.palette.palette[self.selected] = rgb
					self.canvas.itemconfigure(self.selected+1, fill=c, outline=c)
					self.mark_edited()

	def update_title(self):
		file_path = self.file
		if not file_path and self.is_file_open():
			file_path = 'Untitled.pal'
		if not file_path:
			self.title('PyPAL %s' % LONG_VERSION)
		else:
			self.title('PyPAL %s (%s)' % (LONG_VERSION, file_path))

	def mark_edited(self, edited=True):
		self.edited = edited
		self.editstatus['state'] = NORMAL if edited else DISABLED

	def new(self, key=None):
		if not self.unsaved():
			self.palette = Palette()
			self.file = None
			self.format = None
			self.status.set('Editing new Palette.')
			self.mark_edited(False)
			self.update_title()
			if self.selected is None:
				self.selected = 0
				self.select(None,0)
			self.update()
			self.action_states()
			self.colorstatus(None, 0)

	def open(self, key=None, file=None):
		if not self.unsaved():
			if file is None:
				file = self.settings.lastpath.select_open_file(self, title='Open Palette', filetypes=Palette.FileType.load_types())
				if not file:
					return
			pal = Palette()
			try:
				pal.load_file(file)
				self.format = pal.format
			except PyMSError as e:
				ErrorDialog(self, e)
				return
			self.palette = pal
			self.file = file
			self.update_title()
			self.status.set('Load Successful!')
			self.mark_edited(False)
			if self.selected is None:
				self.selected = 0
				self.select(None,0)
			self.update()
			self.action_states()
			self.colorstatus(None, 0)

	def save(self, key=None):
		self.saveas(file_path=self.file, file_format=self.format)

	def saveas(self, key=None, file_path=None, file_format=None, file_type=Palette.FileType.sc_pal):
		if not file_path:
			file_path = self.settings.lastpath.select_save_file(self, title='Save Palette As', filetypes=Palette.FileType.save_types(file_type.format, file_type.ext))
			if not file_path:
				return
		elif not check_allow_overwrite_internal_file(file_path):
			return
		if not file_format:
			file_format = file_type.format
		try:
			self.palette.save(file_path, file_format)
		except PyMSError as e:
			ErrorDialog(self, e)
		self.status.set('Save Successful!')
		self.mark_edited(False)
		self.file = file_path
		self.format = file_format
		self.update_title()
		self.action_states()

	def close(self, key=None):
		if not self.is_file_open():
			return
		if not self.unsaved():
			self.palette = None
			self.file = None
			self.update_title()
			self.status.set('Load or create a palette.')
			self.mark_edited(False)
			self.selected = None
			self.canvas.coords(self.sel, 0, 0, 0, 0)
			self.update()
			self.action_states()

	def register(self, e=None):
		for type,ext in [('','pal'),('Tileset ','wpe')]:
			try:
				register_registry('PyPAL', ext, type + 'Palette')
			except PyMSError as e:
				ErrorDialog(self, e)
				break

	def sets(self, key=None, err=None):
		SettingsDialog(self, [('Theme',)], (550,380), err, settings=self.settings)

	def help(self, e=None):
		HelpDialog(self, self.settings, 'Help/Programs/PyPAL.md')

	def about(self, key=None):
		AboutDialog(self, 'PyPAL', LONG_VERSION)

	def exit(self, e=None):
		if not self.unsaved():
			self.settings.windows.save_window_size('main', self)
			self.settings.save()
			self.destroy()
