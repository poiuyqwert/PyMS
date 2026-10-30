
from .Config import PyPCXConfig
from .SettingsDialog import SettingsDialog

from ..FileFormats.PCX import PCX
from ..FileFormats.Palette import Palette
from ..FileFormats.GRP import frame_to_photo
from ..FileFormats.BMP import BMP

from ..Utilities import registry
from ..Utilities import UIKit as UI
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
from ..Utilities.SponsorDialog import SponsorDialog


LONG_VERSION = 'v' + Assets.version('PyPCX')

class PyPCX(UI.MainWindow):
	def __init__(self, guifile: str | None = None) -> None:
		#Window
		UI.MainWindow.__init__(self)
		self.set_icon('PyPCX')
		self.protocol('WM_DELETE_WINDOW', self.exit)
		ga.set_application('PyPCX', Assets.version('PyPCX'))
		ga.track(GAScreen('PyPCX'))
		setup_trace('PyPCX', self)

		self.config_ = PyPCXConfig()
		UI.Theme.load_theme(self.config_.theme.value, self)

		self.pcx: PCX | None = None
		self.file: str | None = None
		self.image: UI.AnyPhotoImage | None = None
		self.canvas_image: UI.Canvas.Item | None = None
		self.edited = False

		self.update_title()

		def save() -> None:
			self.save()
		def saveas() -> None:
			self.saveas()

		#Menu
		self.menu = UI.Menu(self)
		self.config(menu=self.menu)

		file_menu = self.menu.add_cascade('File')
		file_menu.add_command('Open...', self.open, UI.Ctrl.o)
		file_menu.add_separator()
		file_menu.add_command('Save', save, UI.Ctrl.s, enabled=False, tags='file_open')
		file_menu.add_command('Save As...', saveas, UI.Ctrl.Alt.a, enabled=False, tags='file_open', underline='As')
		file_menu.add_separator()
		file_menu.add_command('Import BMP...', self.iimport, UI.Ctrl.i)
		file_menu.add_command('Export BMP...', self.export, UI.Ctrl.e, enabled=False, tags='file_open')
		file_menu.add_separator()
		file_menu.add_command('Close', self.close, UI.Ctrl.w, enabled=False, tags='file_open', underline='c')
		file_menu.add_separator()
		file_menu.add_command('Check for Updates...', self.check_for_updates, underline='u')
		file_menu.add_separator()
		file_menu.add_command('Exit', self.exit, UI.Shortcut.Exit, underline='x')

		palette_menu = self.menu.add_cascade('Palette')
		palette_menu.add_command('Import Palette...', self.loadpal, UI.Ctrl.Alt.i, enabled=False, tags='file_open')
		palette_menu.add_separator()
		save_palette_menu = palette_menu.add_cascade('Save Palette As')
		save_palette_menu.add_command('RIFF *.pal...', lambda: self.savepal(file_type=Palette.FileType.riff), UI.Ctrl.r, enabled=False, tags='file_open')
		save_palette_menu.add_command('JASC *.pal...', lambda: self.savepal(file_type=Palette.FileType.jasc), UI.Ctrl.j, enabled=False, tags='file_open')
		save_palette_menu.add_command('StarCraft *.pal...', lambda: self.savepal(file_type=Palette.FileType.sc_pal), UI.Ctrl.p, enabled=False, tags='file_open')
		save_palette_menu.add_command('StarCraft Terrain *.wpe...', lambda: self.savepal(file_type=Palette.FileType.wpe), UI.Ctrl.t, enabled=False, tags='file_open')
		save_palette_menu.add_command('Adobe Color Table *.act...', lambda: self.savepal(file_type=Palette.FileType.act), UI.Ctrl.a, enabled=False, tags='file_open')

		settings_menu = self.menu.add_cascade('Settings')
		settings_menu.add_command('Manage Settings...', self.sets, UI.Ctrl.m)
		settings_menu.add_separator()
		settings_menu.add_command('Set as Default *.pcx Editor (Windows Only)', self.register_registry, enabled=registry.IS_AVAILABLE, underline='D')

		help_menu = self.menu.add_cascade('Help')
		help_menu.add_command('View Help', self.help, UI.Key.F1, underline='H')
		help_menu.add_separator()
		help_menu.add_command('Donate...', self.sponsor, underline='D')
		help_menu.add_command('About PyPCX', self.about, underline='A')

		#Toolbar
		self.toolbar = UI.Toolbar(self)
		self.toolbar.add_button(Assets.get_image('open'), self.open, 'Open', UI.Ctrl.o, bind_shortcut=False)
		self.toolbar.add_gap()
		self.toolbar.add_button(Assets.get_image('save'), save, 'Save', UI.Ctrl.s, enabled=False, tags='file_open', bind_shortcut=False)
		self.toolbar.add_button(Assets.get_image('saveas'), saveas, 'Save As', UI.Ctrl.Alt.a, enabled=False, tags='file_open', bind_shortcut=False)
		self.toolbar.add_gap()
		self.toolbar.add_button(Assets.get_image('importc'), self.iimport, 'Import BMP', UI.Ctrl.i, bind_shortcut=False)
		self.toolbar.add_button(Assets.get_image('exportc'), self.export, 'Export BMP', UI.Ctrl.e, enabled=False, tags='file_open', bind_shortcut=False)
		self.toolbar.add_gap()
		self.toolbar.add_button(Assets.get_image('close'), self.close, 'Close', UI.Ctrl.w, enabled=False, tags='file_open', bind_shortcut=False)
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('colors'), self.loadpal, 'Import Palette', UI.Ctrl.Alt.i, enabled=False, tags='file_open', bind_shortcut=False)
		self.toolbar.add_gap()
		self.toolbar.add_button(Assets.get_image('saveriff'), lambda: self.savepal(file_type=Palette.FileType.riff), 'Save Palette as RIFF *.pal', UI.Ctrl.r, enabled=False, tags='file_open', bind_shortcut=False)
		self.toolbar.add_button(Assets.get_image('savejasc'), lambda: self.savepal(file_type=Palette.FileType.jasc), 'Save Palette as JASC *.pal', UI.Ctrl.j, enabled=False, tags='file_open', bind_shortcut=False)
		self.toolbar.add_button(Assets.get_image('savepal'), lambda: self.savepal(file_type=Palette.FileType.sc_pal), 'Save Palette as StarCraft *.pal', UI.Ctrl.p, enabled=False, tags='file_open', bind_shortcut=False)
		self.toolbar.add_button(Assets.get_image('savewpe'), lambda: self.savepal(file_type=Palette.FileType.wpe), 'Save Palette as StarCraft Terrain *.wpe', UI.Ctrl.t, enabled=False, tags='file_open', bind_shortcut=False)
		self.toolbar.add_button(Assets.get_image('saveact'), lambda: self.savepal(file_type=Palette.FileType.act), 'Save Palette as Adobe Color Table *.act', UI.Ctrl.a, enabled=False, tags='file_open', bind_shortcut=False)
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('asc3topyai'), self.sets, 'Manage Settings', UI.Ctrl.m, bind_shortcut=False)
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('register'), self.register_registry, 'Set as Default *.pcx Editor (Windows Only)', enabled=registry.IS_AVAILABLE)
		self.toolbar.add_button(Assets.get_image('help'), self.help, 'View Help', UI.Key.F1, bind_shortcut=False)
		self.toolbar.add_button(Assets.get_image('about'), self.about, 'About PyPCX')
		self.toolbar.add_button(Assets.get_image('money'), self.sponsor, 'Donate')
		self.toolbar.add_button(Assets.get_image('update'), self.check_for_updates, 'Check for Updates')
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('exit'), self.exit, 'Exit', UI.Shortcut.Exit, bind_shortcut=False)
		self.toolbar.pack(side=UI.TOP, padx=1, pady=1, fill=UI.X)

		#Canvas
		f = UI.Frame(self, bd=2, relief=UI.SUNKEN, background='#808080')
		l = UI.Frame(f, background='#808080')
		self.canvas = UI.Canvas(l, width=0, height=0, bd=0, highlightthickness=0)
		l.pack(side=UI.LEFT, fill=UI.Y, padx=2, pady=2)
		f.pack(fill=UI.BOTH, expand=1, padx=5, pady=5)

		#Statusbar
		self.status = UI.StringVar()
		self.status.set('Load a PCX or import a BMP.')
		statusbar = UI.StatusBar(self)
		statusbar.add_label(self.status, weight=0.6)
		self.editstatus = statusbar.add_icon(Assets.get_image('save'))
		statusbar.add_spacer()

		self.config_.windows.main.load_size(self)

		if guifile:
			self.open(file=guifile)

		UpdateDialog.check_update(self, 'PyPCX')

	def is_file_open(self) -> bool:
		return self.pcx is not None

	def action_states(self) -> None:
		self.toolbar.tag_enabled('file_open', self.is_file_open())
		self.menu.tag_enabled('file_open', self.is_file_open())
		self.editstatus['state'] = UI.NORMAL if self.edited else UI.DISABLED

	def mark_edited(self, edited: bool = True) -> None:
		self.edited = edited
		self.action_states()

	def preview(self) -> None:
		if not self.pcx:
			return
		self.canvas.config(width=self.pcx.width,height=self.pcx.height)
		if not self.canvas.winfo_manager():
			self.canvas.pack(side=UI.TOP)
		self.image = frame_to_photo(self.pcx.palette, self.pcx)
		if self.canvas_image is not None:
			self.canvas_image.config(image=self.image)
		else:
			self.canvas_image = self.canvas.create_image(0, 0, image=self.image, anchor=UI.NW)
		self.action_states()

	def check_saved(self) -> CheckSaved:
		if not self.pcx or not self.edited:
			return CheckSaved.saved
		file = self.file
		if not file:
			file = 'Unnamed.pcx'
		save = UI.MessageBox.askyesnocancel(parent=self, title='Save Changes?', message=f"Save changes to '{file}'?", default=UI.MessageBox.YES)
		if save is None:
			return CheckSaved.cancelled
		if not save:
			return CheckSaved.saved
		if self.file:
			return self.save()
		return self.saveas()

	def update_title(self) -> None:
		file_path = self.file
		if not file_path and self.is_file_open():
			file_path = 'Untitled.pcx'
		if not file_path:
			self.title(f'PyPCX {LONG_VERSION}')
		else:
			self.title(f'PyPCX {LONG_VERSION} ({file_path})')

	def open(self, file: str | None = None) -> None:
		if self.check_saved() == CheckSaved.cancelled:
			return
		if file is None:
			file = self.config_.last_path.pcx.select_open(self)
			if not file:
				return
		pcx = PCX()
		try:
			pcx.load(file)
		except PyMSError as e:
			ErrorDialog(self, e)
			return
		self.pcx = pcx
		self.file = file
		self.update_title()
		self.mark_edited(False)
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
			self.pcx.save(file_path)
		except PyMSError as e:
			ErrorDialog(self, e)
			return CheckSaved.cancelled
		self.file = file_path
		self.update_title()
		self.mark_edited(False)
		self.status.set('Save Successful!')
		return CheckSaved.saved

	def loadpal(self) -> None:
		if not self.pcx:
			return
		file = self.config_.last_path.pal.select_open(self)
		if not file:
			return
		pal = Palette()
		try:
			pal.load(file)
		except PyMSError as e:
			ErrorDialog(self, e)
			return
		self.pcx.palette = list(pal.palette)
		self.mark_edited()
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
			b.save(file)
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
			b.load(file)
		except PyMSError as e:
			ErrorDialog(self, e)
			return
		if not self.pcx:
			self.pcx = PCX()
			self.update_title()
		self.pcx.load_pixels(b.image,b.palette)
		self.mark_edited()
		self.preview()
		self.status.set('Image imported successfully!')

	def close(self) -> None:
		if self.check_saved() == CheckSaved.cancelled:
			return
		self.pcx = None
		self.file = None
		self.update_title()
		self.status.set('Load a PCX or import a BMP.')
		self.canvas.delete(UI.ALL)
		self.canvas_image = None
		self.canvas.forget()
		self.image = None
		self.action_states()

	def register_registry(self) -> None:
		try:
			registry.register('PyPCX', 'pcx')
		except PyMSError as e:
			ErrorDialog(self, e)

	def sets(self) -> None:
		SettingsDialog(self, self.config_)

	def help(self) -> None:
		HelpDialog(self, self.config_.windows.help, 'Help/Programs/PyPCX.md')

	def about(self) -> None:
		AboutDialog(self, 'PyPCX', LONG_VERSION)

	def sponsor(self) -> None:
		SponsorDialog(self)

	def check_for_updates(self) -> None:
		UpdateDialog(self, 'PyPCX')

	def exit(self) -> None:
		if self.check_saved() == CheckSaved.cancelled:
			return
		self.config_.windows.main.save_size(self)
		self.config_.save()
		self.destroy()
