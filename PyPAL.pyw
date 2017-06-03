from Libs.utils import *
from Libs.setutils import *
from Libs.trace import setup_trace
from Libs import PAL,BMP

from Tkinter import *
from tkMessageBox import *
import tkFileDialog,tkColorChooser

from thread import start_new_thread
import optparse, os, webbrowser, sys

VERSION = (1,6)
LONG_VERSION = 'v%s.%s' % VERSION

class PyPAL(Tk):
	def __init__(self, guifile=None):
		#Config
		try:
			self.settings = eval(file(os.path.join(BASE_DIR,'Settings','PyPAL.txt'), 'r').read().strip(),{})
		except IOError, e:
			if e.args[0] == 2:
				self.settings = {}
			else:
				raise

		#Window
		Tk.__init__(self)
		self.title('PyPAL %s' % LONG_VERSION)
		try:
			self.icon = os.path.join(BASE_DIR,'Images','PyPAL.ico')
			self.wm_iconbitmap(self.icon)
		except:
			self.icon = '@%s' % os.path.join(BASE_DIR, 'Images','PyPAL.xbm')
			self.wm_iconbitmap(self.icon)
		self.protocol('WM_DELETE_WINDOW', self.exit)
		setup_trace(self, 'PyPAL')
		self.resizable(False, False)

		self.palette = None
		self.file = None
		self.type = None
		self.edited = False
		self.selected = None

		#Toolbar
		buttons = [
			('new', self.new, 'New (Ctrl+N)', NORMAL, 'Ctrl+N'),
			('open', self.open, 'Open (Ctrl+O)', NORMAL, 'Ctrl+O'),
			('save', self.save, 'Save (Ctrl+S)', DISABLED, 'Ctrl+S'),
			('saveriff', lambda key=None,i=0: self.saveas(key,type=i), 'Save as RIFF *.pal (Ctrl+R)', DISABLED, 'Ctrl+R'),
			('savejasc', lambda key=None,i=1: self.saveas(key,type=i), 'Save as JASC *.pal (Ctrl+J)', DISABLED, 'Ctrl+J'),
			('savepal', lambda key=None,i=2: self.saveas(key,type=i), 'Save as StarCraft *.pal (Ctrl+P)', DISABLED, 'Ctrl+P'),
			('savewpe', lambda key=None,i=3: self.saveas(key,type=i), 'Save as StarCraft Terrain *.wpe (Ctrl+T)', DISABLED, 'Ctrl+T'),
			('close', self.close, 'Close (Ctrl+W)', DISABLED, 'Ctrl+W'),
			10,
			('register', self.register, 'Set as default *.pal and *.wpe editor (Windows Only)', [DISABLED,NORMAL][win_reg], ''),
			('help', self.help, 'Help (F1)', NORMAL, 'F1'),
			('about', self.about, 'About PyPAL', NORMAL, ''),
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

		palmenu = [
			('Copy (Ctrl+C)', self.copy, 0), # 0
			('Paste (Ctrl+P)', self.paste, 0), # 1
		]
		self.palmenu = Menu(self, tearoff=0)
		for m in palmenu:
			if m:
				l,c,u = m
				self.palmenu.add_command(label=l, command=c, underline=u)
			else:
				self.palmenu.add_separator()

		#Canvas
		self.canvas = Canvas(self, width=273, height=273, background='#000000')
		self.canvas.pack(padx=2, pady=2)
		for n in range(256):
			x,y = 3+17*(n%16),3+17*(n/16)
			self.canvas.create_rectangle(x, y, x+15, y+15, fill='#000000', outline='#000000')
			self.canvas.tag_bind(n+1, '<Enter>', lambda e,i=n: self.colorstatus(e,i))
			self.canvas.tag_bind(n+1, '<Leave>', lambda e,i=-1: self.colorstatus(e,i))
			self.canvas.tag_bind(n+1, '<Button-1>', lambda e,i=n: self.select(e,i))
			self.canvas.tag_bind(n+1, '<Double-Button-1>', lambda e,i=n: self.changecolor(e,i))
			self.canvas.tag_bind(n+1, '<ButtonRelease-3>', lambda e,i=n: self.popup(e,i))
		self.sel = self.canvas.create_rectangle(0,0,0,0,outline='#FFFFFF')

		self.bind('<<Copy>>', self.copy)
		self.bind('<<Paste>>', self.paste)

		#Statusbar
		self.status = StringVar()
		statusbar = Frame(self)
		Label(statusbar, textvariable=self.status, bd=1, relief=SUNKEN, width=40, anchor=W).pack(side=LEFT, padx=1)
		image = PhotoImage(file=os.path.join(BASE_DIR,'Images','save.gif'))
		self.editstatus = Label(statusbar, image=image, bd=0, state=DISABLED)
		self.editstatus.image = image
		self.editstatus.pack(side=LEFT, padx=1, fill=Y)
		Label(statusbar, bd=1, relief=SUNKEN, anchor=W).pack(side=LEFT, expand=1, padx=1, fill=X)
		self.status.set('Load or create a Palette.')
		statusbar.pack(side=BOTTOM, fill=X)

		if guifile:
			self.open(file=guifile)

		start_new_thread(check_update, (self,))

	def unsaved(self):
		if self.palette and self.edited:
			file = self.file
			if not file:
				file = 'Unnamed.pal'
			save = askquestion(parent=self, title='Save Changes?', message="Save changes to '%s'?" % file, default=YES, type=YESNOCANCEL)
			if save != 'no':
				if save == 'cancel':
					return True
				if self.file:
					self.save()
				else:
					self.saveas()

	def select_file(self, title, open=True, ext='.pal', filetypes=[('RIFF, JASC, and StarCraft PAL','*.pal'),('StarCraft Tileset WPE','*.wpe'),('ZSoft PCX','*.pcx'),('8-Bit BMP','*.bmp'),('All Files','*')]):
		path = self.settings.get('lastpath', BASE_DIR)
		file = [tkFileDialog.asksaveasfilename,tkFileDialog.askopenfilename][open](parent=self, title=title, defaultextension=ext, filetypes=filetypes, initialdir=path)
		if file:
			self.settings['lastpath'] = os.path.dirname(file)
		return file

	def action_states(self):
		file = [NORMAL,DISABLED][not self.palette]
		for btn in ['saveriff','savejasc','savepal','savewpe','close']:
			self.buttons[btn]['state'] = file
		self.buttons['save']['state'] = [NORMAL,DISABLED][not self.palette or self.type == None]

	def popup(self, e, i):
		if self.palette:
			self.select(e,i)
			self.palmenu.entryconfig(i, state=[DISABLED,NORMAL][not not self.canpaste()])
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
			c = tkColorChooser.askcolor(parent=self, initialcolor='#%02X%02X%02X' % tuple(self.palette.palette[i]), title='Select Color')
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
			m = re.match('^#([\dA-Fa-f]{2})([\dA-Fa-f]{2})([\dA-Fa-f]{2})$', c)
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
			self.palette = PAL.Palette()
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
				file = self.select_file('Open Palette')
				if not file:
					return
			pal = PAL.Palette()
			try:
				pal.load_file(file)
				self.type = pal.type
			except PyMSError, e:
				bmp = BMP.BMP()
				try:
					bmp.load_file(file)
				except PyMSError, b:
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
		if key and self.buttons['save']['state'] != NORMAL:
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
		if key and self.buttons['save']['state'] != NORMAL:
			return
		types = [(('RIFF PAL','*.pal'),('JASC PAL','*.pal'),('StarCraft PAL','*.pal'),('StarCraft Terrain WPE','*.wpe'))[type]]
		types.append(('All Files','*'))
		file = self.select_file('Save Palette As', False, filetypes=types)
		if not file:
			return True
		self.file = file
		self.title('PyPAL %s (%s)' % (LONG_VERSION,self.file))
		self.type = type
		self.save()
		self.action_states()

	def close(self, key=None):
		if key and self.buttons['close']['state'] != NORMAL:
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
				register_registry('PyPAL',type + 'Palette',ext,os.path.join(BASE_DIR, 'PyPAL.pyw'),os.path.join(BASE_DIR,'Images','PyPAL.ico'))
			except PyMSError, e:
				ErrorDialog(self, e)
				break

	def help(self, e=None):
		webbrowser.open('file:///%s' % os.path.join(BASE_DIR, 'Docs', 'PyPAL.html'))

	def about(self, key=None):
		AboutDialog(self, 'PyPAL', LONG_VERSION)

	def exit(self, e=None):
		if not self.unsaved():
			savesettings('PyPAL', self.settings)
			self.destroy()

def main():
	import sys
	if not sys.argv or (len(sys.argv) == 1 and os.path.basename(sys.argv[0]).lower() in ['','pypal.py','pypal.pyw','pypal.exe']):
		gui = PyPAL()
		gui.mainloop()
	else:
		p = optparse.OptionParser(usage='usage: PyPAL [options] <inp> [out]', version='PyPAL %s' % LONG_VERSION)
		p.add_option('-s', '--starcraft', action='store_const', const=0, dest='format', help="Convert to StarCraft PAL format [default]", default=0)
		p.add_option('-w', '--wpe', action='store_const', const=1, dest='format', help="Convert to StarCraft WPE format")
		p.add_option('-r', '--riff', action='store_const', const=2, dest='format', help="Convert to RIFF PAL format")
		p.add_option('-j', '--jasc', action='store_const', const=3, dest='format', help="Convert to JASC PAL format")
		p.add_option('--gui', help="Opens a file with the GUI", default='')
		opt, args = p.parse_args()
		if opt.gui:
			gui = PyPAL(opt.gui)
			gui.mainloop()
		else:
			if not len(args) in [1,2]:
				p.error('Invalid amount of arguments')
			path = os.path.dirname(args[0])
			if not path:
				path = os.path.abspath('')
			pal = PAL.Palette()
			ext = ['pal','wpe','pal','pal'][opt.format]
			if len(args) == 1:
				args.append('%s%s%s' % (os.path.join(path,os.extsep.join(os.path.basename(args[0]).split(os.extsep)[:-1])), os.extsep, ext))
			print "Reading Palette '%s'..." % args[0]
			try:
				pal.load_file(args[0])
				print " - '%s' read successfully\nConverting '%s' to %s file '%s'..." % (args[0], ext.upper(), args[1])
				[pal.save_sc_pal,pal.save_sc_wpe,pal.save_riff_pal,pal.save_jasc_pal][opt.format](args[1])
				print " - '%s' written succesfully" % args[1]
			except PyMSError, e:
				print repr(e)

if __name__ == '__main__':
	main()