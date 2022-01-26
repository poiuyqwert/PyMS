
from FramesDialog import FramesDialog
from utils import grptobmp, bmptogrp

from ..FileFormats import GRP
from ..FileFormats import BMP
from ..FileFormats import Palette

from ..Utilities.utils import BASE_DIR, VERSIONS, WIN_REG_AVAILABLE, couriernew, register_registry
from ..Utilities.Settings import Settings
from ..Utilities.PyMSError import PyMSError
from ..Utilities.UIKit import *
from ..Utilities.analytics import ga, GAScreen
from ..Utilities.trace import setup_trace
from ..Utilities.Toolbar import Toolbar
from ..Utilities.ScrolledListbox import ScrolledListbox
from ..Utilities.IntegerVar import IntegerVar
from ..Utilities.DropDown import DropDown
from ..Utilities.Tooltip import Tooltip
from ..Utilities.StatusBar import StatusBar
from ..Utilities.UpdateDialog import UpdateDialog
from ..Utilities.ErrorDialog import ErrorDialog
from ..Utilities.AboutDialog import AboutDialog

import os, re, webbrowser
from math import ceil

LONG_VERSION = 'v%s' % VERSIONS['PyGRP']

class BMPStyle:
	bmp_per_frame = 'bmp_per_frame'
	single_bmp_framesets = 'single_bmp_framesets'
	single_bmp_vertical = 'single_bmp_vertical'

	ALL = (
		(bmp_per_frame, 'One BMP per Frame'),
		(single_bmp_framesets, 'Single BMP (Framesets)'),
		(single_bmp_vertical, 'Single BMP (Vertical/SFGrpConv)')
	)
	LOOKUP = {key: n for n,(key,_) in enumerate(ALL)}

class FrameSet:
	first               = 1 << 0
	prev_frameset       = 1 << 1
	prev_frame          = 1 << 2
	play_prev_framesets = 1 << 3
	play_prev_frames    = 1 << 4
	stop                = 1 << 5
	play_next_frames    = 1 << 6
	play_next_framesets = 1 << 7
	next_frame          = 1 << 8
	next_frameset       = 1 << 9
	last                = 1 << 10

	PLAY = play_prev_framesets | play_prev_frames | play_next_frames | play_next_framesets

class PyGRP(MainWindow):
	def __init__(self, guifile=None):
		self.settings = Settings('PyGRP', '1')

		#Window
		MainWindow.__init__(self)
		self.title('PyGRP %s' % LONG_VERSION)
		self.set_icon('PyGRP')
		self.protocol('WM_DELETE_WINDOW', self.exit)
		ga.set_application('PyGRP', VERSIONS['PyGRP'])
		ga.track(GAScreen('PyGRP'))
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
		self.toolbar = Toolbar(self)
		self.toolbar.add_button('new', self.new, 'New', Ctrl.n)
		self.toolbar.add_button('open', self.open, 'Open', Ctrl.o)
		self.toolbar.add_button('save', self.save, 'Save', Ctrl.s, enabled=False, tags='file_open')
		self.toolbar.add_button('saveas', self.saveas, 'Save As', Ctrl.Alt.a, enabled=False, tags='file_open')
		self.toolbar.add_button('close', self.close, 'Close', Ctrl.w, enabled=False, tags='file_open')
		self.toolbar.add_section()
		self.toolbar.add_button('exportc', self.exports, 'Export Selected Frames', Ctrl.e, enabled=False, tags='frame_selected')
		self.toolbar.add_button('importc', self.imports, 'Import Frames', Ctrl.i, enabled=False, tags='file_open')
		self.toolbar.add_gap()
		self.toolbar.add_button('remove', self.remove, 'Remove Frames', Key.Delete, enabled=False, tags='frame_selected')
		self.toolbar.add_button('up', lambda: self.shift(-1), 'Move Frames Up', Ctrl.u, enabled=False, identifier='up', tags='frame_selected')
		self.toolbar.add_button('down', lambda: self.shift(1), 'Move Frames Down', Ctrl.d, enabled=False, identifier='down', tags='frame_selected')
		self.toolbar.add_section()
		self.toolbar.add_button('register', self.register, 'Set as default *.grp editor (Windows Only)', enabled=WIN_REG_AVAILABLE)
		self.toolbar.add_button('help', self.help, 'Help', Key.F1)
		self.toolbar.add_button('about', self.about, 'About PyGRP')
		self.toolbar.add_section()
		self.toolbar.add_button('exit', self.exit, 'Exit', Alt.F4)
		self.toolbar.pack(side=TOP, padx=1, pady=1, fill=X)

		frame = Frame(self)

		self.hex = IntVar()
		self.hex.set(self.settings.get('hex', False))

		leftframe = Frame(frame)
		#Listbox
		s = Frame(leftframe)
		Label(s, text='Frames:', anchor=W).pack(side=LEFT)
		Checkbutton(s, text='Hex', variable=self.hex, command=self.update_list).pack(side=RIGHT)
		s.pack(side=TOP, fill=X)
		self.listbox = ScrolledListbox(leftframe, scroll_speed=2, selectmode=EXTENDED, activestyle=DOTBOX, width=15, height=17, bd=0, highlightthickness=0, exportselection=0)
		self.listbox.pack(side=TOP, padx=1, pady=1, fill=X, expand=1)
		self.listbox.bind('<<ListboxSelect>>', self.preview)
		self.bind(Ctrl.a, self.selectall)

		#Palette
		Label(leftframe, text='Palette:', anchor=W).pack(fill=X)
		self.pallist = ScrolledListbox(leftframe, width=15, height=4, bd=0, activestyle=DOTBOX, highlightthickness=0, exportselection=0)
		self.pallist.pack(side=BOTTOM, padx=1, pady=1, fill=BOTH, expand=1)
		self.pallist.bind('<<ListboxSelect>>', self.changepalette)

		s = -1
		for pal in os.listdir(os.path.join(BASE_DIR, 'Palettes')):
			try:
				p = Palette.Palette()
				p.load_file(os.path.join(BASE_DIR, 'Palettes', pal))
				if pal == self.settings.preview.get('palette', 'Units.pal'):
					s = self.pallist.size()
					self.pal = pal
				if not self.pal:
					self.pal = pal
				self.pallist.insert(END, pal)
				self.palettes[pal] = p
			except:
				pass
		if not self.pal:
			raise PyMSError('PyGRP', "Couldn't load palettes")
		if s == -1:
			self.settings.preview.palette = self.pal
			s = 0
		self.pallist.select_set(s)
		self.pallist.see(s)

		rightframe = Frame(frame)
		#Canvas
		self.canvas = Canvas(rightframe, width=258, height=258, background=self.settings.preview.get('bgcolor','#000000'))
		self.canvas.pack(side=TOP, padx=2, pady=2)
		self.canvas.bind(Double.Click_Left, self.bgcolor)
		self.grpbrdr = self.canvas.create_rectangle(0, 0, 0, 0, outline='#00FF00')
		self.framebrdr = self.canvas.create_rectangle(0, 0, 0, 0, outline='#FF0000')

		#Frameviewing
		self.controls = Toolbar(rightframe)
		self.controls.add_button('begin', lambda: self.frameset(FrameSet.first), 'Jump to first frame', enabled=False, tags='can_preview')
		self.controls.add_button('frw', lambda: self.frameset(FrameSet.prev_frameset), 'Jump 17 frames Up', enabled=False, tags='can_preview')
		self.controls.add_button('rw', lambda: self.frameset(FrameSet.prev_frame), 'Jump 1 frame Up', enabled=False, tags='can_preview')
		self.controls.add_button('frwp', lambda: self.frameset(FrameSet.play_prev_framesets), 'Play every 17th frame going Up', enabled=False, tags='can_preview')
		self.controls.add_button('rwp', lambda: self.frameset(FrameSet.play_prev_frames), 'Play every frame going Up', enabled=False, tags='can_preview')
		self.controls.add_button('stop', lambda: self.frameset(FrameSet.stop), 'Stop playing frames', enabled=False, identifier='stop', tags='can_preview')
		self.controls.add_button('fwp', lambda: self.frameset(FrameSet.play_next_frames), 'Play every frame going Down', enabled=False, tags='can_preview')
		self.controls.add_button('ffwp', lambda: self.frameset(FrameSet.play_next_framesets), 'Play every 17th frame going Down', enabled=False, tags='can_preview')
		self.controls.add_button('fw', lambda: self.frameset(FrameSet.next_frame), 'Jump 1 frame Down', enabled=False, tags='can_preview')
		self.controls.add_button('ffw', lambda: self.frameset(FrameSet.next_frameset), 'Jump 17 frames Down', enabled=False, tags='can_preview')
		self.controls.add_button('end', lambda: self.frameset(FrameSet.last), 'Jump to last frame', enabled=False, tags='can_preview')
		self.controls.pack(padx=1, pady=1)

		self.prevspeed = IntegerVar(self.settings.preview.get('speed', 150), [1,5000])
		self.transid = IntegerVar(self.settings.get('transid', 0), [0,255])
		self.prevfrom = IntegerVar(0, [0,0])
		self.prevto = IntegerVar(0, [0,0])
		self.showpreview = IntVar()
		self.showpreview.set(self.settings.preview.get('show', 1))
		self.looppreview = IntVar()
		self.looppreview.set(self.settings.preview.get('loop', 1))
		self.grpo = IntVar()
		self.grpo.set(self.settings.preview.get('grpoutline', 1))
		self.frameo = IntVar()
		self.frameo.set(self.settings.preview.get('frameoutline', 1))
		self.bmp_style = IntVar()
		self.bmp_style.set(BMPStyle.LOOKUP.get(self.settings.get('bmpstyle', BMPStyle.ALL[0][0]), 0))
		self.uncompressed = IntVar()
		self.uncompressed.set(self.settings.get('uncompressed', 0))

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
		s = Frame(opts)
		Label(s, text='Preview Between: ').pack(side=LEFT)
		self.prevstart = Entry(s, textvariable=self.prevfrom, font=couriernew, width=3, state=DISABLED)
		self.prevstart.pack(side=LEFT)
		Label(s, text=' - ').pack(side=LEFT)
		self.prevend = Entry(s, textvariable=self.prevto, font=couriernew, width=3, state=DISABLED)
		self.prevend.pack(side=LEFT)
		s.grid(row=1, columnspan=2)
		Checkbutton(opts, text='Show Preview', variable=self.showpreview, command=self.showprev).grid(row=2, column=0, sticky=W)
		Checkbutton(opts, text='Loop Preview', variable=self.looppreview).grid(row=2, column=1, sticky=W)
		Checkbutton(opts, text='GRP Outline (Green)', variable=self.grpo, command=self.grpoutline).grid(row=3, column=0, sticky=W)
		Checkbutton(opts, text='Frame Outline (Red)', variable=self.frameo, command=self.frameoutline).grid(row=3, column=1, sticky=W)
		dd = DropDown(opts, self.bmp_style, [name for _,name in BMPStyle.ALL])
		Tooltip(dd, """\
This option controls the style of BMP being Exported/Imported.
BMP's must be imported with the same style they were exported as.""")
		dd.grid(row=4, column=0, sticky=EW, padx=(3,0))
		Checkbutton(opts, text='Save Uncompressed', variable=self.uncompressed).grid(row=4, column=1, sticky=W)
		opts.pack(pady=(0,3))

		leftframe.pack(side=LEFT, padx=1, pady=1, fill=Y, expand=1)
		rightframe.pack(side=RIGHT, padx=1, pady=1)
		frame.pack()

		#Statusbar
		self.status = StringVar()
		self.status.set('Load or create a GRP.')
		statusbar = StatusBar(self)
		statusbar.add_label(self.status, width=45)
		self.editstatus = statusbar.add_icon(PhotoImage(file=os.path.join(BASE_DIR, 'PyMS', 'Images', 'save.gif')))
		statusbar.add_spacer()
		statusbar.pack(side=BOTTOM, fill=X)

		self.settings.window.load_window_size('main', self)

		if guifile:
			self.open(file=guifile)

		UpdateDialog.check_update(self, 'PyGRP')

	def unsaved(self):
		if self.grp and self.edited:
			file = self.file
			if not file:
				file = 'Unnamed.grp'
			save = MessageBox.askquestion(parent=self, title='Save Changes?', message="Save changes to '%s'?" % file, default=MessageBox.YES, type=MessageBox.YESNOCANCEL)
			if save != MessageBox.NO:
				if save == MessageBox.CANCEL:
					return True
				if self.file:
					self.save()
				else:
					self.saveas()

	def is_file_open(self):
		return not not self.grp

	def is_frame_selected(self):
		return not not self.listbox.curselection()

	def can_preview(self):
		return self.listbox.size() > 1 and self.showpreview.get()

	def can_shift_up(self):
		selected = [int(i) for i in self.listbox.curselection()]
		return selected and min(selected) > 0

	def can_shift_down(self):
		selected = [int(i) for i in self.listbox.curselection()]
		return selected and max(selected) < self.listbox.size()-1

	def action_states(self):
		self.editstatus['state'] = NORMAL if self.edited else DISABLED
		self.transent['state'] = NORMAL if self.is_file_open() else DISABLED
		self.toolbar.tag_enabled('file_open', self.is_file_open())
		self.toolbar.tag_enabled('frame_selected', self.is_frame_selected())
		if not self.can_shift_up():
			self.toolbar.set_enabled('up', False)
		if not self.can_shift_down():
			self.toolbar.set_enabled('down', False)
		self.controls.tag_enabled('can_preview', self.can_preview())
		if not self.play:
			self.controls.set_enabled('stop', False)

	def showprev(self):
		if self.showpreview.get():
			self.preview()
		elif self.item:
			self.stopframe()
			self.item.delete()
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
			self.grpbrdr.coords(x, y, w, h)
		else:
			self.grpbrdr.coords(0, 0, 0, 0)

	def frameoutline(self):
		x1,y1,x2,y2 = 0,0,0,0
		if self.grp and self.frameo.get() and self.listbox.curselection() and self.showpreview.get():
			frame = int(self.listbox.curselection()[0])
			x1,y1,x2,y2 = self.grp.images_bounds[frame]
			dx = 131 - self.grp.width/2
			dy = 131 - self.grp.height/2
			x1 += dx
			x2 += dx + 1
			y1 += dy
			y2 += dy + 1
		self.framebrdr.coords(x1,y1, x2,y2)

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
					self.item.delete()
				self.item = self.canvas.create_image(132, 132, image=image)
				if self.frameo.get():
					self.frameoutline()
		elif self.item:
			self.item.delete()
			self.item = None

	def changepalette(self, e=None):
		if self.pallist.curselection():
			pal = self.pallist.get(self.pallist.curselection()[0])
			if pal != self.pal:
				self.pal = pal
				self.preview(None, True)

	def frameset(self, n):
		if n == FrameSet.stop:
			self.stopframe()
		elif n & FrameSet.PLAY:
			if n == FrameSet.play_prev_framesets:
				self.speed = -17
			elif n == FrameSet.play_prev_frames:
				self.speed = -1
			elif n == FrameSet.play_next_frames:
				self.speed = 1
			elif n == FrameSet.play_next_framesets:
				self.speed = 17
			self.play = self.after(int(self.prevspeed.get()), self.playframe)
			self.action_states()
		else:
			if n == FrameSet.first:
				s = 0
			elif n == FrameSet.last:
				s = END
			elif self.listbox.curselection():
				s = int(self.listbox.curselection()[0])
				if n == FrameSet.prev_frameset:
					s -= 17
				elif n == FrameSet.prev_frame:
					s -= 1
				elif n == FrameSet.next_frame:
					s += 1
				elif n == FrameSet.next_frameset:
					s += 17
				if s < 0 or s >= self.listbox.size():
					if not self.looppreview.get():
						return
					while s < 0:
						s += self.listbox.size()
					if s >= self.listbox.size():
						s %= self.listbox.size()
			else:
				s = 0
			self.listbox.select_clear(0,END)
			self.listbox.select_set(s)
			self.listbox.see(s)
			self.preview()

	def stopframe(self):
		if self.play:
			self.speed = None
			self.after_cancel(self.play)
			self.play = None
			self.action_states()

	def playframe(self):
		prevfrom = self.prevfrom.get()
		prevto = self.prevto.get()
		if self.speed and self.listbox.curselection() and prevto > prevfrom:
			i = int(self.listbox.curselection()[0]) + self.speed
			frames = prevto-prevfrom+1
			if self.looppreview.get() or (i >= prevfrom and i <= prevto):
				while i < prevfrom or i > prevto:
					if i < prevfrom:
						i += frames
					if i > prevto:
						i -= frames
				self.listbox.select_clear(0,END)
				self.listbox.select_set(i)
				self.listbox.see(i)
				self.preview()
				self.after_cancel(self.play)
				self.play = self.after(int(self.prevspeed.get()), self.playframe)
				return
		self.stopframe()

	def bgcolor(self, e=None):
		c = ColorChooser.askcolor(parent=self, initialcolor=self.canvas['background'], title='Select a background color')
		if c[1]:
			self.canvas['background'] = c[1]

	def selectall(self, e=None):
		self.listbox.select_set(0,END)
		self.action_states()

	def preview_limits(self, init=False):
		if self.grp:
			self.prevstart.config(state=NORMAL)
			self.prevend.config(state=NORMAL)
			to = max(self.grp.frames-1,0)
			self.prevfrom.range[1] = to
			self.prevto.range[1] = to
			if init or self.prevto.get() > to:
				self.prevto.set(to)
		else:
			self.prevstart.config(state=DISABLED)
			self.prevend.config(state=DISABLED)
			self.prevfrom.set(0)
			self.prevto.set(0)

	def append_frame(self, frame):
		f = frame
		if self.hex.get():
			f = '0x%02X' % frame
		self.listbox.insert(END, '%sFrame %s' % ('   ' * (frame / 17 % 2), f))
	def update_list(self):
		s = self.listbox.curselection()
		y = self.listbox.yview()[0]
		self.listbox.delete(0,END)
		if not self.grp:
			return
		for frame in range(self.grp.frames):
			self.append_frame(frame)
		for i in s:
			self.listbox.select_set(i)
		self.listbox.yview_moveto(y)

	def new(self, key=None):
		self.stopframe()
		if not self.unsaved():
			self.grp = GRP.GRP(self.palettes[self.pal], transindex=self.transid.get())
			self.edited = False
			self.frame = None
			self.file = None
			self.frames = []
			self.status.set('Editing new GRP.')
			self.update_list()
			self.listbox.select_set(0)
			self.preview_limits(True)
			self.preview()
			self.action_states()
			self.grpoutline()
			self.frameoutline()

	def open(self, key=None, file=None):
		self.stopframe()
		if not self.unsaved():
			if file == None:
				file = self.settings.lastpath.grp.select_open_file(self, title='Open GRP', filetypes=(('GRP Files','*.grp'),))
				if not file:
					return
			grp = GRP.GRP(self.palettes[self.pal])
			try:
				grp.load_file(file, transindex=self.transid.get())
			except PyMSError as e:
				ErrorDialog(self, e)
				return
			self.frame = None
			self.grp = grp
			self.file = file
			self.frames = [{} for _ in range(grp.frames)]
			self.edited = False
			self.status.set('Load successful!')
			self.status.set(file)
			self.update_list()
			self.listbox.select_set(0)
			self.preview_limits(True)
			self.preview()
			self.action_states()
			self.grpoutline()
			self.frameoutline()
			if grp.uncompressed:
				MessageBox.showinfo(parent=self, title='Uncompressed GRP', message='You have opened an uncompresed GRP.\nWhen saving make sure you select the "Save Uncompressed" option.')

	def save(self, key=None):
		if not self.is_file_open():
			return
		self.stopframe()
		if self.file == None:
			self.saveas()
			return
		try:
			self.grp.save_file(self.file)
			self.status.set('Save Successful!')
			self.edited = False
			self.action_states()
		except PyMSError as e:
			ErrorDialog(self, e)

	def saveas(self, key=None):
		if not self.is_file_open():
			return
		self.stopframe()
		file = self.settings.lastpath.grp.select_save_file(self, title='Save GRP As', filetypes=(('GRP Files','*.grp'),))
		if not file:
			return True
		self.file = file
		self.save()

	def close(self, key=None):
		if not self.is_file_open():
			return
		self.stopframe()
		if not self.unsaved():
			self.edited = False
			self.grp = None
			self.frame = None
			self.file = None
			self.frames = []
			self.status.set('Load or create a GRP.')
			self.listbox.delete(0,END)
			self.preview_limits()
			self.preview()
			self.action_states()
			self.grpoutline()
			self.frameoutline()

	def exports(self, key=None):
		if not self.is_frame_selected():
			return
		self.stopframe()
		indexs = [int(i) for i in self.listbox.curselection()]
		file = self.settings.lastpath.bmp.select_save_file(self, key='export', title='Export Frames To...', filetypes=(('256 Color BMP','*.bmp'),))
		if file:
			self.status.set('Extracting frames, please wait...')
			name = os.extsep.join(os.path.basename(file).replace(' ','').split(os.extsep)[:-1])
			self.update_idletasks()
			try:
				grptobmp(os.path.dirname(file), self.palettes[self.pal], self.uncompressed.get(), self.bmp_style.get(), self.grp, name, indexs, True)
			except PyMSError as e:
				ErrorDialog(self, e)
				return
			self.status.set('Frames extracted successfully!')

	def imports(self, key=None):
		if not self.is_file_open():
			return
		self.stopframe()
		update_preview_limit = self.prevto.get() == self.grp.frames
		if self.bmp_style.get():
			files = self.settings.lastpath.bmp.select_open_file(self, key='import', title='Import single BMP...', filetypes=(('256 Color BMP','*.bmp'),))
		else:
			files = self.settings.lastpath.bmp.select_open_files(self, key='import', title='Import frames...', filetypes=(('256 Color BMP','*.bmp'),))
		if files:
			frames = 0
			if self.bmp_style.get():
				t = FramesDialog(self)
				if not t.result.get():
					return
				frames = t.result.get()
			self.status.set('Importing frames, please wait...')
			size = None
			if self.grp.frames:
				size = [self.grp.width,self.grp.height]
			try:
				fs = bmptogrp(os.path.dirname(files[0]), self.palettes[self.pal], self.uncompressed.get(), frames, files, None, size, True, True, BMPStyle.ALL[self.bmp_style.get()][0] == BMPStyle.single_bmp_vertical, self.transid.get())
			except PyMSError as e:
				ErrorDialog(self, e)
			else:
				frame = self.grp.frames
				if not frame:
					self.grp.width = fs.width
					self.grp.height = fs.height
				sel = self.listbox.size()
				self.grp.images.extend(fs.images)
				self.grp.images_bounds.extend(fs.images_bounds)
				for _ in fs.images:
					self.frames.append({})
					self.append_frame(frame)
					frame += 1
				self.edited = True
				self.grp.frames = len(self.grp.images)
				self.listbox.select_clear(0,END)
				self.listbox.select_set(sel)
				self.listbox.see(sel)
				self.status.set('Frames imported successfully!')
				self.preview_limits(update_preview_limit)
				self.preview()
				self.action_states()
				self.grpoutline()
				self.frameoutline()

	def remove(self, key=None):
		if not self.is_frame_selected():
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
		self.update_list()
		self.edited = True
		if self.listbox.size():
			self.listbox.select_set(i)
			self.listbox.see(i)
		else:
			self.frame = None
		self.preview_limits()
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
		t = self.grp.images_bounds[f]
		self.grp.images_bounds[f] = self.grp.images_bounds[d]
		self.grp.images_bounds[d] = t

	def shift(self, d=1):
		if (d == -1 and not self.can_shift_up()) or (d == 1 and not self.can_shift_down()):
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
		self.edited = True
		self.action_states()

	def register(self, e=None):
		try:
			register_registry('PyGRP','','grp',os.path.join(BASE_DIR, 'PyGRP.pyw'),os.path.join(BASE_DIR, 'PyMS', 'Images', 'PyGRP.ico'))
		except PyMSError as e:
			ErrorDialog(self, e)

	def help(self, e=None):
		webbrowser.open('file:///%s' % os.path.join(BASE_DIR, 'Docs', 'PyGRP.html'))

	def about(self, key=None):
		self.stopframe()
		AboutDialog(self, 'PyGRP', LONG_VERSION, [('TeLaMoN','Compressed GRP file specs.')])

	def exit(self, e=None):
		self.stopframe()
		if not self.unsaved():
			self.settings.window.save_window_size('main', self)
			self.settings.hex = not not self.hex.get()
			self.settings.preview.bgcolor = self.canvas['background']
			self.settings.preview.speed = int(self.prevspeed.get())
			self.settings.preview.show = not not self.showpreview.get()
			self.settings.preview.loop = not not self.looppreview.get()
			self.settings.preview.grpoutline = not not self.grpo.get()
			self.settings.preview.frameoutline = not not self.frameo.get()
			self.settings.preview.palette = self.pal
			self.settings.bmpstyle = BMPStyle.ALL[self.bmp_style.get()][0]
			self.settings.uncompressed = not not self.uncompressed.get()
			self.settings.transid = self.transid.get()
			self.settings.save()
			self.destroy()
