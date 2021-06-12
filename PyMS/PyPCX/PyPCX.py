
from ..FileFormats.PCX import PCX
from ..FileFormats.Palette import Palette
from ..FileFormats.GRP import frame_to_photo
from ..FileFormats.BMP import BMP

from ..Utilities.utils import BASE_DIR, VERSIONS, WIN_REG_AVAILABLE, register_registry
from ..Utilities.UIKit import *
from ..Utilities.analytics import ga, GAScreen
from ..Utilities.trace import setup_trace
from ..Utilities.Settings import Settings
from ..Utilities.Toolbar import Toolbar
from ..Utilities.UpdateDialog import UpdateDialog
from ..Utilities.PyMSError import PyMSError
from ..Utilities.ErrorDialog import ErrorDialog
from ..Utilities.AboutDialog import AboutDialog
from ..Utilities.StatusBar import StatusBar

import os, webbrowser

LONG_VERSION = 'v%s' % VERSIONS['PyPCX']

class PyPCX(MainWindow):
	def __init__(self, guifile=None):
		self.settings = Settings('PyPCX', '1')

		#Window
		MainWindow.__init__(self)
		self.title('PyPCX %s' % LONG_VERSION)
		self.set_icon('PyPCX')
		self.protocol('WM_DELETE_WINDOW', self.exit)
		ga.set_application('PyPCX', VERSIONS['PyPCX'])
		ga.track(GAScreen('PyPCX'))
		setup_trace(self, 'PyPCX')

		self.pcx = None
		self.file = None
		self.edited = False

		#Toolbar
		self.toolbar = Toolbar(self)
		self.toolbar.add_button('open', self.open, 'Open', Ctrl.o)
		self.toolbar.add_button('save', self.save, 'Save', Ctrl.s, enabled=False, tags='file_open')
		self.toolbar.add_button('saveas', self.saveas, 'Save As', Ctrl.Alt.a, enabled=False, tags='file_open')
		self.toolbar.add_button('close', self.close, 'Close', Ctrl.w, enabled=False, tags='file_open')
		self.toolbar.add_gap()
		self.toolbar.add_button('exportc', self.export, 'Export as BMP', Ctrl.e, enabled=False, tags='file_open')
		self.toolbar.add_button('importc', self.iimport, 'Import BMP', Ctrl.i),
		self.toolbar.add_section()
		self.toolbar.add_button('colors', self.loadpal, 'Import a palette', Ctrl.Alt.i, enabled=False, tags='file_open')
		self.toolbar.add_button('saveriff', lambda: self.savepal(file_type=Palette.FileType.riff), 'Save Palette as RIFF *.pal', Ctrl.r, enabled=False, tags='file_open')
		self.toolbar.add_button('savejasc', lambda: self.savepal(file_type=Palette.FileType.jasc), 'Save Palette as JASC *.pal', Ctrl.j, enabled=False, tags='file_open')
		self.toolbar.add_button('savepal', lambda: self.savepal(file_type=Palette.FileType.sc_pal), 'Save Palette as StarCraft *.pal', Ctrl.p, enabled=False, tags='file_open')
		self.toolbar.add_button('savewpe', lambda: self.savepal(file_type=Palette.FileType.wpe), 'Save Palette as StarCraft Terrain *.wpe', Ctrl.t, enabled=False, tags='file_open')
		self.toolbar.add_button('saveact', lambda: self.savepal(file_type=Palette.FileType.act), 'Save as Adobe Color Table *.act', Ctrl.a, enabled=False, tags='file_open')
		self.toolbar.add_section()
		self.toolbar.add_button('register', self.register, 'Set as default *.pcx editor (Windows Only)', enabled=WIN_REG_AVAILABLE)
		self.toolbar.add_button('help', self.help, 'Help', Key.F1)
		self.toolbar.add_button('about', self.about, 'About PyPCX')
		self.toolbar.add_section()
		self.toolbar.add_button('exit', self.exit, 'Exit', Alt.F4)
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
		self.editstatus = statusbar.add_icon(PhotoImage(file=os.path.join(BASE_DIR,'PyMS','Images','save.gif')))
		statusbar.add_spacer()

		self.settings.windows.load_window_size('main', self)

		if guifile:
			self.open(file=guifile)

		UpdateDialog.check_update(self, 'PyPCX')

	def is_file_open(self):
		return not not self.pcx

	def action_states(self):
		self.toolbar.tag_enabled('file_open', self.is_file_open())
		self.editstatus['state'] = NORMAL if self.edited else DISABLED

	def preview(self):
		self.canvas.config(width=self.pcx.width,height=self.pcx.height)
		self.canvas.pack(side=TOP)
		self.canvas.pcx = frame_to_photo(self.pcx.palette, self.pcx, -1, size=False, trans=False)
		self.canvas.create_image(0, 0, image=self.canvas.pcx, anchor=NW)
		self.action_states()

	def unsaved(self):
		if self.pcx and self.edited:
			file = self.file
			if not file:
				file = 'Unnamed.pcx'
			save = MessageBox.askquestion(parent=self, title='Save Changes?', message="Save changes to '%s'?" % file, default=MessageBox.YES, type=MessageBox.YESNOCANCEL)
			if save != MessageBox.NO:
				if save == MessageBox.CANCEL:
					return True
				if self.file:
					self.save()
				else:
					self.saveas()

	def open(self, key=None, file=None):
		if self.unsaved():
			return
		if file == None:
			file = self.settings.lastpath.pcx.select_open_file(self, title='Open PCX', filetypes=(('StarCraft PCX','*.pcx'),))
			if not file:
				return
		pcx = PCX()
		try:
			pcx.load_file(file)
		except PyMSError, e:
			ErrorDialog(self, e)
			return
		self.pcx = pcx
		self.title('PyPCX %s (%s)' % (LONG_VERSION,file))
		self.file = file
		self.edited = False
		self.status.set('Load Successful!')
		self.preview()

	def save(self, key=None):
		if not self.is_file_open():
			return
		if self.file == None:
			self.saveas()
			return
		try:
			self.pcx.save_file(self.file)
		except PyMSError, e:
			ErrorDialog(self, e)
			return
		self.edited = False
		self.status.set('Save Successful!')
		self.action_states()

	def saveas(self, key=None, type=0):
		if not self.is_file_open():
			return
		file = self.settings.lastpath.pcx.select_save_file(self, title='Save PCX As', filetypes=(('StarCraft PCX','*.pcx'),))
		if not file:
			return True
		self.file = file
		self.title('PyPCX %s (%s)' % (LONG_VERSION,self.file))
		self.save()

	def loadpal(self, key=None):
		if not self.is_file_open():
			return
		file = self.settings.lastpath.pal.select_open_file(self, key='import', title='Import Palette', filetypes=Palette.FileType.load_types())
		if not file:
			return True
		pal = Palette()
		try:
			pal.load_file(file)
		except PyMSError, e:
			ErrorDialog(self, e)
			return
		self.pcx.palette = list(pal.palette)
		self.edited = True
		self.preview()

	def savepal(self, key=None, file_type=Palette.FileType.sc_pal):
		if not self.is_file_open():
			return
		file = self.settings.lastpath.pal.select_save_file(self, key='export', title='Save Palette As', filetypes=Palette.FileType.save_types(file_type.format, file_type.ext))
		if not file:
			return True
		p = Palette()
		p.palette = list(self.pcx.palette)
		try:
			p.save(file, file_type.format)
			self.status.set('Palette saved successfully!')
		except PyMSError, e:
			ErrorDialog(self, e)

	def export(self, key=None):
		if not self.is_file_open():
			return
		file = self.settings.lastpath.bmp.select_save_file(self, key='export', title='Export to BMP', filetypes=(('256 Color BMP','*.bmp'),))
		if not file:
			return True
		b = BMP()
		b.set_pixels(self.pcx.image,self.pcx.palette)
		try:
			b.save_file(file)
		except PyMSError, e:
			ErrorDialog(self, e)
			return
		self.status.set('Image exported successfully!')

	def iimport(self, key=None):
		if not self.is_file_open():
			return
		file = self.settings.lastpath.bmp.select_open_file(self, key='import', title='Import a BMP', filetypes=(('256 Color BMP','*.bmp'),))
		if not file:
			return True
		b = BMP()
		try:
			b.load_file(file)
		except PyMSError, e:
			ErrorDialog(self, e)
			return
		if not self.pcx:
			self.pcx = PCX()
			self.file = 'Unnamed.pcx'
			self.title('PyPCX %s (%s)' % (LONG_VERSION,self.file))
		self.pcx.load_data(b.image,b.palette)
		self.edited = False
		self.preview()
		self.status.set('Image imported successfully!')

	def close(self, key=None):
		if self.unsaved():
			return
		if not self.is_file_open():
			return
		self.pcx = None
		self.title('PyPCX %s' % LONG_VERSION)
		self.file = None
		self.status.set('Load a PCX or import a BMP.')
		self.canvas.delete(ALL)
		self.canvas.forget()
		self.canvas.pcx = None
		self.action_states()

	def register(self, e=None):
		try:
			register_registry('PyPCX','StarCraft PCX','pcx',os.path.join(BASE_DIR, 'PyPCX.pyw'),os.path.join(BASE_DIR,'PyMS','Images','PyPCX.ico'))
		except PyMSError, e:
			ErrorDialog(self, e)

	def help(self, e=None):
		webbrowser.open('file:///%s' % os.path.join(BASE_DIR, 'Docs', 'PyPCX.html'))

	def about(self, key=None):
		AboutDialog(self, 'PyPCX', LONG_VERSION)

	def exit(self, e=None):
		if self.unsaved():
			return
		self.settings.windows.save_window_size('main', self)
		self.settings.save()
		self.destroy()
