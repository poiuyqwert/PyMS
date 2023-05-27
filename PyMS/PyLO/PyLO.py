
from .LOCodeText import LOCodeText
from .FindReplaceDialog import FindReplaceDialog
from .CodeColors import CodeColors
from .Constants import RE_COORDINATES, RE_DRAG_COORDS

from ..FileFormats.LO import LO
from ..FileFormats.Palette import Palette
from ..FileFormats.GRP import CacheGRP, frame_to_photo

from ..Utilities.utils import WIN_REG_AVAILABLE, register_registry, FFile
from ..Utilities.UIKit import *
from ..Utilities.Settings import Settings
from ..Utilities.analytics import ga, GAScreen
from ..Utilities.trace import setup_trace
from ..Utilities import Assets
from ..Utilities.MPQHandler import MPQHandler
from ..Utilities.SettingsPanel import SettingsPanel
from ..Utilities.PyMSError import PyMSError
from ..Utilities.ErrorDialog import ErrorDialog
from ..Utilities.UpdateDialog import UpdateDialog
from ..Utilities.WarningDialog import WarningDialog
from ..Utilities.SettingsDialog import SettingsDialog
from ..Utilities.AboutDialog import AboutDialog
from ..Utilities.HelpDialog import HelpDialog
from ..Utilities.fileutils import check_allow_overwrite_internal_file

LONG_VERSION = 'v%s' % Assets.version('PyLO')

class PyLO(MainWindow):
	def __init__(self, guifile=None):
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

		self.lo = None
		self.file = None
		self.edited = False
		self.findhistory = []
		self.replacehistory = []
		self.findwindow = None
		self.basegrp = None
		self.overlaygrp = None
		self.unitpal = Palette()
		self.unitpal.load_file(Assets.palette_file_path('Units.pal'))
		self.previewing = None
		self.overlayframe = None
		self.dragoffset = None
		self.pauseupdate = False
		self.grp_cache = [{},{}]

		self.update_title()

		#Toolbar
		self.toolbar = Toolbar(self)
		self.toolbar.add_button(Assets.get_image('new'), self.new, 'New', Ctrl.n)
		self.toolbar.add_gap()
		self.toolbar.add_button(Assets.get_image('open'), self.open, 'Open', Ctrl.o)
		self.toolbar.add_button(Assets.get_image('import'), self.iimport, 'Import LO?', Ctrl.i)
		self.toolbar.add_gap()
		self.toolbar.add_button(Assets.get_image('save'), self.save, 'Save', Ctrl.s, enabled=False, tags='file_open')
		self.toolbar.add_button(Assets.get_image('saveas'), self.saveas, 'Save As', Ctrl.Alt.a, enabled=False, tags='file_open')
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
		self.toolbar.add_button(Assets.get_image('register'), self.register, 'Set as default *.lo? editor (Windows Only)', enabled=WIN_REG_AVAILABLE)
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
		self.canvas = Canvas(c, borderwidth=0, width=275, height=275, background='#000000', highlightthickness=0, theme_tag='preview')
		for tt in [0,1]:
			self.canvas.bind(Mouse.Click_Left, lambda e,t=tt: self.drag(e,t,0))
			self.canvas.bind(Mouse.Drag_Left, lambda e,t=tt: self.drag(e,t,1))
			self.canvas.bind(ButtonRelease.Click_Left, lambda e,t=tt: self.drag(e,t,2))
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
			g.load_file(self.mpqhandler.get_file(self.settings.settings.files['basegrp']))
			self.updatebasegrp(g)
		except PyMSError as e:
			if self.usebasegrp.get():
				self.usebasegrp.set(0)
				ErrorDialog(self, e)
		try:
			g = CacheGRP()
			g.load_file(self.mpqhandler.get_file(self.settings.settings.files['overlaygrp']))
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

	def scrolling(self, t, p, e=None):
		a = {'pages':17,'units':1}
		frames = self.overlaygrp.frames-1
		if t == 'moveto':
			self.overlayframe = int(frames * float(p))
		elif t == 'scroll':
			self.overlayframe = min(frames,max(0,self.overlayframe + int(p) * a[e]))
		self.previewupdate()
		self.updatescroll()
		self.framesupdate()

	def updatescroll(self):
		if self.overlayframe is not None and self.overlaygrp is not None:
			frames = float(self.overlaygrp.frames)
			step = 1 / frames
			self.framescroll.set(self.overlayframe*step, (self.overlayframe+1)*step)

	def updategrps(self):
		self.grppanel.variables['Base GRP:'][2][1]['state'] = [DISABLED,NORMAL][self.usebasegrp.get()]
		self.grppanel.variables['Overlay GRP:'][2][1]['state'] = [DISABLED,NORMAL][self.useoverlaygrp.get()]

	def drag(self, e, t, c):
		if c == 0 and self.previewing:
			self.dragoffset = (self.previewing[2] - e.x,self.previewing[3] - e.y)
			self.text.text.edit_separator()
		elif c == 1 and self.previewing and self.dragoffset:
			p = [max(-128,min(127,e.x + self.dragoffset[0])),max(-128,min(127,e.y + self.dragoffset[1]))]
			self.drawpreview(self.previewing[0],p)
		elif c == 2:
			s = self.text.index('%s linestart' % INSERT)
			m = RE_DRAG_COORDS.match(self.text.get(s,'%s lineend' % INSERT))
			if m:
				self.pauseupdate = True
				self.text.delete(s,'%s lineend' % INSERT)
				self.text.insert(s,'%s%s%s%s%s' % (m.group(1),self.previewing[2],m.group(2),self.previewing[3],m.group(3)))
				self.pauseupdate = False
			self.dragoffset = None
			self.text.text.edit_separator()

	def updateusebase(self):
		self.updategrps()
		try:
			g = CacheGRP()
			g.load_file(self.mpqhandler.get_file(self.settings.settings.files['basegrp']))
			self.updatebasegrp(g)
		except PyMSError as e:
			if self.usebasegrp.get():
				self.usebasegrp.set(0)
			ErrorDialog(self, e)

	def updateuseoverlay(self):
		self.updategrps()
		try:
			g = CacheGRP()
			g.load_file(self.mpqhandler.get_file(self.settings.settings.files['overlaygrp']))
			self.updateoverlaygrp(g)
		except PyMSError as e:
			if self.useoverlaygrp.get():
				self.useoverlaygrp.set(0)
			ErrorDialog(self, e)

	def updatebasegrp(self, grp):
		self.basegrp = grp
		self.grp_cache[0] = {}
		self.previewing = None
		self.previewupdate()
		self.framesupdate()

	def updateoverlaygrp(self, grp):
		self.overlaygrp = grp
		self.grp_cache[1] = {}
		self.previewing = None
		self.previewupdate()
		self.framesupdate()

	def unsaved(self):
		if self.lo and self.edited:
			file = self.file
			if not file:
				file = 'Unnamed.loa'
			save = MessageBox.askquestion(parent=self, title='Save Changes?', message="Save changes to '%s'?" % file, default=MessageBox.YES, type=MessageBox.YESNOCANCEL)
			if save != MessageBox.NO:
				if save == MessageBox.CANCEL:
					return True
				if self.file:
					self.save()
				else:
					self.saveas()

	def is_file_open(self):
		return not not self.lo

	def action_states(self):
		self.toolbar.tag_enabled('file_open', self.is_file_open())
		self.text['state'] = NORMAL if self.is_file_open() else DISABLED # TODO: Better edited status?

	def statusupdate(self):
		i = self.text.index(INSERT).split('.') + [0]
		item = self.text.tag_ranges('Selection')
		if item:
			i[2] = len(self.text.get(*item))
		self.codestatus.set('Line: %s  Column: %s  Selected: %s' % tuple(i))
		self.previewupdate()
		self.framesupdate()

	def framesupdate(self):
		bm,om,b,o = '-'*4
		if self.basegrp:
			bm = self.basegrp.frames
		if self.previewing:
			b = self.previewing[0] + 1
		if self.overlaygrp:
			om = self.overlaygrp.frames
		if self.overlayframe is not None:
			o = self.overlayframe + 1
		self.baseframes.set('Base Frame: %s / %s' % (b,bm))
		self.overlayframes.set('Overlay Frame: %s / %s' % (o,om))

	def previewupdate(self):
		if not self.pauseupdate:
			m = RE_COORDINATES.match(self.text.get('%s linestart' % INSERT,'%s lineend' % INSERT))
			if m:
				i = INSERT
				f = -1
				while True:
					i = self.text.tag_prevrange('Header',i)
					if not i:
						break
					i = i[0]
					f += 1
				if f >= 0:
					self.drawpreview(f,list(int(n) for n in m.groups()))
					return
			self.canvas.delete(ALL)
			self.previewing = None

	def grp(self, f, t):
		if f is not None:
			if not f in self.grp_cache[t]:
				try:
					self.grp_cache[t][f] = frame_to_photo(self.unitpal.palette, [self.basegrp,self.overlaygrp][t], f, True, False)
				except:
					self.grp_cache[t][f] = None
			return self.grp_cache[t][f]

	def drawpreview(self, f, offset):
		if [f,self.overlayframe]+offset != self.previewing:
			self.canvas.delete(ALL)
			base,overlay = self.grp(f,0),self.grp(self.overlayframe,1)
			if self.usebasegrp.get() and base:
				self.canvas.create_image(138, 138, image=base)
			else:
				self.canvas.create_line(133,138,144,138,fill='#00FF00')
				self.canvas.create_line(138,133,138,144,fill='#00FF00')
			if self.useoverlaygrp.get() and overlay:
				self.canvas.create_image(138 + offset[0], 138 + offset[1], image=overlay)
			else:
				x,y = offset
				self.canvas.create_line(x+133,y+138,x+144,y+138,fill='#0000FF')
				self.canvas.create_line(x+138,y+133,x+138,y+144,fill='#0000FF')
			self.previewing = [f,self.overlayframe]+offset

	def edit(self):
		self.mark_edited()
		self.previewupdate()

	def update_title(self):
		file_path = self.file
		if not file_path and self.is_file_open():
			file_path = 'Untitled.lo?'
		if not file_path:
			self.title('PyLO %s' % LONG_VERSION)
		else:
			self.title('PyLO %s (%s)' % (LONG_VERSION, file_path))

	def mark_edited(self, edited=True):
		self.edited = edited
		self.editstatus['state'] = NORMAL if edited else DISABLED

	def new(self, key=None):
		if not self.unsaved():
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

	def open(self, key=None, file=None):
		if not self.unsaved():
			if file is None:
				file = self.settings.lastpath.lo.select_open_file(self, title='Open LO', filetypes=[FileType.lo(),FileType.loa(),FileType.lob(),FileType.lod(),FileType.lof(),FileType.loo(),FileType.los(),FileType.lou(),FileType.log(),FileType.lol(),FileType.lox()])
				if not file:
					return
			lo = LO()
			d = FFile()
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
			self.text.insert('1.0', d.data.rstrip('\n'))
			self.text.edit_reset()
			self.text.see('1.0')
			self.text.mark_set('insert', '2.0 lineend')
			self.mark_edited(False)

	def iimport(self, key=None):
		if not self.unsaved():
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

	def save(self, key=None):
		self.saveas(file_path=self.file)

	def saveas(self, key=None, file_path=None):
		if not file_path:
			file_path = self.settings.lastpath.lo.select_save_file(self, title='Save LO As', filetypes=[FileType.lo(),FileType.loa(),FileType.lob(),FileType.lod(),FileType.lof(),FileType.loo(),FileType.los(),FileType.lou(),FileType.log(),FileType.lol(),FileType.lox()])
			if not file_path:
				return
		elif not check_allow_overwrite_internal_file(file_path):
			return
		try:
			self.lo.interpret(self.text)
			self.lo.compile(file_path)
		except PyMSError as e:
			ErrorDialog(self, e)
			return
		self.file = file_path
		self.update_title()
		self.status.set('Save Successful!')
		self.mark_edited(False)

	def export(self, key=None):
		file = self.settings.lastpath.txt.select_save_file(self, key='export', title='Export TXT', filetypes=[FileType.txt()])
		if not file:
			return True
		try:
			self.lo.decompile(file)
			self.status.set('Export Successful!')
		except PyMSError as e:
			ErrorDialog(self, e)

	def test(self, key=None):
		i = LO()
		try:
			warnings = i.interpret(self)
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
		if warnings:
			c = False
			for w in warnings:
				if w.line is not None:
					if not c:
						self.text.see('%s.0' % w.line)
						c = True
					self.text.tag_add('Warning', '%s.0' % w.line, '%s.end' % w.line)
			WarningDialog(self, warnings, True)
		else:
			MessageBox.askquestion(parent=self, title='Test Completed', message='The code compiles with no errors or warnings.', type=MessageBox.OK)

	def close(self, key=None):
		if not self.unsaved():
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

	def find(self, key=None):
		if not self.findwindow:
			self.findwindow = FindReplaceDialog(self)
			self.bind(Key.F3, self.findwindow.findnext)
		elif self.findwindow.state() == 'withdrawn':
			self.findwindow.deiconify()
		self.findwindow.focus_set()

	def colors(self, key=None):
		c = CodeColors(self)
		if c.cont:
			self.text.setup(c.cont)

	def mpqsettings(self, key=None):
		SettingsDialog(self, [('Theme',)], (550,380), mpqhandler=self.mpqhandler)

	def register(self, e=None):
		for type,ext in [('Attack','a'),('Birth','b'),('Landing Dust','d'),('Fire','f'),('Powerup','o'),('Shield/Smoke','s'),('Liftoff Dust','u'),('Misc.','g'),('Misc.','l'),('Misc.','x')]:
			try:
				register_registry('PyLO','lo' + ext, type + ' Overlay')
			except PyMSError as e:
				ErrorDialog(self, e)
				break

	def help(self, e=None):
		HelpDialog(self, self.settings, 'Help/Programs/PyLO.md')

	def about(self, key=None):
		AboutDialog(self, 'PyLO', LONG_VERSION)

	def exit(self, e=None):
		if not self.unsaved():
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

	def readlines(self):
		return self.text.get('1.0', END).split('\n')

	def destroy(self):
		if self.findwindow:
			Toplevel.destroy(self.findwindow)
		MainWindow.destroy(self)
