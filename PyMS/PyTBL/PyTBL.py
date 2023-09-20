
from .Config import PyTBLConfig
from .Delegates import MainDelegate
from .FindDialog import FindDialog
from .GotoDialog import GotoDialog
from .PreviewDialog import PreviewDialog
from .SettingsUI.SettingsDialog import SettingsDialog

from ..FileFormats import TBL
from ..FileFormats import PCX
from ..FileFormats import FNT
from ..FileFormats import Palette
from ..FileFormats import GRP

from ..Utilities.utils import WIN_REG_AVAILABLE, register_registry
from ..Utilities.UIKit import *
from ..Utilities.analytics import ga, GAScreen
from ..Utilities.trace import setup_trace
from ..Utilities import Assets
from ..Utilities.MPQHandler import MPQHandler
from ..Utilities.UpdateDialog import UpdateDialog
from ..Utilities.PyMSError import PyMSError
from ..Utilities.ErrorDialog import ErrorDialog
from ..Utilities.AboutDialog import AboutDialog
from ..Utilities.HelpDialog import HelpDialog
from ..Utilities.fileutils import check_allow_overwrite_internal_file
from ..Utilities.CheckSaved import CheckSaved
from ..Utilities.SettingsUI.BaseSettingsDialog import ErrorableSettingsDialogDelegate

from typing import Literal

LONG_VERSION = 'v%s' % Assets.version('PyTBL')

class PyTBL(MainWindow, MainDelegate, ErrorableSettingsDialogDelegate):
	def __init__(self, guifile: str | None = None) -> None:
		MainWindow.__init__(self)
		self.guifile = guifile

		self.set_icon('PyTBL')
		self.protocol('WM_DELETE_WINDOW', self.exit)
		ga.set_application('PyTBL', Assets.version('PyTBL'))
		ga.track(GAScreen('PyTBL'))
		setup_trace('PyTBL', self)
		
		self.config_ = PyTBLConfig()
		Theme.load_theme(self.config_.theme.value, self)

		self.tbl: TBL.TBL | None = None
		self.file: str | None = None
		self.edited = False
		self.findwindow: FindDialog | None = None
		self.gotowindow: GotoDialog | None = None
		self.tfontgam: PCX.PCX
		self.font8: FNT.FNT
		self.font10: FNT.FNT
		self.unitpal: Palette.Palette
		self.icons: GRP.GRP

		self.update_title()

		self.listmenu = Menu(self, tearoff=0)
		self.listmenu.add_command(label='Add String', command=self.add, shortcut=Key.Insert, bind_shortcut=False) # type: ignore[call-arg]
		self.listmenu.add_command(label='Insert String', command=self.insert, shortcut=Shift.Insert, bind_shortcut=False) # type: ignore[call-arg]
		self.listmenu.add_command(label='Remove String', command=self.remove, shortcut=Key.Delete, tags='string_selected', bind_shortcut=False) # type: ignore[call-arg]
		self.listmenu.add_separator()
		self.listmenu.add_command(label='Move String Up', command=lambda: self.movestring(-1), shortcut=Shift.Up, bind_shortcut=False) # type: ignore[call-arg]
		self.listmenu.add_command(label='Move String Down', command=lambda: self.movestring(1), shortcut=Shift.Down, bind_shortcut=False) # type: ignore[call-arg]

		self.toolbar = Toolbar(self)
		self.toolbar.add_button(Assets.get_image('new'), self.new, 'New', Ctrl.n)
		self.toolbar.add_gap()
		self.toolbar.add_button(Assets.get_image('open'), self.open, 'Open', Ctrl.o)
		self.toolbar.add_button(Assets.get_image('opendefault'), self.open_default, 'Open Default TBL', Ctrl.d)
		self.toolbar.add_button(Assets.get_image('import'), self.iimport, 'Import Strings', Ctrl.i)
		self.toolbar.add_gap()
		def save():
			self.save()
		self.toolbar.add_button(Assets.get_image('save'), save, 'Save', Ctrl.s, enabled=False, tags='file_open')
		def saveas():
			self.saveas()
		self.toolbar.add_button(Assets.get_image('saveas'), saveas, 'Save As', Ctrl.Alt.a, enabled=False, tags='file_open')
		self.toolbar.add_button(Assets.get_image('export'), self.export, 'Export Strings', Ctrl.e, enabled=False, tags='file_open')
		self.toolbar.add_gap()
		self.toolbar.add_button(Assets.get_image('close'), self.close, 'Close', Ctrl.w, enabled=False, tags='file_open')
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('add'), self.add, 'Add String', Key.Insert, enabled=False, tags='file_open')
		self.toolbar.add_button(Assets.get_image('insert'), self.insert, 'Insert String', Shift.Insert, enabled=False, tags='string_selected')
		self.toolbar.add_button(Assets.get_image('remove'), self.remove, 'Remove String (Delete in Listbox, Shift+Delete in Textbox)', Shift.Delete, enabled=False, tags='string_selected', add_shortcut_to_tooltip=False)
		self.toolbar.add_gap()
		self.toolbar.add_button(Assets.get_image('up'), lambda: self.movestring(-1), 'Move String Up', Shift.Up, enabled=False, tags='string_selected', bind_shortcut=False)
		self.toolbar.add_button(Assets.get_image('down'), lambda: self.movestring(1), 'Move String Down', Shift.Down, enabled=False, tags='string_selected', bind_shortcut=False)
		self.toolbar.add_gap()
		self.toolbar.add_button(Assets.get_image('find'), self.find, 'Find Strings', Ctrl.f, enabled=False, tags='file_open')
		self.toolbar.add_button(Assets.get_image('ffw'), self.goto, 'Go to', Ctrl.g, enabled=False, tags='file_open')
		self.toolbar.add_gap()
		self.toolbar.add_button(Assets.get_image('test'), self.preview, 'Test String', Ctrl.t, enabled=False, tags='string_selected')
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('asc3topyai'), self.mpqsettings, 'Manage Settings', Ctrl.m)
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('register'), self.register_registry, 'Set as default *.tbl editor (Windows Only)', enabled=WIN_REG_AVAILABLE)
		self.toolbar.add_button(Assets.get_image('help'), self.help, 'Help', Key.F1)
		self.toolbar.add_button(Assets.get_image('about'), self.about, 'About PyTBL')
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('exit'), self.exit, 'Exit', Shortcut.Exit)
		self.toolbar.grid(row=0,column=0, padx=1,pady=1, sticky=EW)

		self.bind_all(Shift.Up(), lambda e: self.movestring(-1))
		self.bind_all(Shift.Down(), lambda e: self.movestring(1))

		self.hor_pane = PanedWindow(self,orient=HORIZONTAL)

		# listbox
		self.listbox = ScrolledListbox(self.hor_pane, scroll_speed=2, width=35, height=1)
		self.listbox.pack(side=LEFT, fill=BOTH, expand=1)
		self.hor_pane.add(self.listbox, sticky=NSEW, minsize=200)
		self.listbox.bind(WidgetEvent.Listbox.Select(), lambda e: self.update_string())
		self.listbox.bind(Mouse.Click_Right(), self.popup)

		# Textbox
		self.ver_pane = PanedWindow(self.hor_pane,orient=VERTICAL)
		textframe = Frame(self.ver_pane, bd=2, relief=SUNKEN)
		hscroll = Scrollbar(textframe, orient=HORIZONTAL)
		vscroll = Scrollbar(textframe)
		self.text = Text(textframe, height=1, bd=0, undo=True, maxundo=100, wrap=NONE, highlightthickness=0, xscrollcommand=hscroll.set, yscrollcommand=vscroll.set, exportselection=False, state=DISABLED)
		text_w = getattr(self.text, '_w')
		self.text_orig = text_w + '_orig'
		self.tk.call('rename', text_w, self.text_orig)
		self.tk.createcommand(text_w, self.dispatch)
		self.text.mark_set('textend', '1.0')
		self.text.mark_gravity('textend', RIGHT)
		self.text.grid(sticky=NSEW)
		self.text.bind(Ctrl.a(), lambda e: self.after(1, self.selectall))
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
		text = Text(colors, height=1, bd=0, undo=True, maxundo=100, wrap=NONE, highlightthickness=0, xscrollcommand=hscroll.set, yscrollcommand=vscroll.set, exportselection=False)
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
		self.editstatus = statusbar.add_icon(Assets.get_image('save.gif'))
		statusbar.add_label(self.stringstatus)
		statusbar.grid(row=2,column=0, sticky=EW)

		self.grid_columnconfigure(0, weight=1)
		self.grid_rowconfigure(1, weight=1)

		self.config_.windows.main.load_size(self)
		self.config_.panes.string_list.load_size(self.hor_pane)
		self.config_.panes.color_list.load_size(self.ver_pane)

		self.mpq_handler = MPQHandler(self.config_.mpqs)
	
	def initialize(self) -> None:
		e = self.open_files()
		if e:
			self.mpqsettings(err=e)
		if self.guifile:
			self.open(file=self.guifile)
		UpdateDialog.check_update(self, 'PyTBL')

	def open_files(self) -> (PyMSError | None):
		self.mpq_handler.open_mpqs()
		err: PyMSError | None = None
		try:
			tfontgam = PCX.PCX()
			font8 = FNT.FNT()
			font10 = FNT.FNT()
			unitpal = Palette.Palette()
			icons = GRP.GRP()
			tfontgam.load_file(self.mpq_handler.load_file(self.config_.settings.files.tfontgam.file_path))
			try:
				font8.load_file(self.mpq_handler.load_file(self.config_.settings.files.font8.file_path, False))
			except:
				font8.load_file(self.mpq_handler.load_file(self.config_.settings.files.font8.file_path, True))
			try:
				font10.load_file(self.mpq_handler.load_file(self.config_.settings.files.font10.file_path, False))
			except:
				font10.load_file(self.mpq_handler.load_file(self.config_.settings.files.font10.file_path, True))
			unitpal.load_file(self.mpq_handler.load_file(self.config_.settings.files.unit_pal.file_path))
			icons.load_file(self.mpq_handler.load_file(self.config_.settings.files.icons.file_path))
		except PyMSError as e:
			err = e
		else:
			self.tfontgam = tfontgam
			self.font8 = font8
			self.font10 = font10
			self.unitpal = unitpal
			self.icons = icons
		self.mpq_handler.close_mpqs()
		return err

	def update_string_status(self) -> None:
		if not self.tbl:
			self.stringstatus.set('')
		else:
			string_count = self.listbox.size()
			if not string_count:
				string_index = '-'
			else:
				string_index = str(self.listbox.curselection()[0])
			self.stringstatus.set(f'String: {string_index}/{string_count}')

	def update_string(self) -> None:
		self.text_delete('1.0', END)
		if not self.tbl:
			return
		if not self.listbox.size():
			return
		s = int(self.listbox.curselection()[0])
		self.text_insert('1.0', TBL.decompile_string(self.tbl.strings[s], '\n'))
		self.update_string_status()

	def popup(self, event: Event) -> None:
		if not self.tbl:
			return
		self.listmenu.tag_enabled('string_selected', self.is_string_selected()) # type: ignore[attr-defined]
		self.listmenu.post(event.x_root, event.y_root)

	def selectall(self) -> None:
		self.text.tag_remove(SEL, '1.0', END)
		self.text.tag_add(SEL, '1.0', END)
		self.text.mark_set(INSERT, '1.0')

	def check_saved(self) -> CheckSaved:
		if not self.tbl or not self.edited:
			return CheckSaved.saved
		file = self.file
		if not file:
			file = 'Unnamed.tbl'
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
		return not not self.tbl

	def is_string_selected(self) -> bool:
		return not not self.listbox.curselection()

	def action_states(self) -> None:
		file_open = self.is_file_open()
		string_selected = self.is_string_selected()
		self.toolbar.tag_enabled('file_open', file_open)
		self.text['state'] = NORMAL if string_selected else DISABLED
		self.toolbar.tag_enabled('string_selected', string_selected)

	def text_insert(self, pos: str, text: str) -> None:
		self.tk.call((self.text_orig, 'insert', pos, text))

	def text_delete(self, start: str, end: str | None = None):
		self.tk.call((self.text_orig, 'delete', start, end))

	def dispatch(self, cmd: str, *args: str ) -> None:
		try:
			r = self.tk.call((self.text_orig, cmd) + args)
		except TclError:
			r = ''
		if self.tbl and self.listbox.size() and cmd in ['insert','delete']:
			if not self.edited:
				self.edited = True
				self.editstatus['state'] = NORMAL
			i = int(self.listbox.curselection()[0])
			self.tbl.strings[i] = TBL.compile_string(self.text.get('1.0','textend'))
			self.listbox.delete(i)
			self.listbox.insert(i, TBL.decompile_string(self.tbl.strings[i]))
			self.listbox.select_set(i)
		return r

	def update_title(self) -> None:
		file_path = self.file
		if not file_path and self.is_file_open():
			file_path = 'Untitled.tbl'
		if not file_path:
			self.title('PyTBL %s' % LONG_VERSION)
		else:
			self.title('PyTBL %s (%s)' % (LONG_VERSION, file_path))

	def mark_edited(self, edited: bool = True) -> None:
		self.edited = edited
		self.editstatus['state'] = NORMAL if edited else DISABLED

	def new(self) -> None:
		if self.check_saved() == CheckSaved.cancelled:
			return
		self.tbl = TBL.TBL()
		self.file = None
		self.status.set('Editing new TBL.')
		self.mark_edited(False)
		self.update_title()
		if self.listbox.size():
			self.text_delete('1.0', END)
		self.listbox.delete(0, END)
		self.stringstatus.set('')
		self.action_states()

	def open(self, file: str | None = None):
		if self.check_saved() == CheckSaved.cancelled:
			return
		if not file:
			file = self.config_.last_path.tbl.select_open(self)
			if not file:
				return
		tbl = TBL.TBL()
		try:
			tbl.load_file(file)
		except PyMSError as e:
			ErrorDialog(self, e)
			return
		self.tbl = tbl
		self.listbox.delete(0, END)
		self.text_delete('1.0', END)
		for string in self.tbl.strings:
			self.listbox.insert(END, TBL.decompile_string(string))
		if self.listbox.size():
			self.listbox.select_set(0)
			self.listbox.see(0)
		self.file = file
		self.update_title()
		self.status.set('Load Successful!')
		self.mark_edited(False)
		self.action_states()
		self.update_string()

	def open_default(self) -> None:
		self.open(Assets.mpq_file_path('rez','stat_txt.tbl'))

	def iimport(self) -> None:
		if self.check_saved() == CheckSaved.cancelled:
			return
		file = self.config_.last_path.txt.select_open(self)
		if not file:
			return
		tbl = TBL.TBL()
		try:
			tbl.interpret(file)
		except PyMSError as e:
			ErrorDialog(self, e)
			return
		self.tbl = tbl
		self.listbox.delete(0, END)
		self.text_delete('1.0', END)
		for string in self.tbl.strings:
			self.listbox.insert(END, TBL.decompile_string(string))
		if self.listbox.size():
			self.listbox.select_set(0)
			self.listbox.see(0)
		self.file = file
		self.update_title()
		self.status.set('Import Successful!')
		self.mark_edited(False)
		self.action_states()
		self.update_string()

	def save(self) -> CheckSaved:
		return self.saveas(file_path=self.file)

	def saveas(self, file_path: str | None = None) -> CheckSaved:
		if not self.tbl:
			return CheckSaved.saved
		if not file_path:
			file_path = self.config_.last_path.tbl.select_save(self)
			if not file_path:
				return CheckSaved.cancelled
		elif not check_allow_overwrite_internal_file(file_path):
			return CheckSaved.cancelled
		try:
			self.tbl.compile(file_path)
		except PyMSError as e:
			ErrorDialog(self, e)
			return CheckSaved.cancelled
		self.status.set('Save Successful!')
		self.mark_edited(False)
		self.file = file_path
		self.update_title()
		return CheckSaved.saved

	def export(self) -> None:
		if not self.tbl:
			return
		file = self.config_.last_path.txt.select_save(self)
		if not file:
			return
		try:
			self.tbl.decompile(file)
			self.status.set('Export Successful!')
		except PyMSError as e:
			ErrorDialog(self, e)

	def close(self) -> None:
		if self.check_saved() == CheckSaved.cancelled:
			return
		self.tbl = None
		self.file = None
		self.update_title()
		self.status.set('Load or create a TBL.')
		self.mark_edited(False)
		self.listbox.delete(0, END)
		self.text_delete('1.0', END)
		self.stringstatus.set('')
		self.action_states()

	def add(self, index: int | Literal['end'] = END):
		if not self.tbl:
			return
		if index == END:
			self.tbl.strings.append('')
		else:
			self.tbl.strings.insert(index, '')
		self.listbox.insert(index, '')
		self.listbox.select_clear(0, END)
		self.listbox.select_set(index)
		self.listbox.see(index)
		self.mark_edited()
		self.action_states()
		self.update_string()

	def insert(self) -> None:
		if not self.is_string_selected():
			return
		self.add(int(self.listbox.curselection()[0]))

	def remove(self) -> None:
		if not self.tbl or not self.is_string_selected():
			return
		i = int(self.listbox.curselection()[0])
		del self.tbl.strings[i]
		self.listbox.delete(i)
		if self.listbox.size():
			i = min(i,self.listbox.size()-1) # type: ignore[operator]
			self.listbox.select_set(i)
			self.listbox.see(i)
		self.mark_edited()
		self.action_states()
		self.update_string()

	def movestring(self, delta: int) -> None:
		if not self.tbl or not self.is_string_selected():
			return
		i = int(self.listbox.curselection()[0])
		if delta == -1 and i == 0:
			return
		elif delta == 1 and i == self.listbox.size()-1: # type: ignore[operator]
			return
		self.listbox.delete(i)
		n = i + delta
		s = self.tbl.strings[i]
		self.listbox.insert(n, TBL.decompile_string(s))
		self.listbox.select_clear(0, END)
		self.listbox.select_set(n)
		self.listbox.see(n)
		self.tbl.strings[i] = self.tbl.strings[n]
		self.tbl.strings[n] = s
		self.mark_edited()
		self.action_states()
		self.update_string_status()

	def find(self) -> None:
		if not self.is_file_open():
			return
		if not self.findwindow:
			self.findwindow = FindDialog(self, self)
			self.bind(Key.F3(), self.findwindow.findnext)
		else:
			self.findwindow.make_active() # type: ignore[attr-defined]
			self.findwindow.findentry.focus_set(highlight=True)

	def goto(self) -> None:
		if not self.is_file_open():
			return
		if not self.gotowindow:
			self.gotowindow = GotoDialog(self, self)
		else:
			self.gotowindow.make_active() # type: ignore[attr-defined]
			self.gotowindow.gotoentry.focus_set(highlight=True)

	def preview(self) -> None:
		if not self.is_string_selected():
			return
		PreviewDialog(self, self)

	def mpqsettings(self, err: PyMSError | None = None) -> None:
		SettingsDialog(self, self.config_, self, err, self.mpq_handler)

	def register_registry(self) -> None:
		try:
			register_registry('PyTBL', 'tbl', '')
		except PyMSError as e:
			ErrorDialog(self, e)

	def help(self) -> None:
		HelpDialog(self, self.config_.windows.help, 'Help/Programs/PyTBL.md')

	def about(self) -> None:
		AboutDialog(self, 'PyTBL', LONG_VERSION)

	def exit(self) -> None:
		if self.check_saved() == CheckSaved.cancelled:
			return
		self.config_.panes.string_list.save_size(self.hor_pane)
		self.config_.panes.color_list.save_size(self.ver_pane)
		self.config_.windows.main.save_size(self)
		self.config_.save()
		self.destroy()

	def destroy(self) -> None:
		if self.gotowindow is not None:
			Toplevel.destroy(self.gotowindow)
		if self.findwindow is not None:
			Toplevel.destroy(self.findwindow)
		MainWindow.destroy(self)
