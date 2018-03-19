from Libs.utils import *
from Libs.setutils import *
from Libs.trace import setup_trace
from Libs import PCX,BMP,GRP,PAL

from Tkinter import *
from tkMessageBox import *
import tkFileDialog

from thread import start_new_thread
import optparse, os, webbrowser, sys

LONG_VERSION = 'v%s' % VERSIONS['PyPCX']

class PyPCX(Tk):
	def __init__(self, guifile=None):
		self.settings = loadsettings('PyPCX')

		#Window
		Tk.__init__(self)
		self.title('PyPCX %s' % LONG_VERSION)
		try:
			self.icon = os.path.join(BASE_DIR,'Images','PyPCX.ico')
			self.wm_iconbitmap(self.icon)
		except:
			self.icon = '@%s' % os.path.join(BASE_DIR, 'Images','PyPCX.xbm')
			self.wm_iconbitmap(self.icon)
		self.protocol('WM_DELETE_WINDOW', self.exit)
		setup_trace(self, 'PyPCX')

		self.pcx = None
		self.file = None
		self.type = None

		#Toolbar
		buttons = [
			('open', self.open, 'Open (Ctrl+O)', NORMAL, 'Ctrl+O'),
			('save', self.save, 'Save (Ctrl+S)', DISABLED, 'Ctrl+S'),
			('saveas', self.saveas, 'Save As (Ctrl+Alt+A)', DISABLED, 'Ctrl+Alt+A'),
			('close', self.close, 'Close (Ctrl+W)', DISABLED, 'Ctrl+W'),
			4,
			('exportc', self.export, 'Export as BMP (Ctrl+E)', DISABLED, 'Ctrl+E'),
			('importc', self.iimport, 'Import BMP (Ctrl+I)', NORMAL, 'Ctrl+I'),
			10,
			('colors', self.loadpal, 'Import a palette (Ctrl+Alt+I)', DISABLED, 'Ctrl+Alt+I'),
			('saveriff', lambda key=None,i=0: self.savepal(key,type=i), 'Save Palette as RIFF *.pal (Ctrl+R)', DISABLED, 'Ctrl+R'),
			('savejasc', lambda key=None,i=1: self.savepal(key,type=i), 'Save Palette as JASC *.pal (Ctrl+J)', DISABLED, 'Ctrl+J'),
			('savepal', lambda key=None,i=2: self.savepal(key,type=i), 'Save Palette as StarCraft *.pal (Ctrl+P)', DISABLED, 'Ctrl+P'),
			('savewpe', lambda key=None,i=3: self.savepal(key,type=i), 'Save Palette as StarCraft Terrain *.wpe (Ctrl+T)', DISABLED, 'Ctrl+T'),
			10,
			('register', self.register, 'Set as default *.pcx editor (Windows Only)', [DISABLED,NORMAL][win_reg], ''),
			('help', self.help, 'Help (F1)', NORMAL, 'F1'),
			('about', self.about, 'About PyPCX', NORMAL, ''),
			10,
			('exit', self.exit, 'Exit (Alt+F4)', NORMAL, 'Alt+F4'),
		]
		self.buttons = {}
		toolbar = Frame(self)
		for btn in buttons:
			if isinstance(btn, tuple):
				image = PhotoImage(file=os.path.join(BASE_DIR,'Images','%s.gif' % btn[0]))
				button = Button(toolbar, image=image, width=20, height=20, command=btn[1], state=btn[3])
				button.image = image
				button.tooltip = Tooltip(button, btn[2])
				button.pack(side=LEFT)
				self.buttons[btn[0]] = button
				a = btn[4]
				if a:
					if not a.startswith('F'):
						self.bind('<%s%s>' % (a[:-1].replace('Ctrl','Control').replace('+','-'), a[-1].lower()), btn[1])
					else:
						self.bind('<%s>' % a, btn[1])
			else:
				Frame(toolbar, width=btn).pack(side=LEFT)
		toolbar.pack(side=TOP, padx=1, pady=1, fill=X)

		#Canvas
		f = Frame(self, bd=2, relief=SUNKEN, background='#808080')
		l = Frame(f, background='#808080')
		self.canvas = Canvas(l, width=0, height=0, bd=0, highlightthickness=0)
		l.pack(side=LEFT, fill=Y, padx=2, pady=2)
		f.pack(fill=BOTH, expand=1, padx=5, pady=5)

		#Statusbar
		self.status = StringVar()
		statusbar = Frame(self)
		Label(statusbar, textvariable=self.status, bd=1, relief=SUNKEN, anchor=W).pack(side=LEFT, padx=1, fill=X, expand=1)
		self.status.set('Load a PCX or import a BMP.')
		statusbar.pack(side=BOTTOM, fill=X)

		if 'window' in self.settings:
			loadsize(self, self.settings, 'window', True)

		if guifile:
			self.open(file=guifile)

		start_new_thread(check_update, (self, 'PyPCX'))

	def select_file(self, title, open=True, ext='.pcx', filetypes=[('StarCraft PCX','*.pcx'),('All Files','*')]):
		path = self.settings.get('lastpath', BASE_DIR)
		self._pyms__window_blocking = True
		file = [tkFileDialog.asksaveasfilename,tkFileDialog.askopenfilename][open](parent=self, title=title, defaultextension=ext, filetypes=filetypes, initialdir=path)
		self._pyms__window_blocking = False
		if file:
			self.settings['lastpath'] = os.path.dirname(file)
		return file

	def action_states(self):
		file = [NORMAL,DISABLED][not self.pcx]
		for btn in ['save','saveas','close','exportc','colors','saveriff','savejasc','savepal','savewpe']:
			self.buttons[btn]['state'] = file

	def preview(self):
		self.canvas.config(width=self.pcx.width,height=self.pcx.height)
		self.canvas.pack(side=TOP)
		self.canvas.pcx = GRP.frame_to_photo(self.pcx.palette, self.pcx, -1, size=False, trans=False)
		self.canvas.create_image(0, 0, image=self.canvas.pcx, anchor=NW)
		self.action_states()

	def open(self, key=None, file=None):
		if file == None:
			file = self.select_file('Open PCX')
			if not file:
				return
		pcx = PCX.PCX()
		try:
			pcx.load_file(file)
		except PyMSError, e:
			ErrorDialog(self, e)
			return
		self.pcx = pcx
		self.title('PyPCX %s (%s)' % (LONG_VERSION,file))
		self.file = file
		self.status.set('Load Successful!')
		self.preview()

	def save(self, key=None):
		if key and self.buttons['save']['state'] != NORMAL:
			return
		if self.file == None:
			self.saveas()
			return
		try:
			self.pcx.save_file(self.file)
			self.status.set('Save Successful!')
		except PyMSError, e:
			ErrorDialog(self, e)

	def saveas(self, key=None, type=0):
		if key and self.buttons['saveas']['state'] != NORMAL:
			return
		file = self.select_file('Save PCX As', False)
		if not file:
			return True
		self.file = file
		self.title('PyPCX %s (%s)' % (LONG_VERSION,self.file))
		self.save()

	def loadpal(self, key=None):
		if key and self.buttons['colors']['state'] != NORMAL:
			return
		file = self.select_file('Import Palette', True, '.pal', [('RIFF, JASC, and StarCraft PAL','*.pal'),('StarCraft Tileset WPE','*.wpe'),('ZSoft PCX','*.pcx'),('8-Bit BMP','*.bmp'),('All Files','*')])
		if not file:
			return True
		pal = PAL.Palette()
		try:
			pal.load_file(file)
		except PyMSError, e:
			bmp = BMP.BMP()
			try:
				bmp.load_file(file)
			except PyMSError, b:
				ErrorDialog(self, e)
				return
			pal.palette = bmp.palette
		self.pcx.palette = list(pal.palette)
		self.preview()

	def savepal(self, key, type):
		if key and self.buttons['save']['state'] != NORMAL:
			return
		types = [(('RIFF PAL','*.pal'),('JASC PAL','*.pal'),('StarCraft PAL','*.pal'),('StarCraft Terrain WPE','*.wpe'))[type]]
		types.append(('All Files','*'))
		file = self.select_file('Save Palette As', False, types[0][1][1:], types)
		if not file:
			return True
		p = PAL.Palette()
		p.palette = list(self.pcx.palette)
		try:
			[p.save_riff_pal,p.save_jasc_pal,p.save_sc_pal,p.save_sc_wpe][type](file)
			self.status.set('Palette saved successfully!')
		except PyMSError, e:
			ErrorDialog(self, e)

	def export(self, key=None):
		if key and self.buttons['exportc']['state'] != NORMAL:
			return
		file = self.select_file('Export to BMP', False, '.bmp', [('256 Color BMP','*.bmp'),('All Files','*')])
		if not file:
			return True
		b = BMP.BMP()
		b.load_data(self.pcx.image,self.pcx.palette)
		try:
			b.save_file(file)
		except PyMSError, e:
			ErrorDialog(self, e)
			return
		self.status.set('Image exported successfully!')

	def iimport(self, key=None):
		if key and self.buttons['importc']['state'] != NORMAL:
			return
		file = self.select_file('Import a BMP', True, '.bmp', [('256 Color BMP','*.bmp'),('All Files','*')])
		if not file:
			return True
		b = BMP.BMP()
		try:
			b.load_file(file)
		except PyMSError, e:
			ErrorDialog(self, e)
			return
		if not self.pcx:
			self.pcx = PCX.PCX()
			self.file = 'Unnamed.pcx'
			self.title('PyPCX %s (%s)' % (LONG_VERSION,self.file))
		self.pcx.load_data(b.image,b.palette)
		self.preview()
		self.status.set('Image imported successfully!')

	def close(self, key=None):
		if key and self.buttons['close']['state'] != NORMAL:
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
			register_registry('PyPCX','StarCraft PCX','pcx',os.path.join(BASE_DIR, 'PyPCX.pyw'),os.path.join(BASE_DIR,'Images','PyPCX.ico'))
		except PyMSError, e:
			ErrorDialog(self, e)

	def help(self, e=None):
		webbrowser.open('file:///%s' % os.path.join(BASE_DIR, 'Docs', 'PyPCX.html'))

	def about(self, key=None):
		AboutDialog(self, 'PyPCX', LONG_VERSION)

	def exit(self, e=None):
		savesize(self, self.settings)
		savesettings('PyPCX', self.settings)
		self.destroy()

def main():
	import sys
	if not sys.argv or (len(sys.argv) == 1 and os.path.basename(sys.argv[0]).lower() in ['','pypcx.py','pypcx.pyw','pypcx.exe']):
		gui = PyPCX()
		startup(gui)
	else:
		p = optparse.OptionParser(usage='usage: PyPCX [options] <inp> [out]', version='PyPCX %s' % LONG_VERSION)
		p.add_option('-p', '--pcx', action='store_true', dest='convert', help='Convert from PCX to BMP [Default]', default=True)
		p.add_option('-b', '--bmp', action='store_false', dest='convert', help="Convert from BMP to PCX")
		p.add_option('--gui', help="Opens a file with the GUI", default='')
		opt, args = p.parse_args()
		if opt.gui:
			gui = PyPCX(opt.gui)
			startup(gui)
		else:
			if not len(args) in [1,2]:
				p.error('Invalid amount of arguments')
			path = os.path.dirname(args[0])
			if not path:
				path = os.path.abspath('')
			pcx = PCX.PCX()
			bmp = BMP.BMP()
			ext = ['pcx','bmp'][opt.convert]
			if len(args) == 1:
				args.append('%s%s%s' % (os.path.join(path,os.extsep.join(os.path.basename(args[0]).split(os.extsep)[:-1])), os.extsep, ext))
			if opt.convert:
				print "Reading PCX '%s'..." % args[0]
				try:
					pcx.load_file(args[0])
					print " - '%s' read successfully\nConverting '%s' to %s file '%s'..." % (args[0], ext.upper(), args[1])
					bmp.load_data(pcx.image,pcx.palette)
					bmp.save_file(args[1])
				except PyMSError, e:
					print repr(e)
				else:
					print " - '%s' written succesfully" % args[1]
			else:
				print "Reading BMP '%s'..." % args[0]
				try:
					bmp.load_file(args[0])
					print " - '%s' read successfully\nConverting '%s' to %s file '%s'..." % (args[0], ext.upper(), args[1])
					pcx.load_data(bmp.image,bmp.palette)
					pcx.save_file(args[1])
				except PyMSError, e:
					print repr(e)
				else:
					print " - '%s' written succesfully" % args[1]

if __name__ == '__main__':
	main()