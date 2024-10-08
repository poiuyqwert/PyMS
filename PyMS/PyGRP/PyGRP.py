
from .Config import PyGRPConfig
from .FramesDialog import FramesDialog
from .utils import BMPStyle, grptobmp, bmptogrp
from .SettingsDialog import SettingsDialog

from ..FileFormats import GRP
from ..FileFormats import Palette

from ..Utilities.utils import WIN_REG_AVAILABLE, register_registry
from ..Utilities.PyMSError import PyMSError
from ..Utilities.UIKit import *
from ..Utilities.analytics import ga, GAScreen
from ..Utilities.trace import setup_trace
from ..Utilities import Assets
from ..Utilities.UpdateDialog import UpdateDialog
from ..Utilities.ErrorDialog import ErrorDialog
from ..Utilities.AboutDialog import AboutDialog
from ..Utilities.HelpDialog import HelpDialog
from ..Utilities.fileutils import check_allow_overwrite_internal_file
from ..Utilities.CheckSaved import CheckSaved

import os
from enum import Flag

from typing import Literal

LONG_VERSION = 'v%s' % Assets.version('PyGRP')

class FrameSet(Flag):
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
	def __init__(self, guifile: str | None = None):
		#Window
		MainWindow.__init__(self)
		self.title('PyGRP %s' % LONG_VERSION)
		self.set_icon('PyGRP')
		self.protocol('WM_DELETE_WINDOW', self.exit)
		ga.set_application('PyGRP', Assets.version('PyGRP'))
		ga.track(GAScreen('PyGRP'))
		setup_trace('PyGRP', self)

		self.config_ = PyGRPConfig()
		Theme.load_theme(self.config_.theme.value, self)
		self.resizable(False, False)

		self.frame_index: int | None = None
		self.pal: str
		self.palettes: dict[str, Palette.Palette] = {}
		self.frames: list[dict[str, Image]] = []
		self.item: Canvas.Item | None = None # type: ignore[name-defined]
		self.grp: GRP.GRP | None = None
		self.file: str | None = None
		self.edited = False
		self.speed: int | None = None
		self.play: str | None = None

		#Toolbar
		self.toolbar = Toolbar(self)
		self.toolbar.add_button(Assets.get_image('new'), self.new, 'New', Ctrl.n)
		self.toolbar.add_button(Assets.get_image('open'), self.open, 'Open', Ctrl.o)
		def save() -> None:
			self.save()
		self.toolbar.add_button(Assets.get_image('save'), save, 'Save', Ctrl.s, enabled=False, tags='file_open')
		def save_as() -> None:
			self.saveas()
		self.toolbar.add_button(Assets.get_image('saveas'), save_as, 'Save As', Ctrl.Alt.a, enabled=False, tags='file_open')
		self.toolbar.add_button(Assets.get_image('close'), self.close, 'Close', Ctrl.w, enabled=False, tags='file_open')
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('exportc'), self.exports, 'Export Selected Frames', Ctrl.e, enabled=False, tags='frame_selected')
		self.toolbar.add_button(Assets.get_image('importc'), self.imports, 'Import Frames', Ctrl.i, enabled=False, tags='file_open')
		self.toolbar.add_gap()
		self.toolbar.add_button(Assets.get_image('remove'), self.remove, 'Remove Frames', Key.Delete, enabled=False, tags='frame_selected')
		self.toolbar.add_button(Assets.get_image('up'), lambda: self.shift(-1), 'Move Frames Up', Ctrl.u, enabled=False, tags='can_move_up')
		self.toolbar.add_button(Assets.get_image('down'), lambda: self.shift(1), 'Move Frames Down', Ctrl.d, enabled=False, tags='can_move_down')
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('asc3topyai'), self.settings, "Manage Settings", Ctrl.m)
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('register'), self.register_registry, 'Set as default *.grp editor (Windows Only)', enabled=WIN_REG_AVAILABLE)
		self.toolbar.add_button(Assets.get_image('help'), self.help, 'Help', Key.F1)
		self.toolbar.add_button(Assets.get_image('about'), self.about, 'About PyGRP')
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('exit'), self.exit, 'Exit', Shortcut.Exit)
		self.toolbar.pack(side=TOP, padx=1, pady=1, fill=X)

		frame = Frame(self)

		self.hex = BooleanVar()
		self.hex.set(self.config_.hex.value)

		leftframe = Frame(frame)
		#Listbox
		f = Frame(leftframe)
		Label(f, text='Frames:', anchor=W).pack(side=LEFT)
		Checkbutton(f, text='Hex', variable=self.hex, command=self.update_list).pack(side=RIGHT)
		f.pack(side=TOP, fill=X)
		self.listbox = ScrolledListbox(leftframe, scroll_speed=2, selectmode=EXTENDED, width=15, height=17)
		self.listbox.pack(side=TOP, padx=1, pady=1, fill=X, expand=1)
		self.listbox.bind(WidgetEvent.Listbox.Select(), self.preview)
		self.bind(Ctrl.a(), self.selectall)

		#Palette
		Label(leftframe, text='Palette:', anchor=W).pack(fill=X)
		self.pallist = ScrolledListbox(leftframe, width=15, height=4)
		self.pallist.pack(side=BOTTOM, padx=1, pady=1, fill=BOTH, expand=1)
		self.pallist.bind(WidgetEvent.Listbox.Select(), self.changepalette)

		s = -1
		for pal in os.listdir(Assets.palettes_dir):
			try:
				p = Palette.Palette()
				p.load_file(Assets.palette_file_path(pal))
				if pal == self.config_.preview.palette.value:
					s = self.pallist.size() # type: ignore[assignment]
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
			self.config_.preview.palette.value = self.pal
			s = 0
		self.pallist.select_set(s)
		self.pallist.see(s)

		rightframe = Frame(frame)
		#Canvas
		self.canvas = Canvas(rightframe, width=258, height=258)
		self.canvas.configure(background=self.config_.preview.bg_color.value)
		self.canvas.pack(side=TOP, padx=2, pady=2)
		self.canvas.bind(Double.Click_Left(), self.bgcolor)
		self.grpbrdr: Canvas.Item = self.canvas.create_rectangle(0, 0, 0, 0, outline='#00FF00') # type: ignore[name-defined]
		self.framebrdr: Canvas.Item = self.canvas.create_rectangle(0, 0, 0, 0, outline='#FF0000') # type: ignore[name-defined]

		#Frameviewing
		self.controls = Toolbar(rightframe)
		self.controls.add_button(Assets.get_image('begin'), lambda: self.frameset(FrameSet.first), 'Jump to first frame', enabled=False, tags='can_preview')
		self.controls.add_button(Assets.get_image('frw'), lambda: self.frameset(FrameSet.prev_frameset), 'Jump 17 frames Up', enabled=False, tags='can_preview')
		self.controls.add_button(Assets.get_image('rw'), lambda: self.frameset(FrameSet.prev_frame), 'Jump 1 frame Up', enabled=False, tags='can_preview')
		self.controls.add_button(Assets.get_image('frwp'), lambda: self.frameset(FrameSet.play_prev_framesets), 'Play every 17th frame going Up', enabled=False, tags='can_preview')
		self.controls.add_button(Assets.get_image('rwp'), lambda: self.frameset(FrameSet.play_prev_frames), 'Play every frame going Up', enabled=False, tags='can_preview')
		self.controls.add_button(Assets.get_image('stop'), lambda: self.frameset(FrameSet.stop), 'Stop playing frames', enabled=False, tags=('can_preview', 'is_playing'))
		self.controls.add_button(Assets.get_image('fwp'), lambda: self.frameset(FrameSet.play_next_frames), 'Play every frame going Down', enabled=False, tags='can_preview')
		self.controls.add_button(Assets.get_image('ffwp'), lambda: self.frameset(FrameSet.play_next_framesets), 'Play every 17th frame going Down', enabled=False, tags='can_preview')
		self.controls.add_button(Assets.get_image('fw'), lambda: self.frameset(FrameSet.next_frame), 'Jump 1 frame Down', enabled=False, tags='can_preview')
		self.controls.add_button(Assets.get_image('ffw'), lambda: self.frameset(FrameSet.next_frameset), 'Jump 17 frames Down', enabled=False, tags='can_preview')
		self.controls.add_button(Assets.get_image('end'), lambda: self.frameset(FrameSet.last), 'Jump to last frame', enabled=False, tags='can_preview')
		self.controls.pack(padx=1, pady=1)

		self.prevspeed = IntegerVar(self.config_.preview.speed.value, [1,5000])
		self.transid = IntegerVar(self.config_.transparent_index.value, [0,255])
		self.prevfrom = IntegerVar(0, [0,0])
		self.prevto = IntegerVar(0, [0,0])
		self.showpreview = BooleanVar()
		self.showpreview.set(self.config_.preview.show.value)
		self.looppreview = BooleanVar()
		self.looppreview.set(self.config_.preview.loop.value)
		self.grpo = BooleanVar()
		self.grpo.set(self.config_.preview.outline.grp.value)
		self.frameo = BooleanVar()
		self.frameo.set(self.config_.preview.outline.frame.value)
		self.bmp_style = IntVar()
		self.bmp_style.set(self.config_.bmp_style.value.index)
		self.uncompressed = BooleanVar()
		self.uncompressed.set(self.config_.uncompressed.value)

		#Options
		opts = Frame(rightframe)
		f = Frame(opts)
		Label(f, text='Preview Speed: ').pack(side=LEFT)
		Entry(f, textvariable=self.prevspeed, font=Font.fixed(), width=4).pack(side=LEFT)
		Label(f, text='ms  ').pack(side=LEFT)
		f.grid(row=0, column=0, sticky=W)
		f = Frame(opts)
		Label(f, text='Transparent Index: ').pack(side=LEFT)
		self.transent = Entry(f, textvariable=self.transid, font=Font.fixed(), width=3)
		self.transent.pack(side=LEFT)
		f.grid(row=0, column=1, sticky=W)
		f = Frame(opts)
		Label(f, text='Preview Between: ').pack(side=LEFT)
		self.prevstart = Entry(f, textvariable=self.prevfrom, font=Font.fixed(), width=3, state=DISABLED)
		self.prevstart.pack(side=LEFT)
		Label(f, text=' - ').pack(side=LEFT)
		self.prevend = Entry(f, textvariable=self.prevto, font=Font.fixed(), width=3, state=DISABLED)
		self.prevend.pack(side=LEFT)
		f.grid(row=1, columnspan=2)
		Checkbutton(opts, text='Show Preview', variable=self.showpreview, command=self.showprev).grid(row=2, column=0, sticky=W)
		Checkbutton(opts, text='Loop Preview', variable=self.looppreview).grid(row=2, column=1, sticky=W)
		Checkbutton(opts, text='GRP Outline (Green)', variable=self.grpo, command=self.grpoutline).grid(row=3, column=0, sticky=W)
		Checkbutton(opts, text='Frame Outline (Red)', variable=self.frameo, command=self.frameoutline).grid(row=3, column=1, sticky=W)
		dd = DropDown(opts, self.bmp_style, [style.display_name for style in BMPStyle.ALL()])
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
		self.editstatus = statusbar.add_icon(Assets.get_image('save'))
		statusbar.add_spacer()
		statusbar.pack(side=BOTTOM, fill=X)

		self.config_.windows.main.load_size(self)

		if guifile:
			self.open(file=guifile)

		UpdateDialog.check_update(self, 'PyGRP')

	def check_saved(self) -> CheckSaved:
		if not self.grp or not self.edited:
			return CheckSaved.saved
		file = self.file
		if not file:
			file = 'Unnamed.grp'
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
		return not not self.grp

	def is_frame_selected(self) -> bool:
		return not not self.listbox.curselection()

	def can_preview(self) -> bool:
		return self.listbox.size() > 1 and self.showpreview.get() # type: ignore[return-value, operator]

	def can_move_up(self) -> bool:
		selected = [int(i) for i in self.listbox.curselection()]
		return not not selected and min(selected) > 0

	def can_move_down(self) -> bool:
		selected = [int(i) for i in self.listbox.curselection()]
		return not not selected and max(selected) < self.listbox.size()-1 # type: ignore[operator]

	def action_states(self) -> None:
		self.editstatus['state'] = NORMAL if self.edited else DISABLED
		self.transent['state'] = NORMAL if self.is_file_open() else DISABLED

		self.toolbar.tag_enabled('file_open', self.is_file_open())
		self.toolbar.tag_enabled('frame_selected', self.is_frame_selected())
		self.toolbar.tag_enabled('can_move_up', self.can_move_up())
		self.toolbar.tag_enabled('can_move_down', self.can_move_down())

		self.controls.tag_enabled('can_preview', self.can_preview())
		self.controls.tag_enabled('is_playing', not not self.play)

	def get_bmp_style(self) -> BMPStyle:
		return BMPStyle.from_index(self.bmp_style.get())

	def showprev(self) -> None:
		if self.showpreview.get():
			self.preview()
		elif self.item:
			self.stopframe()
			self.item.delete()
			self.item = None
		self.action_states()
		self.grpoutline()
		self.frameoutline()

	def grpoutline(self) -> None:
		if self.grpo.get() and self.listbox.curselection() and self.showpreview.get():
			if self.grp:
				x,y = 131 - self.grp.width//2, 131 - self.grp.height//2
				w,h = x + self.grp.width + 1, y + self.grp.height + 1
			else:
				x,y,w,h = 0,0,0,0
			self.grpbrdr.coords(x, y, w, h)
		else:
			self.grpbrdr.coords(0, 0, 0, 0)

	def frameoutline(self) -> None:
		x1,y1,x2,y2 = 0,0,0,0
		if self.grp and self.frameo.get() and self.listbox.curselection() and self.showpreview.get():
			frame = int(self.listbox.curselection()[0])
			x1,y1,x2,y2 = self.grp.images_bounds[frame]
			dx = 131 - self.grp.width//2
			dy = 131 - self.grp.height//2
			x1 += dx
			x2 += dx + 1
			y1 += dy
			y2 += dy + 1
		self.framebrdr.coords(x1,y1, x2,y2)

	def preview(self, e: Event | None = None, force: bool = False) -> None:
		if not self.grp:
			return
		self.action_states()
		if self.listbox.size() and self.listbox.curselection() and self.showpreview.get():
			frame = int(self.listbox.curselection()[0])
			if frame != self.frame_index or force or not self.item:
				self.frame_index = frame
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

	def changepalette(self, e: Event | None = None) -> None:
		if not self.pallist.curselection():
			return
		pal = self.pallist.get(self.pallist.curselection()[0])
		if pal == self.pal:
			return
		self.pal = pal
		self.preview(None, True)

	def frameset(self, n: FrameSet) -> None:
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
			s: int | Literal['end']
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
				size: int = self.listbox.size() # type: ignore[assignment]
				if s < 0 or s >= size:
					if not self.looppreview.get():
						return
					while s < 0:
						s += size
					if s >= size:
						s %= size
			else:
				s = 0
			self.listbox.select_clear(0,END)
			self.listbox.select_set(s)
			self.listbox.see(s)
			self.preview()

	def stopframe(self) -> None:
		if not self.play:
			return
		self.speed = None
		self.after_cancel(self.play)
		self.play = None
		self.action_states()

	def playframe(self) -> None:
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
				if self.play:
					self.after_cancel(self.play)
				self.play = self.after(int(self.prevspeed.get()), self.playframe)
				return
		self.stopframe()

	def bgcolor(self, e: Event | None = None) -> None:
		c = ColorChooser.askcolor(parent=self, initialcolor=self.canvas['background'], title='Select a background color')
		if not c[1]:
			return
		self.canvas['background'] = c[1]

	def selectall(self, e: Event | None = None) -> None:
		self.listbox.select_set(0,END)
		self.action_states()

	def preview_limits(self, init=False) -> None:
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

	def append_frame(self, frame_index: int) -> None:
		f = str(frame_index)
		if self.hex.get():
			f = '0x%02X' % frame_index
		self.listbox.insert(END, '%sFrame %s' % ('   ' * (frame_index // 17 % 2), f))

	def update_list(self) -> None:
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

	def new(self, key: Event | None = None) -> None:
		self.stopframe()
		if self.check_saved() == CheckSaved.cancelled:
			return
		self.grp = GRP.GRP(self.palettes[self.pal].palette, transindex=self.transid.get())
		self.edited = False
		self.frame_index = None
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

	def open(self, key: Event | None = None, file: str | None = None) -> None:
		self.stopframe()
		if self.check_saved() == CheckSaved.cancelled:
			return
		if file is None:
			file = self.config_.last_path.grp.select_open(self)
			if not file:
				return
		grp = GRP.GRP(self.palettes[self.pal].palette)
		try:
			grp.load_file(file, transindex=self.transid.get())
		except PyMSError as e:
			ErrorDialog(self, e)
			return
		self.frame_index = None
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

	def save(self, key: Event | None = None) -> CheckSaved:
		return self.saveas(file_path=self.file)

	def saveas(self, key: Event | None = None, file_path: str | None = None) -> CheckSaved:
		if not self.grp:
			return CheckSaved.saved
		self.stopframe()
		if not file_path:
			file_path = self.config_.last_path.grp.select_save(self)
			if not file_path:
				return CheckSaved.cancelled
		elif not check_allow_overwrite_internal_file(file_path):
			return CheckSaved.cancelled
		try:
			self.grp.save_file(file_path)
		except PyMSError as e:
			ErrorDialog(self, e)
			return CheckSaved.cancelled
		self.file = file_path
		self.status.set('Save Successful!')
		self.edited = False
		self.action_states()
		return CheckSaved.saved

	def close(self, key: Event | None = None) -> None:
		if not self.is_file_open():
			return
		if self.check_saved() == CheckSaved.cancelled:
			return
		self.stopframe()
		self.edited = False
		self.grp = None
		self.frame_index = None
		self.file = None
		self.frames = []
		self.status.set('Load or create a GRP.')
		self.listbox.delete(0,END)
		self.preview_limits()
		self.preview()
		self.action_states()
		self.grpoutline()
		self.frameoutline()

	def exports(self, key: Event | None = None) -> None:
		if not self.grp:
			return
		self.stopframe()
		indexs = [int(i) for i in self.listbox.curselection()]
		file = self.config_.last_path.bmp.select_save(self, title='Export Frames To...')
		if file:
			self.status.set('Extracting frames, please wait...')
			name = os.extsep.join(os.path.basename(file).replace(' ','').split(os.extsep)[:-1])
			self.update_idletasks()
			try:
				grptobmp(os.path.dirname(file), self.palettes[self.pal], self.uncompressed.get(), self.get_bmp_style(), self.grp, name, indexs, True)
			except PyMSError as e:
				ErrorDialog(self, e)
				return
			self.status.set('Frames extracted successfully!')

	def imports(self, key: Event | None = None) -> None:
		if not self.grp:
			return
		self.stopframe()
		update_preview_limit = self.prevto.get() == self.grp.frames
		files: list[str] | None = None
		if self.get_bmp_style() == BMPStyle.bmp_per_frame:
			files = self.config_.last_path.bmp.select_open_multiple(self, title='Import frames...')
		else:
			file = self.config_.last_path.bmp.select_open(self)
			if file is not None:
				files = [file]
		if not files:
			return
		frames = 0
		if self.get_bmp_style() != BMPStyle.bmp_per_frame:
			t = FramesDialog(self, self.config_.windows.frames)
			if not t.result.get():
				return
			frames = t.result.get()
		self.status.set('Importing frames, please wait...')
		size = None
		if self.grp.frames:
			size = (self.grp.width, self.grp.height)
		try:
			fs = bmptogrp(os.path.dirname(files[0]), self.palettes[self.pal], self.uncompressed.get(), frames, files, None, size, True, True, self.get_bmp_style().is_vertical, self.transid.get())
			assert fs is not None
		except PyMSError as e:
			ErrorDialog(self, e)
		else:
			frame = self.grp.frames
			if not frame:
				self.grp.width = fs.width
				self.grp.height = fs.height
			sel: int = self.listbox.size() # type: ignore[assignment]
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

	def remove(self, key: Event | None = None) -> None:
		if not self.grp:
			return
		self.stopframe()
		indexs = [int(i) for i in self.listbox.curselection()]
		i = indexs[0]
		size: int = self.listbox.size() # type: ignore[assignment]
		if i == size-1:
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
			self.frame_index = None
		self.preview_limits()
		self.preview(force=True) # TODO: Why force?
		self.action_states()
		self.grpoutline()
		self.frameoutline()

	def swap(self, f: int, d: int) -> None:
		if not self.grp:
			return
		
		c = self.frames[f]
		self.frames[f] = self.frames[d]
		self.frames[d] = c

		i = self.grp.images[f]
		self.grp.images[f] = self.grp.images[d]
		self.grp.images[d] = i
		
		b = self.grp.images_bounds[f]
		self.grp.images_bounds[f] = self.grp.images_bounds[d]
		self.grp.images_bounds[d] = b

	def shift(self, d: int = 1) -> None:
		if (d == -1 and not self.can_move_up()) or (d == 1 and not self.can_move_down()):
			return
		s = [int(i) for i in self.listbox.curselection()]
		s.sort()
		for f in s[::d]:
			self.swap(f,f+d)
		if self.frame_index is not None:
			self.frame_index += d
		self.listbox.select_clear(0,END)
		for f in s:
			self.listbox.select_set(f+d)
		if self.frame_index is not None:
			self.listbox.see(self.frame_index)
		self.edited = True
		self.action_states()

	def register_registry(self, e: Event | None = None) -> None:
		try:
			register_registry('PyGRP', 'grp', '')
		except PyMSError as e:
			ErrorDialog(self, e)

	def settings(self) -> None:
		SettingsDialog(self, self.config_)

	def help(self, e: Event | None = None) -> None:
		HelpDialog(self, self.config_.windows.help, 'Help/Programs/PyGRP.md')

	def about(self, key: Event | None = None) -> None:
		self.stopframe()
		AboutDialog(self, 'PyGRP', LONG_VERSION, [('TeLaMoN','Compressed GRP file specs.')])

	def exit(self, e: Event | None = None) -> None:
		self.stopframe()
		if self.check_saved() == CheckSaved.cancelled:
			return
		self.config_.windows.main.save_size(self)
		self.config_.hex.value = self.hex.get()
		self.config_.preview.bg_color.value = self.canvas['background']
		self.config_.preview.speed.value = int(self.prevspeed.get())
		self.config_.preview.show.value = self.showpreview.get()
		self.config_.preview.loop.value = self.looppreview.get()
		self.config_.preview.outline.grp.value = self.grpo.get()
		self.config_.preview.outline.frame.value = self.frameo.get()
		self.config_.preview.palette.value = self.pal
		self.config_.bmp_style.value = self.get_bmp_style()
		self.config_.uncompressed.value = self.uncompressed.get()
		self.config_.transparent_index.value = self.transid.get()
		self.config_.save()
		self.destroy()
