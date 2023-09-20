
from .Config import PyPCXConfig
from .SettingsDialog import SettingsDialog

from ..FileFormats.PCX import PCX
from ..FileFormats.Palette import Palette
from ..FileFormats.GRP import frame_to_photo
from ..FileFormats.BMP import BMP

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

from typing import cast

LONG_VERSION = 'v%s' % Assets.version('PyPCX')

class PyPCX(MainWindow):
	def __init__(self, guifile: str | None = None) -> None:
		#Window
		MainWindow.__init__(self)
		self.set_icon('PyPCX')
		self.protocol('WM_DELETE_WINDOW', self.exit)
		ga.set_application('PyPCX', Assets.version('PyPCX'))
		ga.track(GAScreen('PyPCX'))
		setup_trace('PyPCX', self)
		
		self.config_ = PyPCXConfig()
		Theme.load_theme(self.config_.theme.value, self)

		self.pcx: PCX | None = None
		self.file: str | None = None
		self.image: Image | None = None
		self.edited = False

		self.update_title()

		#Toolbar
		self.toolbar = Toolbar(self)
		self.toolbar.add_button(Assets.get_image('open'), self.open, 'Open', Ctrl.o)
		def save():
			self.save()
		self.toolbar.add_button(Assets.get_image('save'), save, 'Save', Ctrl.s, enabled=False, tags='file_open')
		def saveas():
			self.saveas()
		self.toolbar.add_button(Assets.get_image('saveas'), saveas, 'Save As', Ctrl.Alt.a, enabled=False, tags='file_open')
		self.toolbar.add_button(Assets.get_image('close'), self.close, 'Close', Ctrl.w, enabled=False, tags='file_open')
		self.toolbar.add_gap()
		self.toolbar.add_button(Assets.get_image('exportc'), self.export, 'Export as BMP', Ctrl.e, enabled=False, tags='file_open')
		self.toolbar.add_button(Assets.get_image('importc'), self.iimport, 'Import BMP', Ctrl.i),
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('colors'), self.loadpal, 'Import a palette', Ctrl.Alt.i, enabled=False, tags='file_open')
		self.toolbar.add_button(Assets.get_image('saveriff'), lambda: self.savepal(file_type=Palette.FileType.riff), 'Save Palette as RIFF *.pal', Ctrl.r, enabled=False, tags='file_open')
		self.toolbar.add_button(Assets.get_image('savejasc'), lambda: self.savepal(file_type=Palette.FileType.jasc), 'Save Palette as JASC *.pal', Ctrl.j, enabled=False, tags='file_open')
		self.toolbar.add_button(Assets.get_image('savepal'), lambda: self.savepal(file_type=Palette.FileType.sc_pal), 'Save Palette as StarCraft *.pal', Ctrl.p, enabled=False, tags='file_open')
		self.toolbar.add_button(Assets.get_image('savewpe'), lambda: self.savepal(file_type=Palette.FileType.wpe), 'Save Palette as StarCraft Terrain *.wpe', Ctrl.t, enabled=False, tags='file_open')
		self.toolbar.add_button(Assets.get_image('saveact'), lambda: self.savepal(file_type=Palette.FileType.act), 'Save as Adobe Color Table *.act', Ctrl.a, enabled=False, tags='file_open')
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('asc3topyai'), self.sets, "Manage Settings", Ctrl.m)
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('register'), self.register_registry, 'Set as default *.pcx editor (Windows Only)', enabled=WIN_REG_AVAILABLE)
		self.toolbar.add_button(Assets.get_image('help'), self.help, 'Help', Key.F1)
		self.toolbar.add_button(Assets.get_image('about'), self.about, 'About PyPCX')
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('exit'), self.exit, 'Exit', Shortcut.Exit)
		self.toolbar.pack(side=TOP, padx=1, pady=1, fill=X)

		#Canvas
		f = Frame(self, bd=2, relief=SUNKEN, background='#808080')
		l = Frame(f, background='#808080')
		self.canvas = Canvas(l, width=0, height=0, bd=0, highlightthickness=0)
		l.pack(side=LEFT, fill=Y, padx=2, pady=2)
		f.pack(fill=BOTH, expand=1, padx=5, pady=5)

		#Statusbar
		self.status = StringVar()
		self.status.set('Load a PCX or import a BMP.')
		statusbar = StatusBar(self)
		statusbar.add_label(self.status, weight=0.6)
		self.editstatus = statusbar.add_icon(Assets.get_image('save'))
		statusbar.add_spacer()

		self.config_.windows.main.load_size(self)

		if guifile:
			self.open(file=guifile)

		UpdateDialog.check_update(self, 'PyPCX')

	def is_file_open(self) -> bool:
		return not not self.pcx

	def action_states(self) -> None:
		self.toolbar.tag_enabled('file_open', self.is_file_open())
		self.editstatus['state'] = NORMAL if self.edited else DISABLED

	def preview(self) -> None:
		if not self.pcx:
			return
		self.canvas.config(width=self.pcx.width,height=self.pcx.height)
		self.canvas.pack(side=TOP)
		self.image = cast(Image, frame_to_photo(self.pcx.palette, self.pcx, -1, size=False, trans=False))
		self.canvas.create_image(0, 0, image=self.image, anchor=NW)
		self.action_states()

	def check_saved(self) -> CheckSaved:
		if not self.pcx or not self.edited:
			return CheckSaved.saved
		file = self.file
		if not file:
			file = 'Unnamed.pcx'
		save = MessageBox.askquestion(parent=self, title='Save Changes?', message="Save changes to '%s'?" % file, default=MessageBox.YES, type=MessageBox.YESNOCANCEL)
		if save == MessageBox.NO:
			return CheckSaved.saved
		elif save == MessageBox.CANCEL:
			return CheckSaved.cancelled
		if self.file:
			return self.save()
		else:
			return self.saveas()

	def update_title(self) -> None:
		file_path = self.file
		if not file_path and self.is_file_open():
			file_path = 'Untitled.pcx'
		if not file_path:
			self.title('PyPCX %s' % LONG_VERSION)
		else:
			self.title('PyPCX %s (%s)' % (LONG_VERSION, file_path))

	def open(self, file: str | None = None) -> None:
		if self.check_saved() == CheckSaved.cancelled:
			return
		if file is None:
			file = self.config_.last_path.pcx.select_open(self)
			if not file:
				return
		pcx = PCX()
		try:
			pcx.load_file(file)
		except PyMSError as e:
			ErrorDialog(self, e)
			return
		self.pcx = pcx
		self.file = file
		self.update_title()
		self.edited = False
		self.status.set('Load Successful!')
		self.preview()

	def save(self) -> CheckSaved:
		return self.saveas(file_path=self.file)

	def saveas(self, file_path: str | None = None) -> CheckSaved:
		if not self.pcx:
			return CheckSaved.saved
		if not file_path:
			file_path = self.config_.last_path.pcx.select_save(self)
			if not file_path:
				return CheckSaved.cancelled
		elif not check_allow_overwrite_internal_file(file_path):
			return CheckSaved.cancelled
		try:
			self.pcx.save_file(file_path)
		except PyMSError as e:
			ErrorDialog(self, e)
			return CheckSaved.cancelled
		self.edited = False
		self.status.set('Save Successful!')
		self.action_states()
		self.file = file_path
		self.update_title()
		return CheckSaved.saved

	def loadpal(self) -> None:
		if not self.pcx:
			return
		file = self.config_.last_path.pal.select_open(self)
		if not file:
			return
		pal = Palette()
		try:
			pal.load_file(file)
		except PyMSError as e:
			ErrorDialog(self, e)
			return
		self.pcx.palette = list(pal.palette)
		self.edited = True
		self.preview()

	def savepal(self, file_type: Palette.FileType = Palette.FileType.sc_pal) -> None:
		if not self.pcx:
			return
		file = self.config_.last_path.pal.select_save(self, filetypes=list(Palette.FileType.save_types(file_type.format, file_type.ext)))
		if not file:
			return
		p = Palette()
		p.palette = list(self.pcx.palette)
		try:
			p.save(file, file_type.format)
			self.status.set('Palette saved successfully!')
		except PyMSError as e:
			ErrorDialog(self, e)

	def export(self) -> None:
		if not self.pcx:
			return
		file = self.config_.last_path.bmp.select_save(self)
		if not file:
			return
		b = BMP()
		b.set_pixels(self.pcx.image,self.pcx.palette)
		try:
			b.save_file(file)
		except PyMSError as e:
			ErrorDialog(self, e)
			return
		self.status.set('Image exported successfully!')

	def iimport(self) -> None:
		if self.check_saved() == CheckSaved.cancelled:
			return
		file = self.config_.last_path.bmp.select_open(self)
		if not file:
			return
		b = BMP()
		try:
			b.load_file(file)
		except PyMSError as e:
			ErrorDialog(self, e)
			return
		if not self.pcx:
			self.pcx = PCX()
			self.file = 'Unnamed.pcx'
			self.update_title()
		self.pcx.load_pixels(b.image,b.palette)
		self.edited = False
		self.preview()
		self.status.set('Image imported successfully!')

	def close(self) -> None:
		if self.check_saved() == CheckSaved.cancelled:
			return
		self.pcx = None
		self.file = None
		self.update_title()
		self.status.set('Load a PCX or import a BMP.')
		self.canvas.delete(ALL)
		self.canvas.forget()
		self.image = None
		self.action_states()

	def register_registry(self) -> None:
		try:
			register_registry('PyPCX', 'pcx')
		except PyMSError as e:
			ErrorDialog(self, e)

	def sets(self) -> None:
		SettingsDialog(self, self.config_)
		# SettingsDialog(self, [('Theme',)], (550,380), err, settings=self.settings)

	def help(self) -> None:
		HelpDialog(self, self.config_.windows.help, 'Help/Programs/PyPCX.md')

	def about(self) -> None:
		AboutDialog(self, 'PyPCX', LONG_VERSION)

	def exit(self) -> None:
		if self.check_saved() == CheckSaved.cancelled:
			return
		self.config_.windows.main.save_size(self)
		self.config_.save()
		self.destroy()
