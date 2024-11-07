
from .Config import PyJSONConfig
from .SettingsDialog import SettingsDialog
from .DataSource import DataSource

from ..FileFormats import JSON

from ..Utilities.utils import WIN_REG_AVAILABLE, register_registry
from ..Utilities.UIKit import *
from ..Utilities.analytics import ga, GAScreen
from ..Utilities.trace import setup_trace
from ..Utilities import Assets
from ..Utilities.UpdateDialog import UpdateDialog
from ..Utilities.PyMSError import PyMSError
from ..Utilities.ErrorDialog import ErrorDialog
from ..Utilities.AboutDialog import AboutDialog
from ..Utilities.HelpDialog import HelpDialog
from ..Utilities.fileutils import check_allow_overwrite_internal_file
from ..Utilities.CheckSaved import CheckSaved
from ..Utilities.SponsorDialog import SponsorDialog

from typing import Literal

LONG_VERSION = 'v%s' % Assets.version('PyJSON')

class PyJSON(MainWindow):
	def __init__(self, guifile: str | None = None) -> None:
		MainWindow.__init__(self)

		self.set_icon('PyJSON')
		self.protocol('WM_DELETE_WINDOW', self.exit)
		ga.set_application('PyJSON', Assets.version('PyJSON'))
		ga.track(GAScreen('PyJSON'))
		setup_trace('PyJSON', self)
		
		self.config_ = PyJSONConfig()
		Theme.load_theme(self.config_.theme.value, self)

		self.file_path: str | None = None
		self.edited = False

		self.update_title()

		self.toolbar = Toolbar(self)
		self.toolbar.add_button(Assets.get_image('new'), self.new, 'New', Ctrl.n)
		self.toolbar.add_gap()
		self.toolbar.add_button(Assets.get_image('open'), self.open, 'Open', Ctrl.o)
		self.toolbar.add_gap()
		def save():
			self.save()
		self.toolbar.add_button(Assets.get_image('save'), save, 'Save', Ctrl.s, enabled=False, tags='file_open')
		def saveas():
			self.saveas()
		self.toolbar.add_button(Assets.get_image('saveas'), saveas, 'Save As', Ctrl.Alt.a, enabled=False, tags='file_open')
		self.toolbar.add_gap()
		self.toolbar.add_button(Assets.get_image('close'), self.close, 'Close', Ctrl.w, enabled=False, tags='file_open')
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('add'), self.add, 'Add Object', Key.Insert, enabled=False, tags='file_open')
		self.toolbar.add_button(Assets.get_image('insert'), self.insert, 'Insert Object', Shift.Insert, enabled=False, tags='object_selected')
		self.toolbar.add_button(Assets.get_image('remove'), self.remove, 'Remove Object', Shift.Delete, enabled=False, tags='object_selected')
		self.toolbar.add_gap()
		self.toolbar.add_button(Assets.get_image('asc3topyai'), self.settings, 'Manage Settings', Ctrl.m)
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('register'), self.register_registry, 'Set as default *.json editor (Windows Only)', enabled=WIN_REG_AVAILABLE)
		self.toolbar.add_button(Assets.get_image('help'), self.help, 'Help', Key.F1)
		self.toolbar.add_button(Assets.get_image('about'), self.about, 'About PyJSON')
		self.toolbar.add_button(Assets.get_image('money'), self.sponsor, 'Donate')
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('exit'), self.exit, 'Exit', Shortcut.Exit)
		self.toolbar.grid(row=0,column=0, padx=1,pady=1, sticky=EW)

		self.hor_pane = PanedWindow(self,orient=HORIZONTAL)

		# treeview
		left_frame = Frame(self.hor_pane)
		self.tree = ScrolledTreeview(left_frame)
		self.tree.pack(side=TOP, fill=BOTH, expand=1)
		self.key_index = IntVar()
		key_frame = Frame(left_frame)
		Label(key_frame, text='Key:').pack(side=LEFT, padx=(0,2))
		self.key_dropdown = DropDown(key_frame, self.key_index, ['id'])
		self.key_dropdown.pack(side=LEFT, fill=X, expand=1)
		key_frame.pack(side=BOTTOM, fill=X, padx=2, pady=2)
		self.hor_pane.add(left_frame, sticky=NSEW, minsize=200)
		self.tree.treeview.bind(WidgetEvent.Treeview.Select(), lambda e: self.refresh_object())

		import json
		with open('/Users/zzahos/Projects/Personal/PyMS_Data/stat_txt.json','r') as f:
			data = json.load(f)
		# data = {
		# 	'Objects':[
		# 		{'Integer':1, 'String':'1', 'Boolean': False},{'Integer':2, 'String':'2', 'Boolean': True}
		# 	]
		# }
		self.data_source = DataSource(data)
		self.data_source.name_key = 'id'
		self.data_source.attach(self.tree.treeview)

		# Editor
		self.editor_frame = LabelFrame(self.hor_pane, text='Editor')
		self.hor_pane.add(self.editor_frame, sticky=NSEW, minsize=200)

		self.hor_pane.grid(row=1,column=0, sticky=NSEW)

		#Statusbar
		self.status = StringVar()
		self.status.set('Load or create a JSON.')
		self.object_status = StringVar()
		statusbar = StatusBar(self)
		statusbar.add_label(self.status)
		self.editstatus = statusbar.add_icon(Assets.get_image('save.gif'))
		statusbar.add_label(self.object_status)
		statusbar.grid(row=2,column=0, sticky=EW)

		self.grid_columnconfigure(0, weight=1)
		self.grid_rowconfigure(1, weight=1)

		self.config_.windows.main.load_size(self)
		self.config_.panes.list.load_size(self.hor_pane)

		if guifile:
			self.open(file_path=guifile)

		UpdateDialog.check_update(self, 'PyJSON')

	def check_saved(self) -> CheckSaved:
		if not self.data_source.data or not self.edited:
			return CheckSaved.saved
		file_path = self.file_path
		if not file_path:
			file_path = 'Unnamed.json'
		save = MessageBox.askquestion(parent=self, title='Save Changes?', message="Save changes to '%s'?" % file_path, default=MessageBox.YES, type=MessageBox.YESNOCANCEL)
		if save == MessageBox.NO:
			return CheckSaved.saved
		if save == MessageBox.CANCEL:
			return CheckSaved.cancelled
		if self.file_path:
			return self.save()
		else:
			return self.saveas()

	def is_file_open(self) -> bool:
		return not not self.data_source.data

	def is_object_selected(self) -> bool:
		return not not self.tree.treeview.selection()

	def action_states(self) -> None:
		file_open = self.is_file_open()
		object_selected = self.is_object_selected()
		self.toolbar.tag_enabled('file_open', file_open)
		self.toolbar.tag_enabled('object_selected', object_selected)

	def update_title(self) -> None:
		file_path = self.file_path
		if not file_path and self.is_file_open():
			file_path = 'Untitled.json'
		if not file_path:
			self.title('[WIP] PyJSON %s' % LONG_VERSION)
		else:
			self.title('[WIP] PyJSON %s (%s)' % (LONG_VERSION, file_path))

	def mark_edited(self, edited: bool = True) -> None:
		self.edited = edited
		self.editstatus['state'] = NORMAL if edited else DISABLED

	def new(self) -> None:
		if self.check_saved() == CheckSaved.cancelled:
			return
		self.data_source.set_data(None)
		self.path = None
		self.status.set('Editing new JSON.')
		self.mark_edited(False)
		self.update_title()
		self.object_status.set('')
		self.action_states()

	def check_format(self, json_data: Any) -> bool:
		if not isinstance(json_data, list):
			return False
		for object in json_data:
			if not isinstance(object, dict):
				return False
		return True

	def refresh_listbox(self) -> None:
		pass

	def clear_editor(self) -> None:
		for child in self.editor_frame.winfo_children():
			child.pack_forget()

	def rebuild_editor(self) -> None:
		self.clear_editor()
		# item_ids = self.tree.treeview.selection()
		# if not item_ids:
		# 	return
		# item_id = item_ids[0]
		# value = self.data_source.value_for(item_id)


	def refresh_object(self) -> None:
		# print(self.tree.treeview.selection())
		# path = self.data_source.item_path(self.tree.treeview.selection()[0])
		# print(path)
		# value = self.data_source.value_for(self.tree.treeview.selection()[0])
		self.rebuild_editor()

	def open(self, file_path: str | None = None):
		if self.check_saved() == CheckSaved.cancelled:
			return
		if not file_path:
			file_path = self.config_.last_path.json.select_open(self)
			if not file_path:
				return
		try:
			json = JSON.load(file_path)
		except PyMSError as e:
			ErrorDialog(self, e)
			return
		self.data_source.set_data(json)
		self.file_path = file_path
		self.update_title()
		self.status.set('Load Successful!')
		self.mark_edited(False)
		self.action_states()
		self.refresh_object()

	def save(self) -> CheckSaved:
		return self.saveas(file_path=self.file_path)

	def saveas(self, file_path: str | None = None) -> CheckSaved:
		if not self.data_source.data:
			return CheckSaved.saved
		if not file_path:
			file_path = self.config_.last_path.json.select_save(self)
			if not file_path:
				return CheckSaved.cancelled
		elif not check_allow_overwrite_internal_file(file_path):
			return CheckSaved.cancelled
		try:
			JSON.save(file_path, self.data_source.data)
		except PyMSError as e:
			ErrorDialog(self, e)
			return CheckSaved.cancelled
		self.status.set('Save Successful!')
		self.mark_edited(False)
		self.file = file_path
		self.update_title()
		return CheckSaved.saved

	def close(self) -> None:
		if self.check_saved() == CheckSaved.cancelled:
			return
		self.data_source.set_data(None)
		self.file_path = None
		self.update_title()
		self.status.set('Load or create a JSON.')
		self.mark_edited(False)
		self.object_status.set('')
		self.action_states()

	def add(self, index: int | Literal['end'] = END):
		if not self.data_source.data:
			return
		self.mark_edited()
		self.action_states()
		self.refresh_object()

	def insert(self) -> None:
		if not self.is_object_selected():
			return
		self.add(int(self.tree.treeview.selection()[0]))

	def remove(self) -> None:
		if not self.data_source.data or not self.is_object_selected():
			return
		self.mark_edited()
		self.action_states()
		self.refresh_object()

	def settings(self) -> None:
		SettingsDialog(self, self.config_)

	def register_registry(self) -> None:
		try:
			register_registry('PyJSON', 'json', '')
		except PyMSError as e:
			ErrorDialog(self, e)

	def help(self) -> None:
		HelpDialog(self, self.config_.windows.help, 'Help/Programs/PyJSON.md')

	def about(self) -> None:
		AboutDialog(self, 'PyJSON', LONG_VERSION)

	def sponsor(self) -> None:
		SponsorDialog(self)

	def exit(self) -> None:
		if self.check_saved() == CheckSaved.cancelled:
			return
		self.config_.panes.list.save_size(self.hor_pane)
		self.config_.windows.main.save_size(self)
		self.config_.save()
		self.destroy()
