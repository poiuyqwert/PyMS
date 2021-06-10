
from ..FileFormats import Palette
from ..FileFormats import BMP

from ..Utilities.utils import VERSIONS, BASE_DIR, WIN_REG_AVAILABLE, register_registry
from ..Utilities.UIKit import *
from ..Utilities.Settings import Settings
from ..Utilities.analytics import ga, GAScreen
from ..Utilities.trace import setup_trace
from ..Utilities.Toolbar import Toolbar
from ..Utilities.UpdateDialog import UpdateDialog
from ..Utilities.PyMSError import PyMSError
from ..Utilities.ErrorDialog import ErrorDialog
from ..Utilities.AboutDialog import AboutDialog

import os, webbrowser

LONG_VERSION = 'v%s' % VERSIONS['PyPAL']

class PyPAL(MainWindow):
	def __init__(self, guifile=None):
		#Config
		self.settings = Settings('PyPAL', '1')

		#Window
		MainWindow.__init__(self)
		self.title('PyPAL %s' % LONG_VERSION)
		self.set_icon('PyPAL')
		self.protocol('WM_DELETE_WINDOW', self.exit)
		ga.set_application('PyPAL', VERSIONS['PyPAL'])
		ga.track(GAScreen('PyPAL'))
		setup_trace(self, 'PyPAL')
		self.resizable(False, False)

		self.palette = None
		self.file = None
		self.type = None
		self.edited = False
		self.selected = None

		#Toolbar
		self.toolbar = Toolbar(self)
		self.toolbar.add_button('new', self.new, 'New', Ctrl.n)
		self.toolbar.add_button('open', self.open, 'Open', Ctrl.o)
		self.toolbar.add_button('save', self.save, 'Save', Ctrl.s, enabled=False, identifier='save', tags='file_open')
		self.toolbar.add_button('saveriff', lambda: self.saveas(type=0), 'Save as RIFF *.pal', Ctrl.r, enabled=False, tags='file_open')
		self.toolbar.add_button('savejasc', lambda: self.saveas(type=1), 'Save as JASC *.pal', Ctrl.j, enabled=False, tags='file_open')
		self.toolbar.add_button('savepal', lambda: self.saveas(type=2), 'Save as StarCraft *.pal', Ctrl.p, enabled=False, tags='file_open')
		self.toolbar.add_button('savewpe', lambda: self.saveas(type=3), 'Save as StarCraft Terrain *.wpe', Ctrl.t, enabled=False, tags='file_open')
		self.toolbar.add_button('close', self.close, 'Close', Ctrl.w, enabled=False, tags='file_open')
		self.toolbar.add_section()
		self.toolbar.add_button('register', self.register, 'Set as default *.pal and *.wpe editor (Windows Only)', enabled=WIN_REG_AVAILABLE)
		self.toolbar.add_button('help', self.help, 'Help', Key.F1)
		self.toolbar.add_button('about', self.about, 'About PyPAL')
		self.toolbar.add_section()
		self.toolbar.add_button('exit', self.exit, 'Exit', Alt.F4)
		self.toolbar.pack(side=TOP, padx=1, pady=1, fill=X)

		self.palmenu = Menu(self, tearoff=0)
		self.palmenu.add_command(label='Copy', command=self.copy, shortcut=Ctrl.c)
		self.palmenu.add_command(label='Paste', command=self.paste, shortcut=Ctrl.p, tags='paste')

		#Canvas
		self.canvas = Canvas(self, width=273, height=273, background='#000000', coordinate_adjust=Canvas.coordinate_adjust_os)
		self.canvas.pack(padx=2, pady=2)
		for n in range(256):
			x,y = 3+17*(n%16),3+17*(n/16)
			self.canvas.create_rectangle(x, y, x+15, y+15, fill='#000000', outline='#000000')
			self.canvas.tag_bind(n+1, Cursor.Enter, lambda e,i=n: self.colorstatus(e,i))
			self.canvas.tag_bind(n+1, Cursor.Leave, lambda e,i=-1: self.colorstatus(e,i))
			self.canvas.tag_bind(n+1, Mouse.Left_Click, lambda e,i=n: self.select(e,i))
			self.canvas.tag_bind(n+1, Double.Left_Click, lambda e,i=n: self.changecolor(e,i))
			self.canvas.tag_bind(n+1, ButtonRelease.Right_Click, lambda e,i=n: self.popup(e,i))
		self.sel = self.canvas.create_rectangle(0,0,0,0,outline='#FFFFFF')

		#Statusbar
		self.status = StringVar()
		statusbar = Frame(self)
		Label(statusbar, textvariable=self.status, bd=1, relief=SUNKEN, width=40, anchor=W).pack(side=LEFT, padx=1)
		image = PhotoImage(file=os.path.join(BASE_DIR,'PyMS','Images','save.gif'))
		self.editstatus = Label(statusbar, image=image, bd=0, state=DISABLED)
		self.editstatus.image = image
		self.editstatus.pack(side=LEFT, padx=1, fill=Y)
		Label(statusbar, bd=1, relief=SUNKEN, anchor=W).pack(side=LEFT, expand=1, padx=1, fill=X)
		self.status.set('Load or create a Palette.')
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
			x,y = 2+17*(i%16),2+17*(i/16)
			self.canvas.coords(self.sel, x, y, x+17, y+17)

	def changecolor(self, e, i):
		if self.palette:
			self.select(None,i)
			c = ColorChooser.askcolor(parent=self, initialcolor='#%02X%02X%02X' % tuple(self.palette.palette[i]), title='Select Color')
			if c[1]:
				self.edited = True
				self.editstatus['state'] = NORMAL
				self.canvas.itemconfigure(i+1, fill=c[1], outline=c[1])
				self.palette.palette[i] = c[0]

	def copy(self, key=None):
		if self.palette and self.selected != None:
			self.clipboard_clear()
			self.clipboard_append('#%02X%02X%02X' % tuple(self.palette.palette[self.selected]))

	def canpaste(self, c=None):
		try:
			if c == None:
				c = self.selection_get(selection='CLIPBOARD')
		except:
			pass
		else:
			m = re.match(r'^#([\dA-Fa-f]{2})([\dA-Fa-f]{2})([\dA-Fa-f]{2})$', c)
			if m:
				return [int(c,16) for c in m.groups()]

	def paste(self, key=None):
		if self.palette and self.selected != None:
			try:
				c = self.selection_get(selection='CLIPBOARD')
			except:
				pass
			else:
				rgb = self.canpaste(c)
				if rgb:
					self.palette.palette[self.selected] = rgb
					self.canvas.itemconfigure(self.selected+1, fill=c, outline=c)
					self.edited = True
					self.editstatus['state'] = NORMAL

	def new(self, key=None):
		if not self.unsaved():
			self.palette = Palette.Palette()
			self.file = None
			self.type = None
			self.status.set('Editing new Palette.')
			self.edited = False
			self.editstatus['state'] = DISABLED
			self.title('PyPAL %s (Unnamed.pal)' % LONG_VERSION)
			if self.selected == None:
				self.selected = 0
				self.select(None,0)
			self.update()
			self.action_states()
			self.colorstatus(None, 0)

	def open(self, key=None, file=None):
		if not self.unsaved():
			if file == None:
				file = self.settings.lastpath.select_file('open', self, 'Open Palette', '.pal', [('RIFF, JASC, and StarCraft PAL','*.pal'),('StarCraft Tileset WPE','*.wpe'),('ZSoft PCX','*.pcx'),('8-Bit BMP','*.bmp'),('All Files','*')])
				if not file:
					return
			pal = Palette.Palette()
			try:
				pal.load_file(file)
				self.type = pal.type
			except PyMSError, e:
				bmp = BMP.BMP()
				try:
					bmp.load_file(file)
				except PyMSError:
					ErrorDialog(self, e)
					return
				pal.palette = bmp.palette
				self.type = None
			self.palette = pal
			self.title('PyPAL %s (%s)' % (LONG_VERSION,file))
			self.file = file
			self.status.set('Load Successful!')
			self.edited = False
			self.editstatus['state'] = DISABLED
			if self.selected == None:
				self.selected = 0
				self.select(None,0)
			self.update()
			self.action_states()
			self.colorstatus(None, 0)

	def save(self, key=None):
		if not self.is_file_open() or not self.type:
			return
		if self.file == None:
			self.saveas()
			return
		try:
			[self.palette.save_riff_pal,self.palette.save_jasc_pal,self.palette.save_sc_pal,self.palette.save_sc_wpe][self.type](self.file)
			self.status.set('Save Successful!')
			self.edited = False
			self.editstatus['state'] = DISABLED
		except PyMSError, e:
			ErrorDialog(self, e)

	def saveas(self, key=None, type=0):
		if not self.is_file_open():
			return
		types = [(('RIFF PAL','*.pal'),('JASC PAL','*.pal'),('StarCraft PAL','*.pal'),('StarCraft Terrain WPE','*.wpe'))[type]]
		types.append(('All Files','*'))
		file = self.settings.lastpath.select_file('save', self, 'Save Palette As', types[0][1], filetypes=types, save=True)
		if not file:
			return True
		self.file = file
		self.title('PyPAL %s (%s)' % (LONG_VERSION,self.file))
		self.type = type
		self.save()
		self.action_states()

	def close(self, key=None):
		if not self.is_file_open():
			return
		if not self.unsaved():
			self.palette = None
			self.title('PyPAL %s' % LONG_VERSION)
			self.file = None
			self.status.set('Load or create a palette.')
			self.edited = False
			self.editstatus['state'] = DISABLED
			self.selected = None
			self.canvas.coords(self.sel, 0, 0, 0, 0)
			self.update()
			self.action_states()

	def register(self, e=None):
		for type,ext in [('','pal'),('Tileset ','wpe')]:
			try:
				register_registry('PyPAL',type + 'Palette',ext,os.path.join(BASE_DIR, 'PyPAL.pyw'),os.path.join(BASE_DIR,'PyMS','Images','PyPAL.ico'))
			except PyMSError, e:
				ErrorDialog(self, e)
				break

	def help(self, e=None):
		webbrowser.open('file:///%s' % os.path.join(BASE_DIR, 'Docs', 'PyPAL.html'))

	def about(self, key=None):
		AboutDialog(self, 'PyPAL', LONG_VERSION)

	def exit(self, e=None):
		if not self.unsaved():
			self.settings.windows.save_window_size('main', self)
			self.settings.save()
			self.destroy()
