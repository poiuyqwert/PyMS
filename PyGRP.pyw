from Libs.utils import *
from Libs.setutils import *
from Libs.trace import setup_trace
from Libs import BMP, GRP, PAL

from Tkinter import *
from tkMessageBox import *
import tkFileDialog,tkColorChooser

from thread import start_new_thread
from math import ceil
import optparse, os, re, webbrowser, sys

VERSION = (3,9)
LONG_VERSION = 'v%s.%s' % VERSION

def grptobmp(path, pal, uncompressed, onebmp, grp, bmp='', frames=None, mute=False):
	if isstr(grp):
		inp = GRP.GRP(pal.palette, uncompressed)
		if not mute:
			print "Reading GRP '%s'..." % grp
		inp.load_file(grp)
		if not mute:
			print " - '%s' read successfully" % grp
	else:
		inp = grp
	if bmp:
		bmpname = bmp
	else:
		bmpname = os.path.join(path,os.extsep.join(os.path.basename(grp).split(os.extsep)[:-1]))
	out = BMP.BMP(pal.palette)
	if frames == None:
		frames = range(inp.frames)
	n = 0
	for f,frame in enumerate(inp.images):
		if f in frames:
			if onebmp == 1:
				if not n % 17:
					out.image.extend([list(y) for y in frame])
				else:
					for y,d in enumerate(frame):
						out.image[(n / 17) * inp.height + y].extend(d)
			elif onebmp == 2:
				out.image.extend([list(y) for y in frame])
			else:
				name = '%s %s%sbmp' % (bmpname, str(n).zfill(3), os.extsep)
				if not mute:
					print "Writing BMP '%s'..." % name
				out.load_data(frame)
				out.save_file(os.path.join(path,name))
				if not mute:
					print " - '%s' written succesfully" % name
			n += 1
	if onebmp:
		if onebmp == 1 and len(frames) % 17 and len(frames) / 17:
			for y in range(inp.height):
				out.image[-y-1].extend([inp.transindex] * inp.width * (17 - len(frames) % 17))
		out.height = len(out.image)
		out.width = len(out.image[0])
		name = '%s%sbmp' % (bmpname, os.extsep)
		out.save_file(os.path.join(path,name))
		if not mute:
			print " - '%s' written succesfully" % name

def bmptogrp(path, pal, uncompressed, frames, bmp, grp='', issize=None, ret=False, mute=False, vertical=False, transindex=0):
	out = GRP.GRP(pal.palette, uncompressed, transindex)
	inp = BMP.BMP()
	try:
		if frames:
			fullfile = os.path.join(path,bmp)
			if not mute:
				print "Reading BMP '%s'..." % fullfile
			inp.load_file(fullfile)
			out.frames = frames
			if vertical:
				out.width = inp.width
				out.height = inp.height / frames
			else:
				out.width = inp.width / min(frames,17)
				out.height = inp.height / int(ceil(frames / 17.0))
			if out.width > 256 or out.height > 256:
				raise PyMSError('Load', "Invalid dimensions in the BMP '%s' (Frames have a maximum size of 256x256, got %sx%s)" % (fullfile,out.width,out.height))
			if issize and out.width != issize[0] and out.height != issize[1]:
				raise PyMSError('Load',"Invalid dimensions in the BMP '%s' (Expected %sx%s, got %sx%s)" % (fullfile,issize[0],issize[1],out.width,out.height))
			for n in range(frames):
				out.images.append([])
				for y in range(out.height):
					if vertical:
						out.images[-1].append(inp.image[n * out.height + y])
					else:
						x = (n % 17) * out.width
						out.images[-1].append(inp.image[(n / 17) * out.height + y][x:x+out.width])
			if not mute:
				print " - '%s' read successfully" % fullfile
			if ret:
				return out
		else:
			if isinstance(bmp, tuple) or isinstance(bmp, list):
				files = bmp
				found = 2
				single = False
			else:
				file = os.path.basename(bmp)
				t = os.extsep.join(file.split(os.extsep)[:-1])
				m = re.match('(.+) (.+?)',t)
				single = not m
				if single:
					name = t
				else:
					name = m.group(1)
				found = 0
				files = os.listdir(path)
				files.sort()
			r = []
			for f in files:
				if found or f == file:
					if found > 1 or (f.startswith(name) and len(f) > len(name)+2):
						fullfile = os.path.join(path,f)
						if not mute:
							print "Reading BMP '%s'..." % fullfile
						inp.load_file(fullfile)
						if found % 2:
							if issize and inp.width != issize[0] and inp.height != issize[1]:
								raise PyMSError('Load',"Invalid dimensions in the BMP '%s' (Expected %sx%s, got %sx%s)" % (fullfile,issize[0],issize[1],inp.width,inp.height))
							if inp.width != out.width or inp.height != out.height:
								raise PyMSError('Input',"Incorrect frame dimensions in BMP '%s' (Expected %sx%s, got %sx%s)" % (fullfile,out.width,out.height,inp.width,inp.height))
							out.frames += 1
							out.images.append(inp.image)
						else:
							if issize and inp.width != issize[0] and inp.height != issize[1]:
								raise PyMSError('Load',"Invalid dimensions in the BMP '%s' (Expected %sx%s, got %sx%s)" % (fullfile,issize[0],issize[1],inp.width,inp.height))
							if inp.width > 256 or inp.height > 256:
								raise PyMSError('Load', "Invalid dimensions in the BMP '%s' (Frames have a maximum size of 256x256, got %sx%s)" % (fullfile,inp.width,inp.height))
							out.load_data(inp.image)
							found += 1
						if not mute:
							print " - '%s' read successfully" % fullfile
						if single:
							break
						#if ret:
						#	r.append(out)
					else:
						break
			if not found:
				raise PyMSError('Input',"Could not find files matching format '%s <frame>.bmp'" % name)
			if ret:
				return out
	except PyMSError:
		raise
	else:
		if grp:
			fullfile = os.path.join(path,grp)
		else:
			fullfile = os.path.join(path,'%s%sgrp' % (name, os.extsep))
		if not mute:
			print "Writing GRP '%s'..." % fullfile
		out.save_file(fullfile)
		if not mute:
			print " - '%s' written successfully" % fullfile

class FramesDialog(PyMSDialog):
	def __init__(self, parent):
		self.result = IntegerVar(1, [1,None])
		PyMSDialog.__init__(self, parent, 'How many frames?')

	def widgetize(self):
		Label(self, text='How many frames are contained in the BMP?').pack(padx=5, pady=5)
		Entry(self, textvariable=self.result).pack(padx=5, fill=X)

		buttons = Frame(self)
		ok = Button(buttons, text='Ok', width=10, command=self.ok)
		ok.pack(side=LEFT, padx=3, pady=3)
		Button(buttons, text='Cancel', width=10, command=self.cancel).pack(padx=3, pady=3)
		buttons.pack()

		return ok

	def cancel(self):
		self.result.check = False
		self.result.set(0)
		PyMSDialog.cancel(self)

class PyGRP(Tk):
	def __init__(self, guifile=None):
		self.settings = loadsettings('PyGRP')

		#Window
		Tk.__init__(self)
		self.title('PyGRP %s' % LONG_VERSION)
		try:
			self.icon = os.path.join(BASE_DIR,'Images','PyGRP.ico')
			self.wm_iconbitmap(self.icon)
		except:
			self.icon = '@%s' % os.path.join(BASE_DIR, 'Images','PyGRP.xbm')
			self.wm_iconbitmap(self.icon)
		self.protocol('WM_DELETE_WINDOW', self.exit)
		setup_trace(self, 'PyGRP')
		self.resizable(False, False)

		self.frame = None
		self.pal = None
		self.palettes = {}
		self.frames = []
		self.item = None
		self.grp = None
		self.file = None
		self.edited = False
		self.speed = None
		self.play = None
		self.undos = []
		self.redos = []

		#Toolbar
		buttons = [
			('new', self.new, 'New (Ctrl+N)', NORMAL, 'Ctrl+N'),
			('open', self.open, 'Open (Ctrl+O)', NORMAL, 'Ctrl+O'),
			('save', self.save, 'Save (Ctrl+S)', DISABLED, 'Ctrl+S'),
			('saveas', self.saveas, 'Save As (Ctrl+Alt+A)', DISABLED, 'Ctrl+Alt+A'),
			('close', self.close, 'Close (Ctrl+W)', DISABLED, 'Ctrl+W'),
			10,
			('exportc', self.exports, 'Export Frames (Ctrl+E)', DISABLED, 'Ctrl+E'),
			('importc', self.imports, 'Import Frames (Ctrl+I)', DISABLED, 'Ctrl+I'),
			4,
			('remove', self.remove, 'Remove Frames (Delete)', DISABLED, 'Delete'),
			('up', lambda e=None,d=-1: self.shift(e,d), 'Move Frames Up (Ctrl+U)', DISABLED, 'Ctrl+U'),
			('down', lambda e=None,d=1: self.shift(e,d), 'Move Frames Down (Ctrl+D)', DISABLED, 'Ctrl+D'),
			10,
			('register', self.register, 'Set as default *.grp editor (Windows Only)', [DISABLED,NORMAL][win_reg], ''),
			('help', self.help, 'Help (F1)', NORMAL, 'F1'),
			('about', self.about, 'About PyGRP', NORMAL, ''),
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
		Label(leftframe, text='Frames:', anchor=W).pack(side=TOP, fill=X)
		listframe = Frame(leftframe, bd=2, relief=SUNKEN)
		scrollbar = Scrollbar(listframe)
		self.listbox = Listbox(listframe, selectmode=EXTENDED, activestyle=DOTBOX, width=15, height=17, bd=0, highlightthickness=0, yscrollcommand=scrollbar.set, exportselection=0)
		bind = [
			('<MouseWheel>', self.scroll),
			('<Home>', lambda e,l=self.listbox,i=0: self.move(e,l,i)),
			('<End>', lambda e,l=self.listbox,i=END: self.move(e,l,i)),
			('<Up>', lambda e,l=self.listbox,i=-1: self.move(e,l,i)),
			('<Left>', lambda e,l=self.listbox,i=-1: self.move(e,l,i)),
			('<Down>', lambda e,l=self.listbox,i=1: self.move(e,l,i)),
			('<Right>', lambda e,l=self.listbox,i=-1: self.move(e,l,i)),
			('<Prior>', lambda e,l=self.listbox,i=-10: self.move(e,l,i)),
			('<Next>', lambda e,l=self.listbox,i=10: self.move(e,l,i)),
		]
		for b in bind:
			self.bind(*b)
			self.listbox.bind(*b)
		self.listbox.bind('<ButtonRelease-1>', self.preview)
		scrollbar.config(command=self.listbox.yview)
		scrollbar.pack(side=RIGHT, fill=Y)
		self.listbox.pack(side=LEFT, fill=BOTH, expand=1)
		listframe.pack(side=TOP, padx=1, pady=1, fill=BOTH, expand=1)
		self.bind('<Control-a>', self.selectall)

		#Palette
		Label(leftframe, text='Palette:', anchor=W).pack(fill=X)
		palette = Frame(leftframe, bd=2, relief=SUNKEN)
		scrollbar = Scrollbar(palette)
		self.pallist = Listbox(palette, width=15, height=4, bd=0, activestyle=DOTBOX, highlightthickness=0, yscrollcommand=scrollbar.set, exportselection=0)
		bind = [
			('<MouseWheel>', self.scroll),
			('<Home>', lambda e,l=self.pallist,i=0: self.move(e,l,i)),
			('<End>', lambda e,l=self.pallist,i=END: self.move(e,l,i)),
			('<Up>', lambda e,l=self.pallist,i=-1: self.move(e,l,i)),
			('<Left>', lambda e,l=self.pallist,i=-1: self.move(e,l,i)),
			('<Down>', lambda e,l=self.pallist,i=1: self.move(e,l,i)),
			('<Right>', lambda e,l=self.pallist,i=-1: self.move(e,l,i)),
			('<Prior>', lambda e,l=self.pallist,i=-10: self.move(e,l,i)),
			('<Next>', lambda e,l=self.pallist,i=10: self.move(e,l,i)),
			('<ButtonRelease-1>', self.changepalette)
		]
		for b in bind:
			self.pallist.bind(*b)
		scrollbar.config(command=self.pallist.yview)
		scrollbar.pack(side=RIGHT, fill=Y)
		self.pallist.pack(side=LEFT, fill=BOTH, expand=1)
		palette.pack(side=BOTTOM, padx=1, pady=1)
		s = -1
		for pal in os.listdir(os.path.join(BASE_DIR, 'Palettes')):
			try:
				p = PAL.Palette()
				p.load_file(os.path.join(BASE_DIR, 'Palettes',pal))
				if pal == self.settings.get('palette'):
					s = self.pallist.size()
					self.pal = pal
				if not self.pal:
					self.pal = pal
				self.pallist.insert(END, pal)
				self.palettes[pal] = p
			except:
				pass
		if not self.pal:
			raise
		if s == -1:
			self.settings['palette'] = self.pal
			s = 0
		self.pallist.select_set(s)
		self.pallist.see(s)

		rightframe = Frame(frame)
		#Canvas
		self.canvas = Canvas(rightframe, width=258, height=258, background=self.settings.get('bgcolor','#000000'))
		self.canvas.pack(side=TOP, padx=2, pady=2)
		self.canvas.bind('<Double-Button-1>', self.bgcolor)
		self.grpbrdr = self.canvas.create_rectangle(0, 0, 0, 0, outline='#00FF00')
		self.framebrdr = self.canvas.create_rectangle(0, 0, 0, 0, outline='#FF0000')

		#Frameviewing
		frameview = Frame(rightframe)
		buttons = [
			('begin', 'Jump to first frame'),
			('frw', 'Jump 17 frames Left'),
			('rw', 'Jump 1 frame Left'),
			('frwp', 'Play every 17th frame going Left'),
			('rwp', 'Play every frame going Left'),
			('stop', 'Stop playing frames'),
			('fwp', 'Play every frame going Right'),
			('ffwp', 'Play every 17th frame going Right'),
			('fw', 'Jump 1 frame Right'),
			('ffw', 'Jump 17 frames Right'),
			('end', 'Jump to last frame')
		]
		for n,btn in enumerate(buttons):
			if isinstance(btn, tuple):
				image = PhotoImage(file=os.path.join(BASE_DIR,'Images','%s.gif' % btn[0]))
				button = Button(frameview, image=image, width=20, height=20, command=lambda i=n: self.frameset(i), state=DISABLED)
				button.image = image
				button.tooltip = Tooltip(button, btn[1])
				button.pack(side=LEFT)
				self.buttons[btn[0]] = button
			else:
				Frame(frameview, width=2).pack(side=LEFT)
		frameview.pack(padx=1, pady=1)

		self.prevspeed = IntegerVar(self.settings.get('previewspeed', 150), [1,5000])
		self.transid = IntegerVar(self.settings.get('transid', 0), [0,255])
		self.showpreview = IntVar()
		self.showpreview.set(self.settings.get('showpreview', 1))
		self.looppreview = IntVar()
		self.looppreview.set(self.settings.get('looppreview', 1))
		self.grpo = IntVar()
		self.grpo.set(self.settings.get('grpoutline', 1))
		self.frameo = IntVar()
		self.frameo.set(self.settings.get('frameoutline', 1))
		self.singlebmp = IntVar()
		self.singlebmp.set(not not self.settings.get('singlebmp', 0))
		self.thirdstate = self.settings.get('singlebmp', 0) == 2

		#Options
		opts = Frame(rightframe)
		s = Frame(opts)
		Label(s, text='Preview Speed: ').pack(side=LEFT)
		Entry(s, textvariable=self.prevspeed, font=couriernew, width=4).pack(side=LEFT)
		Label(s, text='ms  ').pack(side=LEFT)
		s.grid(row=0, column=0, sticky=W)
		s = Frame(opts)
		Label(s, text='Transparent Index: ').pack(side=LEFT)
		self.transent = Entry(s, textvariable=self.transid, font=couriernew, width=3)
		self.transent.pack(side=LEFT)
		s.grid(row=0, column=1, sticky=W)
		Checkbutton(opts, text='Show Preview', variable=self.showpreview, command=self.showprev).grid(row=1, column=0, sticky=W)
		Checkbutton(opts, text='Loop Preview', variable=self.looppreview).grid(row=1, column=1, sticky=W)
		Checkbutton(opts, text='GRP Outline (Green)', variable=self.grpo, command=self.grpoutline).grid(row=2, column=0, sticky=W)
		Checkbutton(opts, text='Frame Outline (Red)', variable=self.frameo, command=self.frameoutline).grid(row=2, column=1, sticky=W)
		self.checktext = StringVar()
		c = Checkbutton(opts, textvariable=self.checktext, variable=self.singlebmp, command=self.threestate)
		self.checktooltip = Tooltip(c, '')
		c.grid(row=3, column=0, sticky=W)
		self.threestate(True)
		self.uncompressed = IntVar()
		self.uncompressed.set(self.settings.get('uncompressed', 0))
		Checkbutton(opts, text='Save Uncompressed', variable=self.uncompressed).grid(row=3, column=1, sticky=W)
		opts.pack()

		leftframe.pack(side=LEFT, padx=1, pady=1, fill=Y, expand=1)
		rightframe.pack(side=RIGHT, padx=1, pady=1)
		frame.pack()

		#Statusbar
		self.status = StringVar()
		statusbar = Frame(self)
		Label(statusbar, textvariable=self.status, bd=1, relief=SUNKEN, width=45, anchor=W).pack(side=LEFT, padx=1)
		image = PhotoImage(file=os.path.join(BASE_DIR,'Images','save.gif'))
		self.editstatus = Label(statusbar, image=image, bd=0, state=DISABLED)
		self.editstatus.image = image
		self.editstatus.pack(side=LEFT, padx=1, fill=Y)
		Label(statusbar, bd=1, relief=SUNKEN, anchor=W).pack(side=LEFT, expand=1, padx=1, fill=X)
		self.status.set('Load or create a GRP.')
		statusbar.pack(side=BOTTOM, fill=X)

		if 'window' in self.settings:
			loadsize(self, self.settings, 'window')

		if guifile:
			self.open(file=guifile)

		start_new_thread(check_update, (self,))

	def unsaved(self):
		if self.grp and self.edited:
			file = self.file
			if not file:
				file = 'Unnamed.grp'
			save = askquestion(parent=self, title='Save Changes?', message="Save changes to '%s'?" % file, default=YES, type=YESNOCANCEL)
			if save != 'no':
				if save == 'cancel':
					return True
				if self.file:
					self.save()
				else:
					self.saveas()

	def select_file(self, title, open=True, ext='.grp', filetypes=[('GRP Files','*.grp'),('All Files','*')]):
		path = self.settings.get('lastpath', BASE_DIR)
		file = [tkFileDialog.asksaveasfilename,tkFileDialog.askopenfilename][open](parent=self, title=title, defaultextension=ext, filetypes=filetypes, initialdir=path)
		if file:
			self.settings['lastpath'] = os.path.dirname(file)
		return file

	def select_files(self):
		path = self.settings.get('lastpath', BASE_DIR)
		file = tkFileDialog.askopenfilename(parent=self, title='Import Frames From...', defaultextension='.bmp', filetypes=[('256 Color BMP','*.bmp'),('All Files','*')], initialdir=path, multiple=True)
		if file:
			self.settings['lastpath'] = os.path.dirname(file[0])
		return file

	def action_states(self):
		s,m = [int(i) for i in self.listbox.curselection()],self.listbox.size()
		file = [NORMAL,DISABLED][not self.grp]
		select = [NORMAL,DISABLED][not s]
		btns = [DISABLED,NORMAL][m > 1 and self.showpreview.get()]
		self.transent['state'] = [DISABLED,NORMAL][not self.grp]
		for btn in ['save','saveas','close','importc']:
			self.buttons[btn]['state'] = file
		for btn in ['exportc','remove']:
			self.buttons[btn]['state'] = select
		self.buttons['up']['state'] = [NORMAL,DISABLED][not s or min(s) == 0]
		self.buttons['down']['state'] = [NORMAL,DISABLED][not s or max(s) == m-1]
		for btn in ['begin','frw','rw','frwp','rwp','fw','ffw','fwp','ffwp','end']:
			self.buttons[btn]['state'] = btns

	def threestate(self, setup=False):
		if not self.singlebmp.get():
			if not setup:
				if not self.thirdstate:
					self.singlebmp.set(1)
				self.thirdstate = not self.thirdstate
		self.checktext.set('Single BMP (%s)' % ['Framesets','Vertical'][self.thirdstate])
		self.checktooltip.text = "Single BMP is used to export or import all the frames in one single bmp\n(instead of one BMP per frame). " + ["\n\nClick the checkbox to enable output as a single bmp organized by framesets",
			"For this option, the first frameset is\nat the top of the bmp, with the other framesets stacked vertcally below\nit. The frames in each frameset are layed out horizontaly. If you export\na BMP with this option, you are required to use this option when\nimporting it. SFGrpConv is not compatable with this type of single BMP.\n\nClick the check again to use the vertical setup compatible with SFGrpConv.",
			"This option is simply each frame stacked\nvirtically, from the first frame at the top to the last at the bottom.\nThis is the same output style as SFGrpConv.\n\nClick the checkbox again to disable output as a single BMP."][self.singlebmp.get() + self.thirdstate]

	def scroll(self, e):
		if e.delta > 0:
			self.listbox.yview('scroll', -2, 'units')
		else:
			self.listbox.yview('scroll', 2, 'units')

	def move(self, e, listbox, offset):
		index = 0
		if offset == END:
			index = listbox.size()-2
		elif offset not in [0,END] and listbox.curselection():
			print listbox.curselection()
			index = max(min(listbox.size()-1, int(listbox.curselection()[0]) + offset),0)
		listbox.select_clear(0,END)
		listbox.select_set(index)
		listbox.see(index)
		if listbox == self.pallist:
			self.changepalette()
		self.preview()
		return "break"

	def showprev(self):
		if self.showpreview.get():
			self.preview()
		elif self.item:
			self.stopframe()
			self.canvas.delete(self.item)
			self.item = None
		self.action_states()
		self.grpoutline()
		self.frameoutline()

	def grpoutline(self):
		if self.grpo.get() and self.listbox.curselection() and self.showpreview.get():
			if self.grp:
				x,y = 131 - self.grp.width/2, 131 - self.grp.height/2
				w,h = x + self.grp.width + 1, y + self.grp.height + 1
			else:
				x,y,w,h = 0,0,0,0
			self.canvas.coords(self.grpbrdr, x, y, w, h)
		else:
			self.canvas.coords(self.grpbrdr, 0, 0, 0, 0)

	def frameoutline(self):
		x1,y1,x2,y2 = 0,0,0,0
		if self.grp and self.frameo.get() and self.listbox.curselection() and self.showpreview.get():
			frame = int(self.listbox.curselection()[0])
			x1,y1,x2,y2 = self.grp.images_bounds[frame]
			dx = 131 - self.grp.width/2
			dy = 131 - self.grp.height/2
			x1 += dx
			x2 += dx + 2
			y1 += dy
			y2 += dy + 2
		self.canvas.coords(self.framebrdr, x1,y1, x2,y2)

	def preview(self, e=None, pal=False):
		self.action_states()
		if self.listbox.size() and self.listbox.curselection() and self.showpreview.get():
			frame = int(self.listbox.curselection()[0])
			if frame != self.frame or pal or not self.item:
				self.frame = frame
				if not self.pal in self.frames[frame]:
					image = GRP.image_to_tk(self.grp.images[frame], self.palettes[self.pal].palette)
					# image = GRP.frame_to_photo(self.palettes[self.pal].palette, self.grp, frame)
					self.frames[frame][self.pal] = image
				else:
					image = self.frames[frame][self.pal]
				if self.item:
					self.canvas.delete(self.item)
				self.item = self.canvas.create_image(132, 132, image=image)
				if self.frameo.get():
					self.frameoutline()
		elif self.item:
			self.canvas.delete(self.item)

	def changepalette(self, e=None):
		if self.pallist.curselection():
			pal = self.pallist.get(self.pallist.curselection()[0])
			if pal != self.pal:
				self.pal = pal
				self.preview(None, True)

	def frameset(self, n):
		if not n in [3,4,5,6,7]:
			if n in [0,10]:
				s = [END,0][not n]
			elif n in [1,2,8,9] and self.listbox.curselection():
				s = int(self.listbox.curselection()[0]) + [-17,-1,1,17][n % 5 - 1]
				if s < 0 or s >= self.listbox.size():
					if not self.looppreview.get():
						return
					if s < 0:
						s += self.listbox.size()
					if s >= self.listbox.size():
						s %= self.listbox.size()
			else:
				s = 0
			self.listbox.select_clear(0,END)
			self.listbox.select_set(s)
			self.listbox.see(s)
			self.preview()
		if n in [3,4,6,7]:
			self.buttons['stop']['state'] = NORMAL
			self.speed = [-17,-1,None,1,17][n - 3]
			self.play = self.after(int(self.prevspeed.get()), self.playframe)
		elif self.speed or self.play:
			self.stopframe()

	def stopframe(self):
		if self.play:
			self.buttons['stop']['state'] = DISABLED
			self.speed = None
			self.after_cancel(self.play)
			self.play = None

	def playframe(self):
		if self.speed and self.listbox.curselection():
			i = int(self.listbox.curselection()[0]) + self.speed
			if self.looppreview.get() or (i > -1 and i < self.listbox.size()):
				while i < 0 or i >= self.listbox.size():
					if i < 0:
						i += self.listbox.size()
					if i >= self.listbox.size():
						i %= self.listbox.size()
				self.listbox.select_clear(0,END)
				self.listbox.select_set(i)
				self.listbox.see(i)
				self.preview()
				self.after_cancel(self.play)
				self.play = self.after(int(self.prevspeed.get()), self.playframe)
				return
		self.stopframe()

	def bgcolor(self, e=None):
		c = tkColorChooser.askcolor(parent=self, initialcolor=self.canvas['background'], title='Select a background color')
		if c[1]:
			self.canvas['background'] = c[1]

	def selectall(self, e=None):
		self.listbox.select_set(0,END)
		self.action_states()

	def new(self, key=None):
		self.stopframe()
		if not self.unsaved():
			self.grp = GRP.GRP(self.palettes[self.pal], transindex=self.transid.get())
			self.edited = False
			self.frame = None
			self.file = None
			self.frames = []
			self.status.set('Editing new GRP.')
			self.editstatus['state'] = DISABLED
			self.listbox.delete(0,END)
			for frame in range(self.grp.frames):
				self.listbox.insert(END, '%sFrame %s' % ('  ' * (frame / 17 % 2), frame))
			self.listbox.select_set(0)
			self.preview()
			self.action_states()
			self.grpoutline()
			self.frameoutline()

	def open(self, key=None, file=None):
		self.stopframe()
		if not self.unsaved():
			if file == None:
				file = self.select_file('Open GRP')
				if not file:
					return
			grp = GRP.GRP(self.palettes[self.pal])
			try:
				grp.load_file(file, transindex=self.transid.get())
			except PyMSError, e:
				ErrorDialog(self, e)
				return
			self.frame = None
			self.grp = grp
			self.file = file
			self.frames = [{} for _ in range(grp.frames)]
			self.edited = False
			self.status.set('Load successful!')
			self.editstatus['state'] = DISABLED
			self.status.set(file)
			self.listbox.delete(0,END)
			for frame in range(self.grp.frames):
				self.listbox.insert(END, '%sFrame %s' % ('   ' * (frame / 17 % 2), frame))
			self.listbox.select_set(0)
			self.preview()
			self.action_states()
			self.grpoutline()
			self.frameoutline()
			if grp.uncompressed:
				askquestion(parent=self, title='Uncompressed GRP', message='You have opened an uncompresed GRP.\nWhen saving make sure you select the "Save Uncompressed" option.', type=OK)

	def save(self, key=None):
		if key and self.buttons['save']['state'] != NORMAL:
			return
		self.stopframe()
		if self.file == None:
			self.saveas()
			return
		try:
			self.grp.save_file(self.file)
			self.status.set('Save Successful!')
			self.edited = False
			self.editstatus['state'] = DISABLED
		except PyMSError, e:
			ErrorDialog(self, e)

	def saveas(self, key=None):
		if key and self.buttons['saveas']['state'] != NORMAL:
			return
		self.stopframe()
		file = self.select_file('Save GRP As', False)
		if not file:
			return True
		self.file = file
		self.save()

	def close(self, key=None):
		if key and self.buttons['close']['state'] != NORMAL:
			return
		self.stopframe()
		if not self.unsaved():
			self.edited = False
			self.grp = None
			self.frame = None
			self.file = None
			self.frames = []
			self.status.set('Load or create a GRP.')
			self.editstatus['state'] = DISABLED
			self.listbox.delete(0,END)
			self.preview()
			self.action_states()
			self.grpoutline()
			self.frameoutline()

	def exports(self, key=None):
		if key and self.buttons['exportc']['state'] != NORMAL:
			return
		self.stopframe()
		indexs = [int(i) for i in self.listbox.curselection()]
		file = self.select_file('Export Frames To...', False, '.bmp', [('256 Color BMP','*.bmp'),('All Files','*')])
		if file:
			self.status.set('Extracting frames, please wait...')
			name = os.extsep.join(os.path.basename(file).replace(' ','').split(os.extsep)[:-1])
			self.update_idletasks()
			try:
				grptobmp(os.path.dirname(file), self.palettes[self.pal], self.uncompressed.get(), self.singlebmp.get() + self.thirdstate, self.grp, name, indexs, True)
			except PyMSError, e:
				ErrorDialog(self, e)
				return
			self.status.set('Frames extracted successfully!')

	def imports(self, key=None):
		if key and self.buttons['importc']['state'] != NORMAL:
			return
		self.stopframe()
		if self.singlebmp.get():
			files = self.select_file('Import single BMP...', True, '.bmp', [('256 Color BMP','*.bmp'),('All Files','*')])
		else:
			files = self.select_files()
		if files:
			frames = 0
			if self.singlebmp.get():
				t = FramesDialog(self)
				if not t.result.get():
					return
				frames = t.result.get()
			self.status.set('Importing frames, please wait...')
			size = None
			if self.grp.frames:
				size = [self.grp.width,self.grp.height]
			try:
				fs = bmptogrp(os.path.dirname(files[0]), self.palettes[self.pal], self.uncompressed.get(), frames, files, None, size, True, True, self.thirdstate, self.transid.get())
			except PyMSError, e:
				ErrorDialog(self, e)
			else:
				frame = self.grp.frames
				if not frame:
					self.grp.width = fs.width
					self.grp.height = fs.height
				sel = self.listbox.size()
				self.grp.images.extend(fs.images)
				self.grp.images_bounds += [GRP.image_bounds(img) for img in fs.images]
				for i in fs.images:
					self.frames.append({})
					self.listbox.insert(END, '%sFrame %s' % ('   ' * (frame / 17 % 2), frame))
					frame += 1
				self.edited = True
				self.editstatus['state'] = NORMAL
				self.grp.frames = len(self.grp.images)
				self.listbox.select_clear(0,END)
				self.listbox.select_set(sel)
				self.listbox.see(sel)
				self.status.set('Frames imported successfully!')
				self.preview()
				self.action_states()
				self.grpoutline()
				self.frameoutline()

	def remove(self, key=None):
		if key and self.buttons['remove']['state'] != NORMAL:
			return
		self.stopframe()
		indexs = [int(i) for i in self.listbox.curselection()]
		i = indexs[0]
		if i == self.listbox.size()-1:
			i -= 1
		for n,index in enumerate(indexs):
			del self.grp.images[index-n]
			del self.grp.images_bounds[index-n]
			del self.frames[index-n]
		self.grp.frames = len(self.grp.images)
		if not self.grp.frames:
			self.grp.width = 0
			self.grp.height = 0
		self.listbox.delete(0,END)
		for frame in range(self.grp.frames):
			self.listbox.insert(END, '%sFrame %s' % ('   ' * (frame / 17 % 2), frame))
		self.edited = True
		self.editstatus['state'] = NORMAL
		if self.listbox.size():
			self.listbox.select_set(i)
			self.listbox.see(i)
		else:
			self.frame = None
		self.preview(pal=self.pal)
		self.action_states()
		self.grpoutline()
		self.frameoutline()

	def swap(self, f, d):
		t = self.frames[f]
		self.frames[f] = self.frames[d]
		self.frames[d] = t
		t = self.grp.images[f]
		self.grp.images[f] = self.grp.images[d]
		self.grp.images[d] = t

	def shift(self, e=None, d=1):
		if e and self.buttons['up']['state'] != NORMAL:
			return
		s = [int(i) for i in self.listbox.curselection()]
		s.sort()
		for f in s[::d]:
			self.swap(f,f+d)
		if self.frame != None:
			self.frame += d
		self.listbox.select_clear(0,END)
		for f in s:
			self.listbox.select_set(f+d)
		if self.frame != None:
			self.listbox.see(self.frame)
		self.action_states()

	def register(self, e=None):
		try:
			register_registry('PyGRP','','grp',os.path.join(BASE_DIR, 'PyGRP.pyw'),os.path.join(BASE_DIR,'Images','PyGRP.ico'))
		except PyMSError, e:
			ErrorDialog(self, e)

	def help(self, e=None):
		webbrowser.open('file:///%s' % os.path.join(BASE_DIR, 'Docs', 'PyGRP.html'))

	def about(self, key=None):
		self.stopframe()
		AboutDialog(self, 'PyGRP', LONG_VERSION, [('TeLaMoN','Compressed GRP file specs.')])

	def exit(self, e=None):
		self.stopframe()
		if not self.unsaved():
			savesize(self, self.settings, 'window')
			self.settings['bgcolor'] = self.canvas['background']
			self.settings['previewspeed'] = int(self.prevspeed.get())
			self.settings['showpreview'] = not not self.showpreview.get()
			self.settings['looppreview'] = not not self.looppreview.get()
			self.settings['grpoutline'] = not not self.grpo.get()
			self.settings['frameoutline'] = not not self.frameo.get()
			self.settings['singlebmp'] = self.singlebmp.get() + self.thirdstate
			self.settings['uncompressed'] = not not self.uncompressed.get()
			self.settings['palette'] = self.pal
			self.settings['transindex'] = self.transid.get()
			try:
				f = file(os.path.join(BASE_DIR,'Settings','PyGRP.txt'),'w')
				f.write(pprint(self.settings))
				f.close()
			except:
				pass
			self.destroy()

def main():
	import sys
	if not sys.argv or (len(sys.argv) == 1 and os.path.basename(sys.argv[0]).lower() in ['','pygrp.py','pygrp.pyw','pygrp.exe']):
		gui = PyGRP()
		gui.mainloop()
	else:
		p = optparse.OptionParser(usage='usage: PyGRP [options] <inp> [out]', version='PyGRP %s' % LONG_VERSION)
		p.add_option('-p', '--palette', metavar='FILE', help='Choose a palette for GRP to BMP conversion [default: %default]', default='Units.pal')
		p.add_option('-g', '--grptobmps', action='store_true', dest='convert', help="Converting from GRP to BMP's [default]", default=True)
		p.add_option('-b', '--bmpstogrp', action='store_false', dest='convert', help="Converting from BMP's to GRP")
		p.add_option('-u', '--uncompressed', action='store_true', help="Used to signify if the GRP is uncompressed (both to and from BMP) [default: Compressed]", default=False)
		p.add_option('-o', '--onebmp', action='store_true', help='Used to signify that you want to convert a GRP to one BMP file. [default: Multiple]', default=False)
		p.add_option('-f', '--frames', type='int', help='Used to signify you are using a single BMP with alll frames, and how many frames there are.', default=0)
		p.add_option('--gui', help="Opens a file with the GUI", default='')
		opt, args = p.parse_args()
		if opt.gui:
			gui = PyGRP(opt.gui)
			gui.mainloop()
		else:
			if not len(args) in [1,2]:
				p.error('Invalid amount of arguments')
			pal = PAL.Palette()
			fullfile = os.path.abspath(os.path.join('Palettes',opt.palette))
			ext = os.extsep + 'pal'
			if not fullfile.endswith(ext):
				fullfile += ext
			print "Reading palette '%s'..." % fullfile
			try:
				pal.load_file(fullfile)
				print " - '%s' read successfully" % fullfile
				path = os.path.dirname(args[0])
				if not path:
					path = os.path.abspath('')
				args[0] = os.path.join(path,os.path.basename(args[0]))
				if opt.convert:
					grptobmp(path, pal, opt.uncompressed, opt.onebmp, *args)
				else:
					bmptogrp(path, pal, opt.uncompressed, opt.frames, *args)
			except PyMSError, e:
				print repr(e)

if __name__ == '__main__':
	main()