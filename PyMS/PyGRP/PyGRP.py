
from .Config import PyGRPConfig
from .FramesDialog import FramesDialog
from .utils import BMPStyle, grptobmp, bmptogrp
from .SettingsDialog import SettingsDialog

from ..FileFormats import GRP
from ..FileFormats import Palette

from ..Utilities import registry
from ..Utilities.PyMSError import PyMSError
from ..Utilities import UIKit as UI
from ..Utilities.analytics import ga, GAScreen
from ..Utilities.trace import setup_trace
from ..Utilities import Assets
from ..Utilities.UpdateDialog import UpdateDialog
from ..Utilities.ErrorDialog import ErrorDialog
from ..Utilities.AboutDialog import AboutDialog
from ..Utilities.HelpDialog import HelpDialog
from ..Utilities.fileutils import check_allow_overwrite_internal_file
from ..Utilities.CheckSaved import CheckSaved
from ..Utilities.SponsorDialog import SponsorDialog

import os
from enum import Flag

from typing import Literal

LONG_VERSION = 'v' + Assets.version('PyGRP')

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

class PyGRP(UI.MainWindow):
	def __init__(self, guifile: str | None = None):
		#Window
		UI.MainWindow.__init__(self)
		self.title(f'PyGRP {LONG_VERSION}')
		self.set_icon('PyGRP')
		self.protocol('WM_DELETE_WINDOW', self.exit)
		ga.set_application('PyGRP', Assets.version('PyGRP'))
		ga.track(GAScreen('PyGRP'))
		setup_trace('PyGRP', self)

		self.config_ = PyGRPConfig()
		UI.Theme.load_theme(self.config_.theme.value, self)
		self.resizable(False, False)

		self.frame_index: int | None = None
		self.pal: str = ''
		self.palettes: dict[str, Palette.Palette] = {}
		self.frames: list[dict[str, UI.Image]] = []
		self.item: UI.Canvas.Item | None = None # type: ignore[name-defined]
		self.grp: GRP.GRP | None = None
		self.file: str | None = None
		self.edited = False
		self.speed: int | None = None
		self.play: str | None = None

		#Toolbar
		self.toolbar = UI.Toolbar(self)
		self.toolbar.add_button(Assets.get_image('new'), self.new, 'New', UI.Ctrl.n)
		self.toolbar.add_button(Assets.get_image('open'), self.open, 'Open', UI.Ctrl.o)
		def save() -> None:
			self.save()
		self.toolbar.add_button(Assets.get_image('save'), save, 'Save', UI.Ctrl.s, enabled=False, tags='file_open')
		def save_as() -> None:
			self.saveas()
		self.toolbar.add_button(Assets.get_image('saveas'), save_as, 'Save As', UI.Ctrl.Alt.a, enabled=False, tags='file_open')
		self.toolbar.add_button(Assets.get_image('close'), self.close, 'Close', UI.Ctrl.w, enabled=False, tags='file_open')
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('exportc'), self.exports, 'Export Selected Frames', UI.Ctrl.e, enabled=False, tags='frame_selected')
		self.toolbar.add_button(Assets.get_image('importc'), self.imports, 'Import Frames', UI.Ctrl.i, enabled=False, tags='file_open')
		self.toolbar.add_gap()
		self.toolbar.add_button(Assets.get_image('remove'), self.remove, 'Remove Frames', UI.Key.Delete, enabled=False, tags='frame_selected')
		self.toolbar.add_button(Assets.get_image('up'), lambda: self.shift(-1), 'Move Frames Up', UI.Ctrl.u, enabled=False, tags='can_move_up')
		self.toolbar.add_button(Assets.get_image('down'), lambda: self.shift(1), 'Move Frames Down', UI.Ctrl.d, enabled=False, tags='can_move_down')
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('asc3topyai'), self.settings, "Manage Settings", UI.Ctrl.m)
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('register'), self.register_registry, 'Set as default *.grp editor (Windows Only)', enabled=registry.IS_AVAILABLE)
		self.toolbar.add_button(Assets.get_image('help'), self.help, 'Help', UI.Key.F1)
		self.toolbar.add_button(Assets.get_image('about'), self.about, 'About PyGRP')
		self.toolbar.add_button(Assets.get_image('money'), self.sponsor, 'Donate')
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('exit'), self.exit, 'Exit', UI.Shortcut.Exit)
		self.toolbar.pack(side=UI.TOP, padx=1, pady=1, fill=UI.X)

		frame = UI.Frame(self)

		self.hex = UI.BooleanVar()
		self.hex.set(self.config_.hex.value)

		leftframe = UI.Frame(frame)
		#Listbox
		f = UI.Frame(leftframe)
		UI.Label(f, text='Frames:', anchor=UI.W).pack(side=UI.LEFT)
		UI.Checkbutton(f, text='Hex', variable=self.hex, command=self.update_list).pack(side=UI.RIGHT)
		f.pack(side=UI.TOP, fill=UI.X)
		self.listbox = UI.ScrolledListbox(leftframe, scroll_speed=2, selectmode=UI.EXTENDED, width=15, height=17)
		self.listbox.pack(side=UI.TOP, padx=1, pady=1, fill=UI.X, expand=1)
		self.listbox.bind(UI.WidgetEvent.Listbox.Select(), self.preview)
		self.bind(UI.Ctrl.a(), self.selectall)

		#Palette
		UI.Label(leftframe, text='Palette:', anchor=UI.W).pack(fill=UI.X)
		self.pallist = UI.ScrolledListbox(leftframe, width=15, height=4)
		self.pallist.pack(side=UI.BOTTOM, padx=1, pady=1, fill=UI.BOTH, expand=1)
		self.pallist.bind(UI.WidgetEvent.Listbox.Select(), self.changepalette)

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
				self.pallist.insert(UI.END, pal)
				self.palettes[pal] = p
			except Exception:
				pass
		if not self.pal:
			raise PyMSError('PyGRP', "Couldn't load palettes")
		if s == -1:
			self.config_.preview.palette.value = self.pal
			s = 0
		self.pallist.select_set(s)
		self.pallist.see(s)

		rightframe = UI.Frame(frame)
		#Canvas
		self.canvas = UI.Canvas(rightframe, width=258, height=258)
		self.canvas.configure(background=self.config_.preview.bg_color.value)
		self.canvas.pack(side=UI.TOP, padx=2, pady=2)
		self.canvas.bind(UI.Double.Click_Left(), self.bgcolor)
		self.grpbrdr: UI.Canvas.Item = self.canvas.create_rectangle(0, 0, 0, 0, outline='#00FF00') # type: ignore[name-defined]
		self.framebrdr: UI.Canvas.Item = self.canvas.create_rectangle(0, 0, 0, 0, outline='#FF0000') # type: ignore[name-defined]

		#Frameviewing
		self.controls = UI.Toolbar(rightframe)
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

		self.prevspeed = UI.IntegerVar(self.config_.preview.speed.value, [1,5000])
		self.transid = UI.IntegerVar(self.config_.transparent_index.value, [0,255])
		self.prevfrom = UI.IntegerVar(0, [0,0])
		self.prevto = UI.IntegerVar(0, [0,0])
		self.showpreview = UI.BooleanVar()
		self.showpreview.set(self.config_.preview.show.value)
		self.looppreview = UI.BooleanVar()
		self.looppreview.set(self.config_.preview.loop.value)
		self.grpo = UI.BooleanVar()
		self.grpo.set(self.config_.preview.outline.grp.value)
		self.frameo = UI.BooleanVar()
		self.frameo.set(self.config_.preview.outline.frame.value)
		self.bmp_style = UI.IntVar()
		self.bmp_style.set(self.config_.bmp_style.value.index)
		self.uncompressed = UI.BooleanVar()
		self.uncompressed.set(self.config_.uncompressed.value)

		#Options
		opts = UI.Frame(rightframe)
		f = UI.Frame(opts)
		UI.Label(f, text='Preview Speed: ').pack(side=UI.LEFT)
		UI.Entry(f, textvariable=self.prevspeed, font=UI.Font.fixed(), width=4).pack(side=UI.LEFT)
		UI.Label(f, text='ms  ').pack(side=UI.LEFT)
		f.grid(row=0, column=0, sticky=UI.W)
		f = UI.Frame(opts)
		UI.Label(f, text='Transparent Index: ').pack(side=UI.LEFT)
		self.transent = UI.Entry(f, textvariable=self.transid, font=UI.Font.fixed(), width=3)
		self.transent.pack(side=UI.LEFT)
		f.grid(row=0, column=1, sticky=UI.W)
		f = UI.Frame(opts)
		UI.Label(f, text='Preview Between: ').pack(side=UI.LEFT)
		self.prevstart = UI.Entry(f, textvariable=self.prevfrom, font=UI.Font.fixed(), width=3, state=UI.DISABLED)
		self.prevstart.pack(side=UI.LEFT)
		UI.Label(f, text=' - ').pack(side=UI.LEFT)
		self.prevend = UI.Entry(f, textvariable=self.prevto, font=UI.Font.fixed(), width=3, state=UI.DISABLED)
		self.prevend.pack(side=UI.LEFT)
		f.grid(row=1, columnspan=2)
		UI.Checkbutton(opts, text='Show Preview', variable=self.showpreview, command=self.showprev).grid(row=2, column=0, sticky=UI.W)
		UI.Checkbutton(opts, text='Loop Preview', variable=self.looppreview).grid(row=2, column=1, sticky=UI.W)
		UI.Checkbutton(opts, text='GRP Outline (Green)', variable=self.grpo, command=self.grpoutline).grid(row=3, column=0, sticky=UI.W)
		UI.Checkbutton(opts, text='Frame Outline (Red)', variable=self.frameo, command=self.frameoutline).grid(row=3, column=1, sticky=UI.W)
		dd = UI.DropDown(opts, self.bmp_style, [style.display_name for style in BMPStyle.ALL()])
		UI.Tooltip(dd, """\
This option controls the style of BMP being Exported/Imported.
BMP's must be imported with the same style they were exported as.""")
		dd.grid(row=4, column=0, sticky=UI.EW, padx=(3,0))
		UI.Checkbutton(opts, text='Save Uncompressed', variable=self.uncompressed).grid(row=4, column=1, sticky=UI.W)
		opts.pack(pady=(0,3))

		leftframe.pack(side=UI.LEFT, padx=1, pady=1, fill=UI.Y, expand=1)
		rightframe.pack(side=UI.RIGHT, padx=1, pady=1)
		frame.pack()

		#Statusbar
		self.status = UI.StringVar()
		self.status.set('Load or create a GRP.')
		statusbar = UI.StatusBar(self)
		statusbar.add_label(self.status, width=45)
		self.editstatus = statusbar.add_icon(Assets.get_image('save'))
		statusbar.add_spacer()
		statusbar.pack(side=UI.BOTTOM, fill=UI.X)

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
		save = UI.MessageBox.askyesnocancel(parent=self, title='Save Changes?', message=f"Save changes to '{file}'?", default=UI.MessageBox.YES)
		if save is None:
			return CheckSaved.cancelled
		if not save:
			return CheckSaved.saved
		if self.file:
			return self.save()
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
		self.editstatus['state'] = UI.NORMAL if self.edited else UI.DISABLED
		self.transent['state'] = UI.NORMAL if self.is_file_open() else UI.DISABLED

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

	def preview(self, _event: UI.Event | None = None, force: bool = False) -> None:
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

	def changepalette(self, _event: UI.Event | None = None) -> None:
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
			self.play = self.after_managed(int(self.prevspeed.get()), self.playframe)
			self.action_states()
		else:
			s: int | Literal['end']
			if n == FrameSet.first:
				s = 0
			elif n == FrameSet.last:
				s = UI.END
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
			self.listbox.select_clear(0,UI.END)
			self.listbox.select_set(s)
			self.listbox.see(s)
			self.preview()

	def stopframe(self) -> None:
		if not self.play:
			return
		self.speed = None
		self.after_managed_cancel(self.play)
		self.play = None
		self.action_states()

	def playframe(self) -> None:
		prevfrom = self.prevfrom.get()
		prevto = self.prevto.get()
		if self.speed and self.listbox.curselection() and prevto > prevfrom:
			i = int(self.listbox.curselection()[0]) + self.speed
			frames = prevto-prevfrom+1
			if self.looppreview.get() or (prevfrom <= i <= prevto):
				while i < prevfrom or i > prevto:
					if i < prevfrom:
						i += frames
					if i > prevto:
						i -= frames
				self.listbox.select_clear(0,UI.END)
				self.listbox.select_set(i)
				self.listbox.see(i)
				self.preview()
				if self.play:
					self.after_managed_cancel(self.play)
				self.play = self.after_managed(int(self.prevspeed.get()), self.playframe)
				return
		self.stopframe()

	def bgcolor(self, _event: UI.Event | None = None) -> None:
		c = UI.ColorChooser.askcolor(parent=self, initialcolor=self.canvas['background'], title='Select a background color')
		if not c[1]:
			return
		self.canvas['background'] = c[1]

	def selectall(self, _event: UI.Event | None = None) -> None:
		self.listbox.select_set(0,UI.END)
		self.action_states()

	def preview_limits(self, init: bool = False) -> None:
		if self.grp:
			self.prevstart.config(state=UI.NORMAL)
			self.prevend.config(state=UI.NORMAL)
			to = max(self.grp.frames-1,0)
			self.prevfrom.range[1] = to
			self.prevto.range[1] = to
			if init or self.prevto.get() > to:
				self.prevto.set(to)
		else:
			self.prevstart.config(state=UI.DISABLED)
			self.prevend.config(state=UI.DISABLED)
			self.prevfrom.set(0)
			self.prevto.set(0)

	def append_frame(self, frame_index: int) -> None:
		f = str(frame_index)
		if self.hex.get():
			f = f'0x{frame_index:02X}'
		self.listbox.insert(UI.END, f'{"   " * (frame_index // 17 % 2)}Frame {f}')

	def update_list(self) -> None:
		s = self.listbox.curselection()
		y = self.listbox.yview()[0]
		self.listbox.delete(0,UI.END)
		if not self.grp:
			return
		for frame in range(self.grp.frames):
			self.append_frame(frame)
		for i in s:
			self.listbox.select_set(i)
		self.listbox.yview_moveto(y)

	def new(self, _event: UI.Event | None = None) -> None:
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

	def open(self, _event: UI.Event | None = None, file: str | None = None) -> None:
		self.stopframe()
		if self.check_saved() == CheckSaved.cancelled:
			return
		if file is None:
			file = self.config_.last_path.grp.select_open(self)
			if not file:
				return
		grp = GRP.GRP(self.palettes[self.pal].palette)
		try:
			grp.load(file, transindex=self.transid.get())
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
			UI.MessageBox.showinfo(parent=self, title='Uncompressed GRP', message='You have opened an uncompresed GRP.\nWhen saving make sure you select the "Save Uncompressed" option.')

	def save(self, _event: UI.Event | None = None) -> CheckSaved:
		return self.saveas(file_path=self.file)

	def saveas(self, _event: UI.Event | None = None, file_path: str | None = None) -> CheckSaved:
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
			self.grp.save(file_path)
		except PyMSError as e:
			ErrorDialog(self, e)
			return CheckSaved.cancelled
		self.file = file_path
		self.status.set('Save Successful!')
		self.edited = False
		self.action_states()
		return CheckSaved.saved

	def close(self, _event: UI.Event | None = None) -> None:
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
		self.listbox.delete(0,UI.END)
		self.preview_limits()
		self.preview()
		self.action_states()
		self.grpoutline()
		self.frameoutline()

	def exports(self, _event: UI.Event | None = None) -> None:
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
				grptobmp(path=os.path.dirname(file), pal=self.palettes[self.pal], uncompressed=self.uncompressed.get(), bmp_style=self.get_bmp_style(), grp=self.grp, bmp=name, frames=indexs, mute=True)
			except PyMSError as e:
				ErrorDialog(self, e)
				return
			self.status.set('Frames extracted successfully!')

	def imports(self, _event: UI.Event | None = None) -> None:
		if not self.grp:
			return
		self.stopframe()
		update_preview_limit = self.prevto.get() == self.grp.frames
		files: str | list[str] | None = None
		if self.get_bmp_style() == BMPStyle.bmp_per_frame:
			files = self.config_.last_path.bmp.select_open_multiple(self, title='Import frames...')
		else:
			file = self.config_.last_path.bmp.select_open(self)
			if file is not None:
				files = file
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
			fs = bmptogrp(path=os.path.dirname(files[0]), pal=self.palettes[self.pal], uncompressed=self.uncompressed.get(), frames=frames, bmp=files, grp=None, issize=size, ret=True, mute=True, vertical=self.get_bmp_style().is_vertical, transindex=self.transid.get())
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
			self.listbox.select_clear(0,UI.END)
			self.listbox.select_set(sel)
			self.listbox.see(sel)
			self.status.set('Frames imported successfully!')
			self.preview_limits(update_preview_limit)
			self.preview()
			self.action_states()
			self.grpoutline()
			self.frameoutline()

	def remove(self, _event: UI.Event | None = None) -> None:
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
		self.listbox.delete(0,UI.END)
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
		self.listbox.select_clear(0,UI.END)
		for f in s:
			self.listbox.select_set(f+d)
		if self.frame_index is not None:
			self.listbox.see(self.frame_index)
		self.edited = True
		self.action_states()

	def register_registry(self, _event: UI.Event | None = None) -> None:
		try:
			registry.register('PyGRP', 'grp', '')
		except PyMSError as e:
			ErrorDialog(self, e)

	def settings(self) -> None:
		SettingsDialog(self, self.config_)

	def help(self, _event: UI.Event | None = None) -> None:
		HelpDialog(self, self.config_.windows.help, 'Help/Programs/PyGRP.md')

	def about(self, _event: UI.Event | None = None) -> None:
		self.stopframe()
		AboutDialog(self, 'PyGRP', LONG_VERSION, [('TeLaMoN','Compressed GRP file specs.')])

	def sponsor(self) -> None:
		SponsorDialog(self)

	def exit(self, _event: UI.Event | None = None) -> None:
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
