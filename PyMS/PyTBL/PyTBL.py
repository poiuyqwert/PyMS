
from .FindDialog import FindDialog
from .GotoDialog import GotoDialog
from .PreviewDialog import PreviewDialog

from ..FileFormats import TBL
from ..FileFormats import PCX
from ..FileFormats import FNT
from ..FileFormats import Palette
from ..FileFormats import GRP

from ..Utilities.utils import VERSIONS, BASE_DIR, WIN_REG_AVAILABLE, register_registry
from ..Utilities.UIKit import *
from ..Utilities.analytics import ga, GAScreen
from ..Utilities.trace import setup_trace
from ..Utilities.Settings import Settings
from ..Utilities.Toolbar import Toolbar
from ..Utilities import Assets
from ..Utilities.MPQHandler import MPQHandler
from ..Utilities.UpdateDialog import UpdateDialog
from ..Utilities.PyMSError import PyMSError
from ..Utilities.ErrorDialog import ErrorDialog
from ..Utilities.SettingsDialog import SettingsDialog
from ..Utilities.AboutDialog import AboutDialog
from ..Utilities.ScrolledListbox import ScrolledListbox
from ..Utilities.StatusBar import StatusBar

import os, webbrowser

LONG_VERSION = 'v%s' % VERSIONS['PyTBL']

class PyTBL(MainWindow):
	def __init__(self, guifile=None):
		MainWindow.__init__(self)
		self.title('PyTBL %s' % LONG_VERSION)
		self.set_icon('PyTBL')
		self.protocol('WM_DELETE_WINDOW', self.exit)
		ga.set_application('PyTBL', VERSIONS['PyTBL'])
		ga.track(GAScreen('PyTBL'))
		setup_trace(self, 'PyTBL')
		
		self.settings = Settings('PyTBL', '1')
		self.settings.settings.files.set_defaults({
			'tfontgam':'MPQ:game\\tfontgam.pcx',
			'font8':'MPQ:font\\font8.fnt',
			'font10':'MPQ:font\\font10.fnt',
			'icons':'MPQ:game\\icons.grp',
			'unitpal':os.path.join(BASE_DIR,'Palettes','Units.pal'),
		})

		self.tbl = None
		self.file = None
		self.edited = False
		self.findhistory = []
		self.findwindow = None
		self.gotohistory = []
		self.gotowindow = None
		self.tfontgam = None
		self.font8 = None
		self.font10 = None
		self.unitpal = None
		self.icons = None

		self.listmenu = Menu(self, tearoff=0)
		self.listmenu.add_command(label='Add String', command=self.add, shortcut=Key.Insert, bind_shortcut=False)
		self.listmenu.add_command(label='Insert String', command=self.insert, shortcut=Shift.Insert, bind_shortcut=False)
		self.listmenu.add_command(label='Remove String', command=self.remove, shortcut=Key.Delete, tags='string_selected', bind_shortcut=False)
		self.listmenu.add_separator()
		self.listmenu.add_command(label='Move String Up', command=lambda: self.movestring(None,0), shortcut=Shift.Up, bind_shortcut=False)
		self.listmenu.add_command(label='Move String Down', command=lambda: self.movestring(None,1), shortcut=Shift.Down, bind_shortcut=False)

		self.toolbar = Toolbar(self)
		self.toolbar.add_button(Assets.get_image('new'), self.new, 'New', Ctrl.n)
		self.toolbar.add_gap()
		self.toolbar.add_button(Assets.get_image('open'), self.open, 'Open', Ctrl.o)
		self.toolbar.add_button(Assets.get_image('opendefault'), self.open_default, 'Open Default TBL', Ctrl.d)
		self.toolbar.add_button(Assets.get_image('import'), self.iimport, 'Import Strings', Ctrl.i)
		self.toolbar.add_gap()
		self.toolbar.add_button(Assets.get_image('save'), self.save, 'Save', Ctrl.s, enabled=False, tags='file_open')
		self.toolbar.add_button(Assets.get_image('saveas'), self.saveas, 'Save As', Ctrl.Alt.a, enabled=False, tags='file_open')
		self.toolbar.add_button(Assets.get_image('export'), self.export, 'Export Strings', Ctrl.e, enabled=False, tags='file_open')
		self.toolbar.add_gap()
		self.toolbar.add_button(Assets.get_image('close'), self.close, 'Close', Ctrl.w, enabled=False, tags='file_open')
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('add'), self.add, 'Add String', Key.Insert, enabled=False, tags='file_open')
		self.toolbar.add_button(Assets.get_image('insert'), self.insert, 'Insert String', Shift.Insert, enabled=False, tags='string_selected')
		self.toolbar.add_button(Assets.get_image('remove'), self.remove, 'Remove String (Delete in Listbox, Shift+Delete in Textbox)', Shift.Delete, enabled=False, tags='string_selected', add_shortcut_to_tooltip=False)
		self.toolbar.add_gap()
		self.toolbar.add_button(Assets.get_image('up'), lambda e=None: self.movestring(e,0), 'Move String Up', Shift.Up, enabled=False, tags='string_selected', bind_shortcut=False)
		self.toolbar.add_button(Assets.get_image('down'), lambda e=None: self.movestring(e,1), 'Move String Down', Shift.Down, enabled=False, tags='string_selected', bind_shortcut=False)
		self.toolbar.add_gap()
		self.toolbar.add_button(Assets.get_image('find'), self.find, 'Find Strings', Ctrl.f, enabled=False, tags='file_open')
		self.toolbar.add_button(Assets.get_image('ffw'), self.goto, 'Go to', Ctrl.g, enabled=False, tags='file_open')
		self.toolbar.add_gap()
		self.toolbar.add_button(Assets.get_image('test'), self.preview, 'Test String', Ctrl.t, enabled=False, tags='string_selected')
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('asc3topyai'), self.mpqsettings, 'Manage Settings', Ctrl.m)
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('register'), self.register, 'Set as default *.tbl editor (Windows Only)', enabled=WIN_REG_AVAILABLE)
		self.toolbar.add_button(Assets.get_image('help'), self.help, 'Help', Key.F1)
		self.toolbar.add_button(Assets.get_image('about'), self.about, 'About PyTBL')
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('exit'), self.exit, 'Exit', Alt.F4)
		self.toolbar.grid(row=0,column=0, padx=1,pady=1, sticky=EW)

		self.bind_all(Shift.Up, lambda e,i=0: self.movestring(e,i))
		self.bind_all(Shift.Down, lambda e,i=1: self.movestring(e,i))

		self.hor_pane = PanedWindow(self,orient=HORIZONTAL)

		# listbox
		self.listbox = ScrolledListbox(self.hor_pane, scroll_speed=2, width=35, height=1, bd=0, highlightthickness=0, exportselection=0, activestyle=DOTBOX)
		self.listbox.pack(side=LEFT, fill=BOTH, expand=1)
		self.hor_pane.add(self.listbox, sticky=NSEW, minsize=200)
		self.listbox.bind('<<ListboxSelect>>', lambda e: self.update(e))
		self.listbox.bind(Mouse.Click_Right, self.popup)

		# Textbox
		self.ver_pane = PanedWindow(self.hor_pane,orient=VERTICAL)
		textframe = Frame(self.ver_pane, bd=2, relief=SUNKEN)
		hscroll = Scrollbar(textframe, orient=HORIZONTAL)
		vscroll = Scrollbar(textframe)
		self.text = Text(textframe, height=1, bd=0, undo=1, maxundo=100, wrap=NONE, highlightthickness=0, xscrollcommand=hscroll.set, yscrollcommand=vscroll.set, exportselection=0, state=DISABLED)
		self.text.orig = self.text._w + '_orig'
		self.tk.call('rename', self.text._w, self.text.orig)
		self.tk.createcommand(self.text._w, self.dispatch)
		self.text.mark_set('textend', '1.0')
		self.text.mark_gravity('textend', RIGHT)
		self.text.grid(sticky=NSEW)
		self.text.bind(Ctrl.a, lambda e: self.after(1, self.selectall))
		hscroll.config(command=self.text.xview)
		hscroll.grid(sticky=EW)
		vscroll.config(command=self.text.yview)
		vscroll.grid(sticky=NS, row=0, column=1)
		textframe.grid_rowconfigure(0, weight=1)
		textframe.grid_columnconfigure(0, weight=1)
		self.ver_pane.add(textframe, sticky=NSEW)
		colors = Frame(self.ver_pane, bd=2, relief=SUNKEN)
		hscroll = Scrollbar(colors, orient=HORIZONTAL)
		vscroll = Scrollbar(colors)
		text = Text(colors, height=1, bd=0, undo=1, maxundo=100, wrap=NONE, highlightthickness=0, xscrollcommand=hscroll.set, yscrollcommand=vscroll.set, exportselection=0)
		text.insert(END, '\n'.join([l[2:] for l in TBL.TBL_REF.split('\n')[1:-2]]))
		text['state'] = DISABLED
		text.grid(sticky=NSEW)
		hscroll.config(command=text.xview)
		hscroll.grid(sticky=EW)
		vscroll.config(command=text.yview)
		vscroll.grid(sticky=NS, row=0, column=1)
		colors.grid_rowconfigure(0, weight=1)
		colors.grid_columnconfigure(0, weight=1)
		self.ver_pane.add(colors, sticky=NSEW)
		# self.ver_pane.pack(side=LEFT, fill=BOTH, expand=1)
		self.hor_pane.add(self.ver_pane, sticky=NSEW, minsize=200)

		self.hor_pane.grid(row=1,column=0, sticky=NSEW)

		#Statusbar
		self.status = StringVar()
		self.status.set('Load or create a TBL.')
		self.stringstatus = StringVar()
		statusbar = StatusBar(self)
		statusbar.add_label(self.status)
		self.editstatus = statusbar.add_icon(PhotoImage(file=os.path.join(BASE_DIR,'PyMS','Images','save.gif')))
		statusbar.add_label(self.stringstatus)
		statusbar.grid(row=2,column=0, sticky=EW)

		self.grid_columnconfigure(0, weight=1)
		self.grid_rowconfigure(1, weight=1)

		self.settings.windows.load_window_size('main', self)
		self.settings.panes.load_pane_size('stringlist', self.hor_pane)
		self.settings.panes.load_pane_size('colorlist', self.ver_pane)

		self.mpqhandler = MPQHandler(self.settings.get('mpqs',[]))
		if (not 'mpqs' in self.settings or not len(self.settings['mpqs'])) and self.mpqhandler.add_defaults():
			self.settings['mpqs'] = self.mpqhandler.mpqs
		e = self.open_files()

		if guifile:
			self.open(file=guifile)

		UpdateDialog.check_update(self, 'PyTBL')

		if e:
			self.mpqsettings(err=e)

	def open_files(self):
		self.mpqhandler.open_mpqs()
		err = None
		try:
			tfontgam = PCX.PCX()
			font8 = FNT.FNT()
			font10 = FNT.FNT()
			unitpal = Palette.Palette()
			icons = GRP.GRP()
			tfontgam.load_file(self.mpqhandler.get_file(self.settings.settings.files.get('tfontgam')))
			try:
				font8.load_file(self.mpqhandler.get_file(self.settings.settings.files.get('font8'), False))
			except:
				font8.load_file(self.mpqhandler.get_file(self.settings.settings.files.get('font8'), True))
			try:
				font10.load_file(self.mpqhandler.get_file(self.settings.settings.files.get('font10'), False))
			except:
				font10.load_file(self.mpqhandler.get_file(self.settings.settings.files.get('font10'), True))
			unitpal.load_file(self.mpqhandler.get_file(self.settings.settings.files.get('unitpal')))
			icons.load_file(self.mpqhandler.get_file(self.settings.settings.files.get('icons')))
		except PyMSError as e:
			err = e
		else:
			self.tfontgam = tfontgam
			self.font8 = font8
			self.font10 = font10
			self.unitpal = unitpal
			self.icons = icons
		self.mpqhandler.close_mpqs()
		return err

	def scroll(self, e):
		if e.delta > 0:
			self.listbox.yview('scroll', -2, 'units')
		else:
			self.listbox.yview('scroll', 2, 'units')

	def move(self, e, a):
		if a == END:
			a = self.listbox.size()-2
		elif a not in [0,END]:
			a = max(min(self.listbox.size()-1, int(self.listbox.curselection()[0]) + a),0)
		self.listbox.select_clear(0,END)
		self.listbox.select_set(a)
		self.listbox.see(a)
		self.update()

	def update(self, e=None, i=None, status=False):
		if self.listbox.size():
			if i:
				i.focus_set()
			s = int(self.listbox.curselection()[0])
			if not status:
				self.text_delete('1.0', END)
				self.text_insert('1.0', TBL.decompile_string(self.tbl.strings[s], '\n'))
			self.stringstatus.set('String: %s / %s' % (s+1,self.listbox.size()))

	def popup(self, e):
		if self.tbl:
			self.listmenu.tag_enabled('string_selected', self.is_string_selected())
			self.listmenu.post(e.x_root, e.y_root)

	def selectall(self, e=None):
		self.text.tag_remove(SEL, '1.0', END)
		self.text.tag_add(SEL, '1.0', END)
		self.text.mark_set(INSERT, '1.0')

	def unsaved(self):
		if self.tbl and self.edited:
			file = self.file
			if not file:
				file = 'Unnamed.tbl'
			save = MessageBox.askquestion(parent=self, title='Save Changes?', message="Save changes to '%s'?" % file, default=MessageBox.YES, type=MessageBox.YESNOCANCEL)
			if save != MessageBox.NO:
				if save == MessageBox.CANCEL:
					return True
				if self.file:
					self.save()
				else:
					self.saveas()

	def is_file_open(self):
		return not not self.tbl

	def is_string_selected(self):
		return not not self.listbox.curselection()

	def action_states(self):
		file_open = self.is_file_open()
		string_selected = self.is_string_selected()
		self.toolbar.tag_enabled('file_open', file_open)
		self.text['state'] = NORMAL if string_selected else DISABLED
		self.toolbar.tag_enabled('string_selected', string_selected)

	def text_insert(self, pos, text):
		self.tk.call((self.text.orig, 'insert', pos, text))

	def text_delete(self, start, end=None):
		self.tk.call((self.text.orig, 'delete', start, end))

	def dispatch(self, cmd, *args):
		try:
			r = self.tk.call((self.text.orig, cmd) + args)
		except TclError:
			r = ''
		if self.listbox.size() and cmd in ['insert','delete']:
			if not self.edited:
				self.edited = True
				self.editstatus['state'] = NORMAL
			i = int(self.listbox.curselection()[0])
			self.tbl.strings[i] = TBL.compile_string(self.text.get('1.0','textend'))
			self.listbox.delete(i)
			self.listbox.insert(i, TBL.decompile_string(self.tbl.strings[i]))
			self.listbox.select_set(i)
		return r

	def new(self, key=None):
		if not self.unsaved():
			self.tbl = TBL.TBL()
			self.file = None
			self.status.set('Editing new TBL.')
			self.edited = False
			self.editstatus['state'] = DISABLED
			self.title('PyTBL %s (Unnamed.tbl)' % LONG_VERSION)
			if self.listbox.size():
				self.text_delete('1.0', END)
			self.listbox.delete(0, END)
			self.stringstatus.set('')
			self.action_states()

	def open(self, key=None, file=None):
		if not self.unsaved():
			if not file:
				file = self.settings.lastpath.tbl.select_open_file(self, title='Open TBL', filetypes=(('StarCraft TBL Files','*.tbl'),))
				if not file:
					return
			tbl = TBL.TBL()
			try:
				tbl.load_file(file)
			except PyMSError as e:
				ErrorDialog(self, e)
				return
			self.tbl = tbl
			self.title('PyTBL %s (%s)' % (LONG_VERSION,file))
			self.listbox.delete(0, END)
			self.text_delete('1.0', END)
			for string in self.tbl.strings:
				self.listbox.insert(END, TBL.decompile_string(string))
			if self.listbox.size():
				self.listbox.select_set(0)
				self.listbox.see(0)
			self.file = file
			self.status.set('Load Successful!')
			self.edited = False
			self.editstatus['state'] = DISABLED
			self.action_states()
			self.update()

	def open_default(self, key=None):
		self.open(key, os.path.join(BASE_DIR, 'PyMS', 'MPQ', 'rez','stat_txt.tbl'))

	def iimport(self, key=None):
		if not self.unsaved():
			file = self.settings.lastpath.txt.select_open_file(self, key='import', title='Import TXT', filetypes=(('Text Files','*.txt'),))
			if not file:
				return
			tbl = TBL.TBL()
			try:
				tbl.interpret(file)
			except PyMSError as e:
				ErrorDialog(self, e)
				return
			self.tbl = tbl
			self.title('PyTBL %s (%s)' % (LONG_VERSION,file))
			self.listbox.delete(0, END)
			self.text_delete('1.0', END)
			for string in self.tbl.strings:
				self.listbox.insert(END, TBL.decompile_string(string))
			if self.listbox.size():
				self.listbox.select_set(0)
				self.listbox.see(0)
			self.file = file
			self.status.set('Import Successful!')
			self.edited = False
			self.editstatus['state'] = DISABLED
			self.action_states()
			self.update()

	def save(self, key=None):
		if not self.is_file_open():
			return
		if self.file == None:
			self.saveas()
			return
		try:
			self.tbl.compile(self.file)
			self.status.set('Save Successful!')
			self.edited = False
			self.editstatus['state'] = DISABLED
		except PyMSError as e:
			ErrorDialog(self, e)

	def saveas(self, key=None):
		if not self.is_file_open():
			return
		file = self.settings.lastpath.tbl.select_save_file(self, title='Save TBL As', filetypes=(('StarCraft TBL Files','*.tbl'),))
		if not file:
			return True
		self.file = file
		self.save()

	def export(self, key=None):
		if not self.is_file_open():
			return
		file = self.settings.lastpath.txt.select_save_file(self, key='export', title='Export TXT', filetypes=(('Text Files','*.txt'),))
		if not file:
			return True
		try:
			self.tbl.decompile(file)
			self.status.set('Export Successful!')
		except PyMSError as e:
			ErrorDialog(self, e)

	def close(self, key=None):
		if not self.is_file_open():
			return
		if not self.unsaved():
			self.tbl = None
			self.title('PyTBL %s' % LONG_VERSION)
			self.file = None
			self.status.set('Load or create a TBL.')
			self.edited = False
			self.editstatus['state'] = DISABLED
			self.listbox.delete(0, END)
			self.text_delete('1.0', END)
			self.stringstatus.set('')
			self.action_states()

	def add(self, key=None, i=END):
		if not self.is_file_open():
			return
		if i == END:
			self.tbl.strings.append('')
		else:
			self.tbl.strings.insert(i, '')
		self.listbox.insert(i, '')
		self.listbox.select_clear(0, END)
		self.listbox.select_set(i)
		self.listbox.see(i)
		self.edited = True
		self.editstatus['state'] = NORMAL
		self.action_states()
		self.update()

	def insert(self, key=None):
		if not self.is_string_selected():
			return
		self.add(None, int(self.listbox.curselection()[0]))

	def remove(self, key=None):
		if not self.is_string_selected():
			return
		i = int(self.listbox.curselection()[0])
		del self.tbl.strings[i]
		self.listbox.delete(i)
		if self.listbox.size():
			i = min(i,self.listbox.size()-1)
			self.listbox.select_set(i)
			self.listbox.see(i)
		self.edited = True
		self.editstatus['state'] = NORMAL
		self.action_states()
		self.update()

	def movestring(self, key=None, dir=0):
		if not self.is_string_selected():
			return
		i = int(self.listbox.curselection()[0])
		if i == [0,self.listbox.size()-1][dir]:
			return
		self.listbox.delete(i)
		n = i + [-1,1][dir]
		s = self.tbl.strings[i]
		self.listbox.insert(n, TBL.decompile_string(s))
		self.listbox.select_clear(0, END)
		self.listbox.select_set(n)
		self.listbox.see(n)
		self.tbl.strings[i] = self.tbl.strings[n]
		self.tbl.strings[n] = s
		self.edited = True
		self.editstatus['state'] = NORMAL
		self.action_states()
		self.update(status=True)

	def find(self, key=None):
		if not self.is_file_open():
			return
		if not self.findwindow:
			self.findwindow = FindDialog(self)
			self.bind(Key.F3, self.findwindow.findnext)
		else:
			self.findwindow.make_active()
			self.findwindow.findentry.focus_set(highlight=True)

	def goto(self, key=None):
		if not self.is_file_open():
			return
		if not self.gotowindow:
			self.gotowindow = GotoDialog(self)
		else:
			self.gotowindow.make_active()
			self.gotowindow.gotoentry.focus_set(highlight=True)

	def preview(self, key=None):
		if not self.is_string_selected():
			return
		PreviewDialog(self)

	def mpqsettings(self, key=None, err=None):
		data = [
			('Preview Settings',[
				('tfontgam.pcx','The special palette which holds text colors.','tfontgam','PCX'),
				('font8.fnt','The font used to preview hotkeys','font8','FNT'),
				('font10.fnt','The font used to preview strings other than hotkeys','font10','FNT'),
				('icons.grp','The icons used to preview hotkeys','icons','GRP'),
				('Unit Palette','The palette used to display icons.grp','unitpal','Palette'),
			])
		]
		SettingsDialog(self, data, (340,430), err, mpqhandler=self.mpqhandler)

	def register(self, e=None):
		try:
			register_registry('PyTBL','','tbl',os.path.join(BASE_DIR, 'PyTBL.pyw'),os.path.join(BASE_DIR,'PyMS','Images','PyTBL.ico'))
		except PyMSError as e:
			ErrorDialog(self, e)

	def help(self, e=None):
		webbrowser.open('file:///%s' % os.path.join(BASE_DIR, 'Docs', 'PyTBL.html'))

	def about(self, key=None):
		AboutDialog(self, 'PyTBL', LONG_VERSION)

	def exit(self, e=None):
		if not self.unsaved():
			self.settings.panes.save_pane_size('stringlist', self.hor_pane)
			self.settings.panes.save_pane_size('colorlist', self.ver_pane)
			self.settings.windows.save_window_size('main', self)
			self.settings.save()
			self.destroy()

	def destroy(self):
		if self.gotowindow != None:
			Toplevel.destroy(self.gotowindow)
		if self.findwindow != None:
			Toplevel.destroy(self.findwindow)
		MainWindow.destroy(self)
