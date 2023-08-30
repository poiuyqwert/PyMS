
from .Config import PyPALConfig
from .SettingsDialog import SettingsDialog

from ..FileFormats.Palette import Palette
from ..FileFormats.Images import RGB

from ..Utilities.utils import WIN_REG_AVAILABLE, register_registry
from ..Utilities.UIKit import *
from ..Utilities.analytics import ga, GAScreen
from ..Utilities.trace import setup_trace
from ..Utilities import Assets
from ..Utilities.UpdateDialog import UpdateDialog
from ..Utilities.PyMSError import PyMSError
from ..Utilities.ErrorDialog import ErrorDialog
from ..Utilities.AboutDialog import AboutDialog
from ..Utilities.HelpDialog import HelpDialog
from ..Utilities.fileutils import check_allow_overwrite_internal_file
from ..Utilities.CheckSaved import CheckSaved

import re

from typing import Callable

LONG_VERSION = 'v%s' % Assets.version('PyPAL')

class PyPAL(MainWindow):
	def __init__(self, guifile: str | None = None) -> None:
		#Config
		self.config_ = PyPALConfig()

		#Window
		MainWindow.__init__(self)
		self.set_icon('PyPAL')
		self.protocol('WM_DELETE_WINDOW', self.exit)
		ga.set_application('PyPAL', Assets.version('PyPAL'))
		ga.track(GAScreen('PyPAL'))
		setup_trace('PyPAL', self)
		Theme.load_theme(self.config_.theme.value, self)
		self.resizable(False, False)

		self.palette: Palette | None = None
		self.file: str | None = None
		self.format: Palette.Format | None = None
		self.edited = False
		self.selected: int | None = None

		self.update_title()

		#Toolbar
		self.toolbar = Toolbar(self)
		self.toolbar.add_button(Assets.get_image('new'), self.new, 'New', Ctrl.n)
		self.toolbar.add_button(Assets.get_image('open'), self.open, 'Open', Ctrl.o)
		def save() -> None:
			self.save()
		self.toolbar.add_button(Assets.get_image('save'), save, 'Save', Ctrl.s, enabled=False, tags=('file_open', 'format_known'))
		def saveas_callback(file_type: Palette.FileType) -> Callable[[], None]:
			def saveas() -> None:
				self.saveas(file_type=file_type)
			return saveas
		self.toolbar.add_button(Assets.get_image('saveriff'), saveas_callback(Palette.FileType.riff), 'Save as RIFF *.pal', Ctrl.r, enabled=False, tags='file_open')
		self.toolbar.add_button(Assets.get_image('savejasc'), saveas_callback(Palette.FileType.jasc), 'Save as JASC *.pal', Ctrl.j, enabled=False, tags='file_open')
		self.toolbar.add_button(Assets.get_image('savepal'), saveas_callback(Palette.FileType.sc_pal), 'Save as StarCraft *.pal', Ctrl.p, enabled=False, tags='file_open')
		self.toolbar.add_button(Assets.get_image('savewpe'), saveas_callback(Palette.FileType.wpe), 'Save as StarCraft Terrain *.wpe', Ctrl.t, enabled=False, tags='file_open')
		self.toolbar.add_button(Assets.get_image('saveact'), saveas_callback(Palette.FileType.act), 'Save as Adobe Color Table *.act', Ctrl.a, enabled=False, tags='file_open')
		self.toolbar.add_button(Assets.get_image('close'), self.close, 'Close', Ctrl.w, enabled=False, tags='file_open')
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('asc3topyai'), self.sets, "Manage Settings", Ctrl.m)
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('register'), self.register_registry, 'Set as default *.pal and *.wpe editor (Windows Only)', enabled=WIN_REG_AVAILABLE)
		self.toolbar.add_button(Assets.get_image('help'), self.help, 'Help', Key.F1)
		self.toolbar.add_button(Assets.get_image('about'), self.about, 'About PyPAL')
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('exit'), self.exit, 'Exit', Shortcut.Exit)
		self.toolbar.pack(side=TOP, padx=1, pady=1, fill=X)

		self.palmenu = Menu(self, tearoff=0)
		self.palmenu.add_command(label='Copy', command=self.copy, shortcut=Ctrl.c) # type: ignore[call-arg]
		self.palmenu.add_command(label='Paste', command=self.paste, shortcut=Ctrl.p, tags='paste') # type: ignore[call-arg]

		#Canvas
		self.canvas = Canvas(self, width=273, height=273, background='#000000', coordinate_adjust=Canvas.coordinate_adjust_os, theme_tag='preview') # type: ignore[call-arg, attr-defined]
		self.canvas.pack(padx=2, pady=2)
		def colorstatus_callback(index: int) -> Callable[[Event], None]:
			def colorstatus(event: Event) -> None:
				self.colorstatus(event, index)
			return colorstatus
		def select_callback(index: int) -> Callable[[Event], None]:
			def select(event: Event) -> None:
				self.select(event, index)
			return select
		def changecolor_callback(index: int) -> Callable[[Event], None]:
			def changecolor(event: Event) -> None:
				self.changecolor(event, index)
			return changecolor
		def popup_callback(index: int) -> Callable[[Event], None]:
			def popup(event: Event) -> None:
				self.popup(event, index)
			return popup
		for n in range(256):
			x,y = 3+17*(n%16),3+17*(n//16)
			self.canvas.create_rectangle(x, y, x+15, y+15, fill='#000000', outline='#000000')
			self.canvas.tag_bind(n+1, Cursor.Enter(), colorstatus_callback(n))
			self.canvas.tag_bind(n+1, Cursor.Leave(), colorstatus_callback(-1))
			self.canvas.tag_bind(n+1, Mouse.Click_Left(), select_callback(n))
			self.canvas.tag_bind(n+1, Double.Click_Left(), changecolor_callback(n))
			self.canvas.tag_bind(n+1, ButtonRelease.Click_Right(), popup_callback(n))
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

		self.config_.windows.main.load(self)

		UpdateDialog.check_update(self, 'PyPAL')

	def check_saved(self) -> CheckSaved:
		if not self.palette or not self.edited:
			return CheckSaved.saved
		file = self.file
		if not file:
			file = 'Unnamed.pal'
		save = MessageBox.askquestion(parent=self, title='Save Changes?', message="Save changes to '%s'?" % file, default=MessageBox.YES, type=MessageBox.YESNOCANCEL)
		if save == MessageBox.NO:
			return CheckSaved.saved
		if save == MessageBox.CANCEL:
			return CheckSaved.cancelled
		if self.file:
			return self.save()
		else:
			return self.saveas()

	def is_file_open(self) -> bool:
		return not not self.palette

	def action_states(self) -> None:
		self.toolbar.tag_enabled('file_open', self.is_file_open())
		self.toolbar.tag_enabled('format_known', self.format is not None)

	def popup(self, e: Event, i: int) -> None:
		if not self.palette:
			return
		self.select(e,i)
		self.palmenu.tag_enabled('paste', not not self.canpaste()) # type: ignore[attr-defined]
		self.palmenu.post(e.x_root, e.y_root)

	def update(self) -> None:
		if self.palette:
			pal = self.palette.palette
		else:
			pal = [(0,0,0)] * 256
		for n,rgb in enumerate(pal):
			c = '#%02X%02X%02X' % tuple(rgb)
			self.canvas.itemconfigure(n+1, fill=c, outline=c)

	def colorstatus(self, e: Event | None, i: int) -> None:
		if self.palette and i > -1:
			info = (i,) + tuple(self.palette.palette[i]) * 2
			self.status.set('Index: %s  RGB: (%s,%s,%s)  Hex: #%02X%02X%02X' % info)

	def select(self, e: Event | None, i: int) -> None:
		if not self.palette:
			return
		self.selected = i
		x,y = 2+17*(i%16),2+17*(i//16)
		self.canvas.coords(self.sel, x, y, x+17, y+17)

	def changecolor(self, e: Event, i: int) -> None:
		if not self.palette:
			return
		self.select(None,i)
		c = ColorChooser.askcolor(parent=self, initialcolor='#%02X%02X%02X' % tuple(self.palette.palette[i]), title='Select Color')
		if c[1]:
			self.mark_edited()
			self.canvas.itemconfigure(i+1, fill=c[1], outline=c[1])
			self.palette.palette[i] = c[0]

	def copy(self, key: Event | None = None) -> None:
		if not self.palette or self.selected is None:
			return
		self.clipboard_clear()
		self.clipboard_append('#%02X%02X%02X' % tuple(self.palette.palette[self.selected]))

	def canpaste(self, c: str | None = None) -> (RGB | None):
		try:
			if c is None:
				c = self.selection_get(selection='CLIPBOARD')
		except:
			pass
		else:
			m = re.match(r'^#([\dA-Fa-f]{2})([\dA-Fa-f]{2})([\dA-Fa-f]{2})$', c)
			if m:
				return (int(m.group(1), 16), int(m.group(2), 16), int(m.group(3), 16))
		return None

	def paste(self, key=None):
		if not self.palette or self.selected is None:
			return
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

	def update_title(self) -> None:
		file_path = self.file
		if not file_path and self.is_file_open():
			file_path = 'Untitled.pal'
		if not file_path:
			self.title('PyPAL %s' % LONG_VERSION)
		else:
			self.title('PyPAL %s (%s)' % (LONG_VERSION, file_path))

	def mark_edited(self, edited: bool = True) -> None:
		self.edited = edited
		self.editstatus['state'] = NORMAL if edited else DISABLED

	def new(self) -> None:
		if self.check_saved() == CheckSaved.cancelled:
			return
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

	def open(self, file: str | None = None) -> None:
		if self.check_saved() == CheckSaved.cancelled:
			return
		if file is None:
			file = self.config_.last_path.pal.select_open(self)
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

	def save(self) -> CheckSaved:
		return self.saveas(file_path=self.file, file_format=self.format)

	def saveas(self, file_path: str | None = None, file_format: Palette.Format | None = None, file_type: Palette.FileType = Palette.FileType.sc_pal) -> CheckSaved:
		if not self.palette:
			return CheckSaved.saved
		if not file_path:
			file_path = self.config_.last_path.pal.select_save(self)
			if not file_path:
				return CheckSaved.cancelled
		elif not check_allow_overwrite_internal_file(file_path):
			return CheckSaved.cancelled
		if not file_format:
			file_format = file_type.format
		try:
			self.palette.save(file_path, file_format)
		except PyMSError as e:
			ErrorDialog(self, e)
			return CheckSaved.cancelled
		self.status.set('Save Successful!')
		self.mark_edited(False)
		self.file = file_path
		self.format = file_format
		self.update_title()
		self.action_states()
		return CheckSaved.saved

	def close(self) -> None:
		if not self.is_file_open():
			return
		if self.check_saved() == CheckSaved.cancelled:
			return
		self.palette = None
		self.file = None
		self.update_title()
		self.status.set('Load or create a palette.')
		self.mark_edited(False)
		self.selected = None
		self.canvas.coords(self.sel, 0, 0, 0, 0)
		self.update()
		self.action_states()

	def register_registry(self) -> None:
		for type,ext in [('','pal'),('Tileset ','wpe')]:
			try:
				register_registry('PyPAL', ext, type + 'Palette')
			except PyMSError as e:
				ErrorDialog(self, e)
				break

	def sets(self) -> None:
		SettingsDialog(self, self.config_)

	def help(self) -> None:
		HelpDialog(self, self.config_.windows.help, 'Help/Programs/PyPAL.md')

	def about(self) -> None:
		AboutDialog(self, 'PyPAL', LONG_VERSION)

	def exit(self) -> None:
		if self.check_saved() == CheckSaved.cancelled:
			return
		self.config_.windows.main.save(self)
		self.config_.save()
		self.destroy()
