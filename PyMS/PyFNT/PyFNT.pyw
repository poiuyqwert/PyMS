from Libs.utils import *
from Libs.setutils import *
from Libs.trace import setup_trace
from Libs.FNT import *
from Libs import BMP,PCX
from Libs.analytics import *

from Tkinter import *
from tkMessageBox import *
import tkFileDialog,tkColorChooser

from thread import start_new_thread
import optparse, os, webbrowser, sys

LONG_VERSION = 'v%s' % VERSIONS['PyFNT']

# Direct implementation of pseudocode from http://en.wikipedia.org/wiki/Bresenham's_line_algorithm#Optimization
# def bresenham_line(start,end):
	# s,e,line = list(start),list(end),[]
	# steep = abs(end[1]-s[1]) > abs(end[0]-s[0])
	# if steep:
		# s[0],s[1] = s[1],s[0]
		# e[0],e[1] = e[1],e[0]
	# if s[0] > e[0]:
		# s[0],e[0] = e[0],s[0]
		# s[1],e[1] = e[1],s[1]
	# dx,dy,y = e[0] - s[0],abs(e[1] - s[1]),s[1]
	# err = dx / 2
	# if s[0] < e[0]:
		# ystep = 1
	# else:
		# ystep = -1
	# for x in range(s[0],e[0]+1):
		# if steep:
			# line.append((y,x))
		# else:
			# line.append((x,y))
		# err = err - dy
		# if err < 0:
			# y += ystep
			# err = err + dx
	# return line

class InfoDialog(PyMSDialog):
	def __init__(self, parent, size=False):
		self.lowi = IntegerVar(32, [1,255], callback=self.check)
		self.letters = IntegerVar(224, [1,224])
		self.size = size
		self.width = IntegerVar(8, [1,255])
		self.height = IntegerVar(11, [1,255])
		PyMSDialog.__init__(self, parent, 'FNT Specifications')

	def widgetize(self):
		Label(self, text='Whats the ASCII code of the lowest character?').pack(padx=5, pady=5)
		Entry(self, textvariable=self.lowi).pack(padx=5, fill=X)
		Label(self, text='How many letters are in the font?').pack(padx=5, pady=5)
		Entry(self, textvariable=self.letters).pack(padx=5, fill=X)
		if self.size:
			Label(self, text='What is the max width of each character?').pack(padx=5, pady=5)
			Entry(self, textvariable=self.width).pack(padx=5, fill=X)
			Label(self, text='What is the max width of each character?').pack(padx=5, pady=5)
			Entry(self, textvariable=self.height).pack(padx=5, fill=X)
		buttons = Frame(self)
		ok = Button(buttons, text='Ok', width=10, command=self.ok)
		ok.pack(side=LEFT, padx=3, pady=3)
		Button(buttons, text='Cancel', width=10, command=self.cancel).pack(padx=3, pady=3)
		buttons.pack()

		return ok

	def check(self,i):
		self.letters.range[1] = 256 - i
		self.letters.editvalue()

	def cancel(self):
		self.size = None
		PyMSDialog.cancel(self)

class PyFNT(Tk):
	def __init__(self, guifile=None):
		self.settings = loadsettings('PyFNT', {'tfontgam':'MPQ:game\\tfontgam.pcx'})

		#Window
		Tk.__init__(self)
		self.title('PyFNT %s' % LONG_VERSION)
		try:
			self.icon = os.path.join(BASE_DIR,'Images','PyFNT.ico')
			self.wm_iconbitmap(self.icon)
		except:
			self.icon = '@%s' % os.path.join(BASE_DIR, 'Images','PyFNT.xbm')
			self.wm_iconbitmap(self.icon)
		self.protocol('WM_DELETE_WINDOW', self.exit)
		ga.set_application('PyFNT', VERSIONS['PyFNT'])
		ga.track(GAScreen('PyFNT'))
		setup_trace(self, 'PyFNT')
		self.resizable(False, False)

		self.fnt = None
		self.file = None
		self.edited = False
		self.palette = None

		#Toolbar
		buttons = [
			('new', self.new, 'New (Ctrl+N)', NORMAL, 'Ctrl+N'),
			('open', self.open, 'Open (Ctrl+O)', NORMAL, 'Ctrl+O'),
			('save', self.save, 'Save (Ctrl+S)', DISABLED, 'Ctrl+S'),
			('saveas', self.saveas, 'Save As (Ctrl+Alt+A)', DISABLED, 'Ctrl+Alt+A'),
			('close', self.close, 'Close (Ctrl+W)', DISABLED, 'Ctrl+W'),
			4,
			('exportc', self.exports, 'Export Font (Ctrl+E)', DISABLED, 'Ctrl+E'),
			('importc', self.imports, 'Import Font (Ctrl+I)', DISABLED, 'Ctrl+I'),
			10,
			('asc3topyai', self.special, "Manage MPQ's and Special Palette (Ctrl+M)", NORMAL, 'Ctrl+M'),
			10,
			('register', self.register, 'Set as default *.fnt editor (Windows Only)', [DISABLED,NORMAL][win_reg], ''),
			('help', self.help, 'Help (F1)', NORMAL, 'F1'),
			('about', self.about, 'About PyFNT', NORMAL, ''),
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

		frame = Frame(self)
		leftframe = Frame(frame)
		#Listbox
		Label(leftframe, text='Characters:', anchor=W).pack(side=TOP, fill=X)
		listframe = Frame(leftframe, bd=2, relief=SUNKEN)
		scrollbar = Scrollbar(listframe)
		self.listbox = Listbox(listframe, width=15, height=17, bd=0, highlightthickness=0, yscrollcommand=scrollbar.set, exportselection=0)
		bind = [
			('<MouseWheel>', self.scroll),
			('<Home>', lambda a,i=0: self.move(a,i)),
			('<End>', lambda a,i=END: self.move(a,i)),
			('<Up>', lambda a,i=-1: self.move(a,i)),
			('<Left>', lambda a,i=-1: self.move(a,i)),
			('<Down>', lambda a,i=1: self.move(a,i)),
			('<Right>', lambda a,i=-1: self.move(a,i)),
			('<Prior>', lambda a,i=-10: self.move(a,i)),
			('<Next>', lambda a,i=10: self.move(a,i)),
		]
		for b in bind:
			self.bind(*b)
		self.listbox.bind('<ButtonRelease-1>', self.preview)
		scrollbar.config(command=self.listbox.yview)
		scrollbar.pack(side=RIGHT, fill=Y)
		self.listbox.pack(side=LEFT, fill=BOTH, expand=1)
		listframe.pack(side=TOP, padx=1, pady=1, fill=BOTH, expand=1)
		leftframe.pack(side=LEFT, padx=1, pady=1, fill=Y)

		rightframe = Frame(frame)
		## Toolbar
		# buttons = [
			# ('test', self.new, 'New (Ctrl+N)', NORMAL, 'Ctrl+Q'),
		# ]
		# toolbar = Frame(rightframe)
		# for btn in buttons:
			# if isinstance(btn, tuple):
				# image = PhotoImage(file=os.path.join(BASE_DIR,'Images','%s.gif' % btn[0]))
				# button = Button(toolbar, image=image, width=20, height=20, command=btn[1], state=btn[3])
				# button.image = image
				# button.tooltip = Tooltip(button, btn[2])
				# button.pack(side=LEFT)
				# self.buttons[btn[0]] = button
				# a = btn[4]
				# if a:
					# if not a.startswith('F'):
						# self.bind('<%s%s>' % (a[:-1].replace('Ctrl','Control').replace('+','-'), a[-1].lower()), btn[1])
					# else:
						# self.bind('<%s>' % a, btn[1])
			# else:
				# Frame(toolbar, width=btn).pack(side=LEFT)
		# toolbar.pack(side=TOP, padx=1, pady=1, fill=X)

		#Canvas
		self.firstbox = None
		Label(rightframe, text='Display:', anchor=W).pack(side=TOP, fill=X)
		t = Frame(rightframe)
		self.canvas = Canvas(t, width=0, height=0, background='#000000')
		self.canvas.pack(side=TOP, padx=2, pady=2)
		t.pack(side=LEFT, fill=Y)
		rightframe.pack(side=LEFT, fill=BOTH, expand=1, padx=1, pady=1)

		frame.pack(fill=BOTH, expand=1)

		#Statusbar
		self.status = StringVar()
		statusbar = Frame(self)
		Label(statusbar, textvariable=self.status, bd=1, relief=SUNKEN, width=35, anchor=W).pack(side=LEFT, padx=1)
		image = PhotoImage(file=os.path.join(BASE_DIR,'Images','save.gif'))
		self.editstatus = Label(statusbar, image=image, bd=0, state=DISABLED)
		self.editstatus.image = image
		self.editstatus.pack(side=LEFT, padx=1, fill=Y)
		Label(statusbar, bd=1, relief=SUNKEN, anchor=W).pack(side=LEFT, expand=1, padx=1, fill=X)
		self.status.set('Load or create a Font.')
		statusbar.pack(side=BOTTOM, fill=X)

		self.mpqhandler = MPQHandler(self.settings.get('mpqs',[]))
		if (not 'mpqs' in self.settings or not len(self.settings['mpqs'])) and self.mpqhandler.add_defaults():
			self.settings['mpqs'] = self.mpqhandler.mpqs
		e = self.open_files()

		if guifile:
			self.open(file=guifile)

		start_new_thread(check_update, (self, 'PyFNT'))

		if e:
			self.special(err=e)

	def open_files(self):
		self.mpqhandler.open_mpqs()
		err = None
		try:
			palette = PCX.PCX()
			palette.load_file(self.mpqhandler.get_file(self.settings['tfontgam']))
		except PyMSError, e:
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
			save = askquestion(parent=self, title='Save Changes?', message="Save changes to '%s'?" % file, default=YES, type=YESNOCANCEL)
			if save != 'no':
				if save == 'cancel':
					return True
				if self.file:
					self.save()
				else:
					self.saveas()

	def select_file(self, title, open=True, ext='.fnt', filetypes=[('StarCraft FNT','*.fnt'),('All Files','*')], parent=None):
		if parent == None:
			parent = self
		path = self.settings.get('lastpath', BASE_DIR)
		parent._pyms__window_blocking = True
		file = [tkFileDialog.asksaveasfilename,tkFileDialog.askopenfilename][open](parent=parent, title=title, defaultextension=ext, filetypes=filetypes, initialdir=path)
		parent._pyms__window_blocking = False
		if file:
			self.settings['lastpath'] = os.path.dirname(file)
		return file

	def action_states(self):
		file = [NORMAL,DISABLED][not self.fnt]
		for btn in ['save','saveas','close','exportc','importc']:
			self.buttons[btn]['state'] = file

	def move(self, e, a):
		if a == END:
			a = self.listbox.size()-2
		elif a not in [0,END]:
			a = max(min(self.listbox.size()-1, int(self.listbox.curselection()[0]) + a),0)
		self.listbox.select_clear(0,END)
		self.listbox.select_set(a)
		self.listbox.see(a)
		self.preview()

	def scroll(self, e):
		if e.delta > 0:
			self.listbox.yview('scroll', -2, 'units')
		else:
			self.listbox.yview('scroll', 2, 'units')

	def updatelist(self):
		self.listbox.delete(0,END)
		for l in range(len(self.fnt.letters)):
			self.listbox.insert(END, '%s (%c)' % (self.fnt.start+l,self.fnt.start+l))
		self.listbox.select_set(0)

	def resize(self):
		self.canvas['width'] = self.fnt.width * 4 + 1
		self.canvas['height'] = self.fnt.height * 4 + 1
		self.canvas.delete(ALL)
		for y in range(self.fnt.height):
			for x in range(self.fnt.width):
				i = self.canvas.create_rectangle(3+x*4,3+y*4,6+x*4,6+y*4, fill='#%02X%02X%02X' % tuple(self.palette.palette[self.palette.image[0][0]]), outline='')
				if x+y == 0:
					self.firstbox = i

	def preview(self, e=None):
		if self.listbox.size():
			l = int(self.listbox.curselection()[0])
			for y,yd in enumerate(self.fnt.letters[l]):
				for x,c in enumerate(yd):
					self.canvas.itemconfigure(self.firstbox+y*self.fnt.width+x, fill='#%02X%02X%02X' % tuple(self.palette.palette[self.palette.image[0][c]]))

	def new(self, key=None):
		if not self.unsaved():
			s = InfoDialog(self,True)
			if s.size != None:
				self.fnt = FNT()
				self.fnt.width,self.fnt.height,self.fnt.start = s.width.get(),s.height.get(),s.lowi.get()
				for _ in range(s.letters.get()):
					self.fnt.letters.append([[0]*self.fnt.width for __ in range(self.fnt.height)])
				self.updatelist()
				self.file = None
				self.status.set('Editing new Font.')
				self.edited = False
				self.editstatus['state'] = DISABLED
				self.title('PyFNT %s (Unnamed.fnt)' % LONG_VERSION)
				self.action_states()
				self.resize()
				self.preview()

	def open(self, key=None, file=None):
		if not self.unsaved():
			if file == None:
				file = self.select_file('Open FNT')
				if not file:
					return
			if isinstance(file, FNT):
				fnt = file
			else:
				fnt = FNT()
				try:
					fnt.load_file(file)
				except PyMSError, e:
					ErrorDialog(self, e)
					return
				self.title('PyFNT %s (%s)' % (LONG_VERSION,file))
				self.file = file
			self.fnt = fnt
			self.updatelist()
			self.status.set('Load Successful!')
			self.edited = False
			self.action_states()
			self.resize()
			self.preview()

	def save(self, key=None):
		if key and self.buttons['save']['state'] != NORMAL:
			return
		if self.file == None:
			self.saveas()
			return
		try:
			self.fnt.save_file(self.file)
			self.status.set('Save Successful!')
			self.edited = False
			self.editstatus['state'] = DISABLED
		except PyMSError, e:
			ErrorDialog(self, e)

	def saveas(self, key=None, type=0):
		if key and self.buttons['saveas']['state'] != NORMAL:
			return
		file = self.select_file('Save FNT As', False)
		if not file:
			return True
		self.file = file
		self.title('PyFNT %s (%s)' % (LONG_VERSION,self.file))
		self.type = type
		self.save()
		self.action_states()

	def close(self, key=None):
		if key and self.buttons['close']['state'] != NORMAL:
			return
		if not self.unsaved():
			self.fnt = None
			self.title('PyFNT %s' % LONG_VERSION)
			self.file = None
			self.status.set('Load or create a FNT.')
			self.edited = False
			self.editstatus['state'] = DISABLED
			self.action_states()
			self.canvas.delete(ALL)
			self.canvas['width'] = 0
			self.canvas['height'] = 0
			self.firstbox = None

	def exports(self, key=None):
		if key and self.buttons['exportc']['state'] != NORMAL:
			return
		file = self.select_file('Export FNT To...', False, '.bmp', [('256 Color BMP','*.bmp'),('All Files','*')])
		if file:
			self.status.set('Extracting font, please wait...')
			self.update_idletasks()
			try:
				fnttobmp(self.fnt,[self.palette.palette[i] for i in self.palette.image[0]] + [[50,100,50] for _ in range(256 - len(self.palette.image[0]))],file)
			except PyMSError, e:
				ErrorDialog(self, e)
			self.status.set('Font exported successfully!')

	def imports(self, key=None):
		if key and self.buttons['importc']['state'] != NORMAL:
			return
		file = self.select_file('Import FNT From...', True, '.bmp', [('256 Color BMP','*.bmp'),('All Files','*')])
		if file:
			s = InfoDialog(self)
			if s.size != None:
				self.status.set('Importing FNT, please wait...')
				b = BMP.BMP()
				try:
					b.load_file(file)
					fnt = bmptofnt(b,s.lowi.get(),s.letters.get())
				except PyMSError, e:
					ErrorDialog(self, e)
				else:
					self.open(file=fnt)
					self.edited = True
					self.editstatus['state'] = NORMAL
					self.status.set('Font imported successfully!')

	def special(self, key=None, err=None):
		SettingsDialog(self, [('Palette Settings',[('tfontgam.pcx','The special palette which holds the text color.','tfontgam','PCX')])], (340,215), err, mpqhandler=self.mpqhandler)

	def register(self, e=None):
		try:
			register_registry('PyFNT','StarCraft Font','fnt',os.path.join(BASE_DIR, 'PyFNT.pyw'),os.path.join(BASE_DIR,'Images','PyFNT.ico'))
		except PyMSError, e:
			ErrorDialog(self, e)

	def help(self, e=None):
		webbrowser.open('file:///%s' % os.path.join(BASE_DIR, 'Docs', 'PyFNT.html'))

	def about(self, key=None):
		thanks = [
			('FaRTy1billion','Help with file format and example FNT previewer'),
			('StormCost-Fortress.net','FNT specs')
		]
		AboutDialog(self, 'PyFNT', LONG_VERSION, thanks)

	def exit(self, e=None):
		if not self.unsaved():
			savesettings('PyFNT', self.settings)
			self.destroy()

def main():
	import sys
	if not sys.argv or (len(sys.argv) == 1 and os.path.basename(sys.argv[0]).lower() in ['','pyfnt.py','pyfnt.pyw','pyfnt.exe']):
		gui = PyFNT()
		gui.startup()
	else:
		p = optparse.OptionParser(usage='usage: PyFNT [options] <inp> [out]', version='PyFNT %s' % LONG_VERSION)
		p.add_option('-d', '--decompile', action='store_true', dest='convert', help="Decompile FNT to a BMP [default]", default=True)
		p.add_option('-c', '--compile', action='store_false', dest='convert', help="Compile a BMP to a FNT")
		p.add_option('-s', '--specifics', action='store', type='string', help="Specifies the lowest ASCII index and amount of letters (seperated by commas) when compiling")
		p.add_option('--gui', help="Opens a file with the GUI", default='')
		opt, args = p.parse_args()
		if opt.gui:
			gui = PyFNT(opt.gui)
			gui.startup()
		else:
			if not len(args) in [1,2]:
				p.error('Invalid amount of arguments')
			path = os.path.dirname(args[0])
			if not path:
				path = os.path.abspath('')
			ext = ['bmp','fnt'][opt.convert]
			if len(args) == 1:
				args.append('%s%s%s' % (os.path.join(path,os.extsep.join(os.path.basename(args[0]).split(os.extsep)[:-1])), os.extsep, ext))
			if opt.convert:
				fnt = FNT()
				print "Reading FNT '%s'..." % args[0]
				try:
					fnt.load_file(args[0])
					print " - '%s' read successfully\nDecompiling FNT to file '%s'..." % (args[0], args[1])
					fnttobmp(fnt,args[1])
					print " - '%s' written succesfully" % args[1]
				except PyMSError, e:
					print repr(e)
			else:
				if not opt.specifics:
					p.error('You must supply the -s option when using the -c option')
				t = opt.specifics.split(',')
				try:
					lowi,letters = int(t),int(t)
				except:
					print 'Invalid compiling specifics (must be lowest ASCII index followed by amount of letters, seperated by a comma)'
				else:
					if lowi < 1 or lowi > 255:
						print 'Invalid lowest ASCII index (must be in the range 1-255)'
					elif letters < 1 or letters > 255:
						print 'Invalid amount of letters (must be in the range 1-255)'
					elif lowi+letters > 256:
						print 'Either too many letters where specified or too high an initial ASCII index'
					else:
						bmp = BMP()
						print "Reading BMP '%s'..." % args[0]
						try:
							bmp.load_file(args[0])
							print " - '%s' read successfully\nDecompiling BMP to file '%s'..." % (args[0], args[1])
							bmptofnt(fnt,args[1])
							print " - '%s' written succesfully" % args[1]
						except PyMSError, e:
							print repr(e)

if __name__ == '__main__':
	main()