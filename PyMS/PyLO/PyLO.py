
from .Delegates import FindDelegate
from .LOCodeText import LOCodeText
from .FindReplaceDialog import FindReplaceDialog
from .CodeColors import CodeColors
from .Constants import RE_COORDINATES, RE_DRAG_COORDS

from ..FileFormats.LO import LO
from ..FileFormats.Palette import Palette
from ..FileFormats.GRP import CacheGRP, frame_to_photo

from ..Utilities.utils import WIN_REG_AVAILABLE, register_registry, FFile
from ..Utilities.UIKit import *
from ..Utilities import Config
from ..Utilities.analytics import ga, GAScreen
from ..Utilities.trace import setup_trace
from ..Utilities import Assets
from ..Utilities.MPQHandler import MPQHandler
from ..Utilities.SettingsPanel import SettingsPanel
from ..Utilities.PyMSError import PyMSError
from ..Utilities.ErrorDialog import ErrorDialog
from ..Utilities.UpdateDialog import UpdateDialog
from ..Utilities.SettingsDialog_Old import SettingsDialog
from ..Utilities.AboutDialog import AboutDialog
from ..Utilities.HelpDialog import HelpDialog
from ..Utilities.fileutils import check_allow_overwrite_internal_file
from ..Utilities.CheckSaved import CheckSaved

import io
from enum import Enum

from typing import cast, Callable

LONG_VERSION = 'v%s' % Assets.version('PyLO')

class MouseEvent(Enum):
	click = 0
	drag = 1
	release = 2

class PyLO(MainWindow, FindDelegate):
	def __init__(self, guifile: str | None = None) -> None:
		self.settings = Settings('PyLO', '1')
		self.settings.settings.files.set_defaults({
			'basegrp':'MPQ:unit\\terran\\wessel.grp',
			'overlaygrp':'MPQ:unit\\terran\\wesselt.grp',
		})

		#Window
		MainWindow.__init__(self)
		self.set_icon('PyLO')
		self.protocol('WM_DELETE_WINDOW', self.exit)
		ga.set_application('PyLO', Assets.version('PyLO'))
		ga.track(GAScreen('PyLO'))
		self.minsize(435,470)
		setup_trace('PyLO', self)
		Theme.load_theme(self.settings.get('theme'), self)

		self.lo: LO | None = None
		self.file: str | None = None
		self.edited = False
		self.findwindow: FindReplaceDialog | None = None
		self.basegrp: CacheGRP | None = None
		self.basegrp_cache: dict[int, Image | None] = {}
		self.overlaygrp: CacheGRP | None = None
		self.overlaygrp_cache: dict[int, Image | None] = {}
		self.unitpal = Palette()
		self.unitpal.load_file(Assets.palette_file_path('Units.pal'))
		self.previewing_basegrp_frame: int | None = None
		self.previewing_overlaygrp_frame: int | None = None
		self.previewing_offset: tuple[int, int] | None = None
		self.overlayframe: int | None = None
		self.dragoffset: tuple[int, int] | None = None
		self.pauseupdate = False

		self.update_title()

		#Toolbar
		self.toolbar = Toolbar(self)
		self.toolbar.add_button(Assets.get_image('new'), self.new, 'New', Ctrl.n)
		self.toolbar.add_gap()
		self.toolbar.add_button(Assets.get_image('open'), self.open, 'Open', Ctrl.o)
		self.toolbar.add_button(Assets.get_image('import'), self.iimport, 'Import LO?', Ctrl.i)
		self.toolbar.add_gap()
		def save():
			self.save()
		self.toolbar.add_button(Assets.get_image('save'), save, 'Save', Ctrl.s, enabled=False, tags='file_open')
		def saveas():
			self.saveas()
		self.toolbar.add_button(Assets.get_image('saveas'), saveas, 'Save As', Ctrl.Alt.a, enabled=False, tags='file_open')
		self.toolbar.add_button(Assets.get_image('export'), self.export, 'Export LO?', Ctrl.e, enabled=False, tags='file_open')
		self.toolbar.add_button(Assets.get_image('test'), self.test, 'Test Code', Ctrl.t, enabled=False, tags='file_open')
		self.toolbar.add_gap()
		self.toolbar.add_button(Assets.get_image('close'), self.close, 'Close', Ctrl.w, enabled=False, tags='file_open')
		self.toolbar.add_spacer(5)
		self.toolbar.add_button(Assets.get_image('find'), self.find, 'Find/Replace', Ctrl.f, enabled=False, tags='file_open')
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('colors'), self.colors, 'Color Settings', Ctrl.Alt.c)
		self.toolbar.add_gap()
		self.toolbar.add_button(Assets.get_image('asc3topyai'), self.mpqsettings, 'Manage MPQ Settings', Ctrl.m)
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('register'), self.register_registry, 'Set as default *.lo? editor (Windows Only)', enabled=WIN_REG_AVAILABLE)
		self.toolbar.add_button(Assets.get_image('help'), self.help, 'Help', Key.F1)
		self.toolbar.add_button(Assets.get_image('about'), self.about, 'About PyLO')
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('exit'), self.exit, 'Exit', Shortcut.Exit)
		self.toolbar.pack(side=TOP, padx=1, pady=1, fill=X)

		m = Frame(self)
		# Text editor
		self.text = LOCodeText(m, self.edit, highlights=self.settings.settings.get('highlights'), state=DISABLED)
		self.text.grid(sticky=NSEW)
		self.text.icallback = self.statusupdate
		self.text.scallback = self.statusupdate
	
		self.mpqhandler = MPQHandler(self.settings.settings.get('mpqs',[]))
		if (not 'mpqs' in self.settings or not len(self.settings.settings.files['mpqs'])) and self.mpqhandler.add_defaults():
			self.settings.settings.files['mpqs'] = self.mpqhandler.mpq_paths()

		self.usebasegrp = IntVar()
		self.usebasegrp.set(not not self.settings.get('usebasegrp'))
		self.useoverlaygrp = IntVar()
		self.useoverlaygrp.set(not not self.settings.get('useoverlaygrp'))
		self.baseframes = StringVar()
		self.baseframes.set('Base Frame: - / -')
		self.overlayframes = StringVar()
		self.overlayframes.set('Overlay Frame: - / -')

		# Previewer
		f = Frame(m)
		c = Frame(f)
		l = Frame(c)
		Label(l, textvariable=self.baseframes, anchor=W).pack(side=LEFT)
		Label(l, textvariable=self.overlayframes, anchor=W).pack(side=RIGHT)
		l.pack(fill=X, expand=1)
		self.canvas = Canvas(c, borderwidth=0, width=275, height=275, background='#000000', highlightthickness=0, theme_tag='preview') # type: ignore[call-arg]
		def drag_callback(t: int, mouse_event: MouseEvent) -> Callable[[Event], None]:
			def drag(event: Event) -> None:
				self.drag(event, t, mouse_event)
			return drag
		for tt in [0,1]:
			self.canvas.bind(Mouse.Click_Left(), drag_callback(tt, MouseEvent.click))
			self.canvas.bind(Mouse.Drag_Left(), drag_callback(tt, MouseEvent.drag))
			self.canvas.bind(ButtonRelease.Click_Left(), drag_callback(tt, MouseEvent.release))
		self.canvas.pack(side=TOP)
		self.framescroll = Scrollbar(c, orient=HORIZONTAL, command=self.scrolling)
		self.framescroll.set(0,1)
		self.framescroll.pack(side=TOP, fill=X)
		c.pack(side=TOP)
		self.grppanel = SettingsPanel(
			f,
			(
				('Base GRP:',False,'basegrp','CacheGRP',self.updatebasegrp),
				('Overlay GRP:',False,'overlaygrp','CacheGRP',self.updateoverlaygrp)
			),
			self.settings,
			self.mpqhandler,
			self
		)
		self.grppanel.pack(side=TOP)
		x = Frame(f)
		Checkbutton(x, text='Use base GRP', variable=self.usebasegrp, command=self.updateusebase).pack(side=LEFT)
		Checkbutton(x, text='Use overlay GRP', variable=self.useoverlaygrp, command=self.updateuseoverlay).pack(side=RIGHT)
		x.pack(side=TOP, fill=X, padx=5, pady=2)
		f.grid(row=0, column=1, sticky=NS)
		try:
			g = CacheGRP()
			g.load_file(self.mpqhandler.load_file(self.settings.settings.files['basegrp']))
			self.updatebasegrp(g)
		except PyMSError as e:
			if self.usebasegrp.get():
				self.usebasegrp.set(0)
				ErrorDialog(self, e)
		try:
			g = CacheGRP()
			g.load_file(self.mpqhandler.load_file(self.settings.settings.files['overlaygrp']))
			self.updateoverlaygrp(g)
		except PyMSError as e:
			if self.useoverlaygrp.get():
				self.useoverlaygrp.set(0)
				ErrorDialog(self, e)
		self.updategrps()

		m.grid_rowconfigure(0,weight=1)
		m.grid_columnconfigure(0,weight=1)
		m.pack(fill=BOTH, expand=1)

		#Statusbar
		self.status = StringVar()
		self.status.set('Load or create a LO?.')
		self.codestatus = StringVar()
		self.codestatus.set('Line: 1  Column: 0  Selected: 0')
		statusbar = StatusBar(self)
		statusbar.add_label(self.status)
		self.editstatus = statusbar.add_icon(Assets.get_image('save'))
		statusbar.add_spacer()
		statusbar.pack(side=BOTTOM, fill=X)

		self.settings.windows.load_window_size('main', self)

		if guifile:
			self.open(file=guifile)

		UpdateDialog.check_update(self, 'PyLO')

	def scrolling(self, scroll_type: str, amount: str, increment: str | None = None):
		if not self.overlaygrp:
			return
		increments = {'pages':17,'units':1}
		frames = self.overlaygrp.frames-1
		if scroll_type == 'moveto':
			self.overlayframe = int(frames * float(amount))
		elif scroll_type == 'scroll':
			self.overlayframe = min(frames,max(0,(self.overlayframe or 0) + int(amount) * increments[increment or 'units']))
		self.previewupdate()
		self.updatescroll()
		self.framesupdate()

	def updatescroll(self) -> None:
		if self.overlayframe is None or self.overlaygrp is None:
			return
		step = 1 / float(self.overlaygrp.frames)
		self.framescroll.set(self.overlayframe*step, (self.overlayframe+1)*step)

	def updategrps(self) -> None:
		self.grppanel.variables['Base GRP:'][2][1]['state'] = NORMAL if self.usebasegrp.get() else DISABLED
		self.grppanel.variables['Overlay GRP:'][2][1]['state'] = NORMAL if self.useoverlaygrp.get() else DISABLED

	# TODO: What is `t` for?
	def drag(self, event: Event, t, mouse_event: MouseEvent) -> None:
		if not self.previewing_offset:
			return
		if mouse_event == MouseEvent.click:
			self.dragoffset = (self.previewing_offset[0] - event.x,self.previewing_offset[1] - event.y)
			self.text.text.edit_separator()
		elif mouse_event == MouseEvent.drag and self.dragoffset:
			offset = (max(-128,min(127,event.x + self.dragoffset[0])), max(-128,min(127,event.y + self.dragoffset[1])))
			print(offset)
			self.drawpreview(self.previewing_basegrp_frame, offset)
		elif mouse_event == MouseEvent.release:
			s = self.text.index('%s linestart' % INSERT)
			m = RE_DRAG_COORDS.match(self.text.get(s,'%s lineend' % INSERT))
			if m:
				self.pauseupdate = True
				self.text.delete(s,'%s lineend' % INSERT)
				self.text.insert(s,'%s%s%s%s%s' % (m.group(1),self.previewing_offset[0],m.group(2),self.previewing_offset[1],m.group(3)))
				self.pauseupdate = False
			self.dragoffset = None
			self.text.text.edit_separator()

	def updateusebase(self) -> None:
		self.updategrps()
		try:
			g = CacheGRP()
			g.load_file(self.mpqhandler.load_file(self.settings.settings.files['basegrp']))
			self.updatebasegrp(g)
		except PyMSError as e:
			if self.usebasegrp.get():
				self.usebasegrp.set(0)
			ErrorDialog(self, e)

	def updateuseoverlay(self) -> None:
		self.updategrps()
		try:
			g = CacheGRP()
			g.load_file(self.mpqhandler.load_file(self.settings.settings.files['overlaygrp']))
			self.updateoverlaygrp(g)
		except PyMSError as e:
			if self.useoverlaygrp.get():
				self.useoverlaygrp.set(0)
			ErrorDialog(self, e)

	def updatebasegrp(self, grp: CacheGRP) -> None:
		self.basegrp = grp
		self.basegrp_cache.clear()
		self.previewing_basegrp_frame = None
		self.previewing_overlaygrp_frame = None
		self.previewing_offset = None
		self.previewupdate()
		self.framesupdate()

	def updateoverlaygrp(self, grp: CacheGRP) -> None:
		self.overlaygrp = grp
		self.overlaygrp_cache.clear()
		self.previewing_basegrp_frame = None
		self.previewing_overlaygrp_frame = None
		self.previewing_offset = None
		self.previewupdate()
		self.framesupdate()

	def check_saved(self) -> CheckSaved:
		if not self.lo or not self.edited:
			return CheckSaved.saved
		file = self.file
		if not file:
			file = 'Unnamed.loa'
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
		return not not self.lo

	def action_states(self) -> None:
		self.toolbar.tag_enabled('file_open', self.is_file_open())
		self.text['state'] = NORMAL if self.is_file_open() else DISABLED

	def statusupdate(self) -> None:
		line, column = self.text.index(INSERT).split('.')
		selected = 0
		item = self.text.tag_ranges('Selection')
		if item:
			selected = len(self.text.get(*item))
		self.codestatus.set(f'Line: {line}  Column: {column}  Selected: {selected}')
		self.previewupdate()
		self.framesupdate()

	def framesupdate(self) -> None:
		bm = '-'
		om = '-'
		b = '-'
		o = '-'
		if self.basegrp:
			bm = str(self.basegrp.frames)
		if self.previewing_basegrp_frame:
			b = str(self.previewing_basegrp_frame + 1)
		if self.overlaygrp:
			om = str(self.overlaygrp.frames)
		if self.overlayframe is not None:
			o = str(self.overlayframe + 1)
		self.baseframes.set(f'Base Frame: {b} / {bm}')
		self.overlayframes.set(f'Overlay Frame: {o} / {om}')

	def clear_preview(self) -> None:
		self.previewing_basegrp_frame = None
		self.previewing_overlaygrp_frame = None
		self.previewing_offset = None

	def previewupdate(self) -> None:
		if self.pauseupdate:
			return
		m = RE_COORDINATES.match(self.text.get('%s linestart' % INSERT,'%s lineend' % INSERT))
		if m:
			index: str = INSERT
			frame_index = -1
			while True:
				index_range = self.text.tag_prevrange('Header', index)
				if not index_range:
					break
				index = index_range[0]
				frame_index += 1
			if frame_index >= 0:
				self.drawpreview(frame_index, (int(m.group(1)), int(m.group(2))))
				return
		self.canvas.delete(ALL)
		self.clear_preview()

	def base_grp_frame(self, frame_index: int | None) -> (Image | None):
		if frame_index is None or self.basegrp is None:
			return None
		if not frame_index in self.basegrp_cache:
			try:
				self.basegrp_cache[frame_index] = cast(Image, frame_to_photo(self.unitpal.palette, self.basegrp, frame_index, True, False))
			except:
				self.basegrp_cache[frame_index] = None
		return self.basegrp_cache[frame_index]

	def overlay_grp_frame(self, frame_index: int | None) -> (Image | None):
		if frame_index is None or self.overlaygrp is None:
			return None
		if not frame_index in self.overlaygrp_cache:
			try:
				self.overlaygrp_cache[frame_index] = cast(Image, frame_to_photo(self.unitpal.palette, self.overlaygrp, frame_index, True, False))
			except:
				self.overlaygrp_cache[frame_index] = None
		return self.overlaygrp_cache[frame_index]

	def drawpreview(self, frame_index: int | None, offset: tuple[int, int]) -> None:
		if frame_index != self.previewing_basegrp_frame or offset != self.previewing_offset:
			self.canvas.delete(ALL)
			basegrp_image = self.base_grp_frame(frame_index)
			overlaygrp_image = self.overlay_grp_frame(self.overlayframe)
			if self.usebasegrp.get() and basegrp_image:
				self.canvas.create_image(138, 138, image=basegrp_image)
			else:
				self.canvas.create_line((133,138),(144,138),fill='#00FF00')
				self.canvas.create_line((138,133),(138,144),fill='#00FF00')
			if self.useoverlaygrp.get() and overlaygrp_image:
				self.canvas.create_image(138 + offset[0], 138 + offset[1], image=overlaygrp_image)
			else:
				x,y = offset
				self.canvas.create_line((x+133,y+138),(x+144,y+138),fill='#0000FF')
				self.canvas.create_line((x+138,y+133),(x+138,y+144),fill='#0000FF')
			self.previewing_basegrp_frame = frame_index
			self.previewing_overlaygrp_frame = self.overlayframe
			self.previewing_offset = offset

	def edit(self) -> None:
		self.mark_edited()
		self.previewupdate()

	def update_title(self) -> None:
		file_path = self.file
		if not file_path and self.is_file_open():
			file_path = 'Untitled.lo?'
		if not file_path:
			self.title('PyLO %s' % LONG_VERSION)
		else:
			self.title('PyLO %s (%s)' % (LONG_VERSION, file_path))

	def mark_edited(self, edited: bool = True) -> None:
		self.edited = edited
		self.editstatus['state'] = NORMAL if edited else DISABLED

	def new(self):
		if self.check_saved() == CheckSaved.cancelled:
			return
		self.lo = LO()
		self.file = None
		self.status.set('Editing new LO?.')
		self.update_title()
		self.grp_cache = [{},{}]
		self.overlayframe = 0
		self.previewupdate()
		self.updatescroll()
		self.framesupdate()
		self.action_states()
		self.text.delete('1.0', END)
		self.text.insert('1.0', 'Frame:\n\t(0, 0)')
		self.text.edit_reset()
		self.mark_edited(False)

	def open(self, file: str | None = None) -> None:
		if self.check_saved() == CheckSaved.cancelled:
			return
		if file is None:
			file = self.settings.lastpath.lo.select_open_file(self, title='Open LO', filetypes=[FileType.lo(),FileType.loa(),FileType.lob(),FileType.lod(),FileType.lof(),FileType.loo(),FileType.los(),FileType.lou(),FileType.log(),FileType.lol(),FileType.lox()])
			if not file:
				return
		lo = LO()
		d = io.StringIO()
		try:
			lo.load_file(file)
			lo.decompile(d)
		except PyMSError as e:
			ErrorDialog(self, e)
			return
		self.lo = lo
		self.file = file
		self.update_title()
		self.status.set('Load Successful!')
		self.overlayframe = 0
		self.previewupdate()
		self.updatescroll()
		self.action_states()
		self.text.delete('1.0', END)
		self.text.insert('1.0', d.getvalue().rstrip('\n'))
		self.text.edit_reset()
		self.text.see('1.0')
		self.text.mark_set('insert', '2.0 lineend')
		self.mark_edited(False)

	def iimport(self):
		if self.check_saved() == CheckSaved.cancelled:
			return
		file = self.settings.lastpath.txt.select_open_file(self, key='import', title='Import TXT', filetypes=[FileType.txt()])
		if not file:
			return
		try:
			text = open(file,'r').read()
		except:
			ErrorDialog(self, PyMSError('Import', "Couldn't import file '%s'" % file))
			return
		self.lo = LO()
		self.file = file
		self.update_title()
		self.status.set('Import Successful!')
		self.overlayframe = 0
		self.previewupdate()
		self.updatescroll()
		self.framesupdate()
		self.action_states()
		self.text.delete('1.0', END)
		self.text.insert('1.0', text.rstrip('\n'))
		self.text.edit_reset()
		self.mark_edited(False)

	def save(self) -> CheckSaved:
		return self.saveas(file_path=self.file)

	def saveas(self, file_path: str | None = None) -> CheckSaved:
		if not self.lo:
			return CheckSaved.saved
		if not file_path:
			file_path = self.settings.lastpath.lo.select_save_file(self, title='Save LO As', filetypes=[FileType.lo(),FileType.loa(),FileType.lob(),FileType.lod(),FileType.lof(),FileType.loo(),FileType.los(),FileType.lou(),FileType.log(),FileType.lol(),FileType.lox()])
			if not file_path:
				return CheckSaved.cancelled
		elif not check_allow_overwrite_internal_file(file_path):
			return CheckSaved.cancelled
		try:
			text = self.text.get('1.0', END)
			self.lo.interpret(text)
			self.lo.compile(file_path)
		except PyMSError as e:
			ErrorDialog(self, e)
			return CheckSaved.cancelled
		self.file = file_path
		self.update_title()
		self.status.set('Save Successful!')
		self.mark_edited(False)
		return CheckSaved.saved

	def export(self) -> None:
		if not self.lo:
			return
		file = self.settings.lastpath.txt.select_save_file(self, key='export', title='Export TXT', filetypes=[FileType.txt()])
		if not file:
			return
		try:
			self.lo.decompile(file)
			self.status.set('Export Successful!')
		except PyMSError as e:
			ErrorDialog(self, e)

	def test(self) -> None:
		i = LO()
		try:
			text = self.text.get('1.0', END)
			i.interpret(text)
		except PyMSError as e:
			if e.line is not None:
				self.text.see('%s.0' % e.line)
				self.text.tag_add('Error', '%s.0' % e.line, '%s.end' % e.line)
			if e.warnings:
				for w in e.warnings:
					if w.line is not None:
						self.text.tag_add('Warning', '%s.0' % w.line, '%s.end' % w.line)
			ErrorDialog(self, e)
			return
		MessageBox.askquestion(parent=self, title='Test Completed', message='The code compiles with no errors or warnings.', type=MessageBox.OK)

	def close(self) -> None:
		if self.check_saved() == CheckSaved.cancelled:
			return
		self.lo = None
		self.file = None
		self.update_title()
		self.status.set('Load or create a LO?.')
		self.overlayframe = None
		self.previewupdate()
		self.updatescroll()
		self.framesupdate()
		self.grp_cache = [{},{}]
		self.text.delete('1.0', END)
		self.mark_edited(False)
		self.action_states()

	def find(self) -> None:
		if not self.findwindow:
			self.findwindow = FindReplaceDialog(self, self.settings, self)
			self.bind(Key.F3(), self.findwindow.findnext)
		elif self.findwindow.state() == 'withdrawn':
			self.findwindow.deiconify()
		self.findwindow.focus_set()

	def colors(self) -> None:
		c = CodeColors(self, self.text.tags)
		if c.cont:
			self.text.setup(c.cont)

	def mpqsettings(self) -> None:
		SettingsDialog(self, [('Theme',)], (550,380), mpqhandler=self.mpqhandler)

	def register_registry(self) -> None:
		for type,ext in [('Attack','a'),('Birth','b'),('Landing Dust','d'),('Fire','f'),('Powerup','o'),('Shield/Smoke','s'),('Liftoff Dust','u'),('Misc.','g'),('Misc.','l'),('Misc.','x')]:
			try:
				register_registry('PyLO','lo' + ext, type + ' Overlay')
			except PyMSError as e:
				ErrorDialog(self, e)
				break

	def help(self) -> None:
		HelpDialog(self, self.settings, 'Help/Programs/PyLO.md')

	def about(self) -> None:
		AboutDialog(self, 'PyLO', LONG_VERSION)

	def exit(self) -> None:
		if self.check_saved() == CheckSaved.cancelled:
			return
		self.settings.windows.save_window_size('main', self)
		self.settings['highlights'] = self.text.highlights
		# TODO: Better logic
		m = Assets.mpq_file_path('')
		self.settings.settings.files['basegrp'] = ['','MPQ:'][self.grppanel.variables['Base GRP:'][0].get()] + self.grppanel.variables['Base GRP:'][1].get().replace(m,'MPQ:',1)
		self.settings.settings.files['overlaygrp'] = ['','MPQ:'][self.grppanel.variables['Overlay GRP:'][0].get()] + self.grppanel.variables['Overlay GRP:'][1].get().replace(m,'MPQ:',1)
		self.settings['usebasegrp'] = self.usebasegrp.get()
		self.settings['useoverlaygrp'] = self.useoverlaygrp.get()
		self.settings.save()
		self.destroy()

	def destroy(self) -> None:
		if self.findwindow:
			Toplevel.destroy(self.findwindow)
		MainWindow.destroy(self)

	# FindDelegate
	def get_text(self) -> CodeText:
		return self.text
