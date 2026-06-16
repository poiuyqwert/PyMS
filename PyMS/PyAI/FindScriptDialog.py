
from .Delegates import MainDelegate

from ..FileFormats.AIBIN.AIScript import AIScript

from ..Utilities import UIKit as UI
from ..Utilities.PyMSDialog import PyMSDialog
from ..Utilities.Config import WindowGeometry
from ..Utilities.utils import binary
from ..Utilities import ItemSelectDialog

import re

from typing import Sequence

class ScriptLocation:
	aiscript = 1
	bwscript = 2
	either = aiscript | bwscript

class FindScriptDialog(PyMSDialog, ItemSelectDialog.Delegate):
	def __init__(self, parent: UI.AnyWindow, config: WindowGeometry, delegate: MainDelegate):
		self.config_ = config
		self.delegate = delegate

		self.results = False
		self.id = UI.StringVar()
		self.bw = UI.IntVar(value=ScriptLocation.either)
		self.flags = UI.StringVar()
		self.stringid = UI.StringVar()
		self.string = UI.StringVar()
		self.casesens = UI.IntVar()
		self.regex = UI.IntVar()

		self.reset_entry: UI.Entry | None = None
		self.reset_color: str | None = None
		self.reset_timer: str | None = None

		self.matching_scripts: list[AIScript] = []

		PyMSDialog.__init__(self, parent, 'Find a Script')

	def widgetize(self) -> UI.Widget:
		self.bind(UI.Ctrl.a(), self.selectall)

		UI.Label(self, text='AI ID', anchor=UI.W).pack(fill=UI.X)
		self.identry = UI.Entry(self, textvariable=self.id)
		self.identry.pack(fill=UI.X)

		frame = UI.Frame(self)
		UI.Radiobutton(frame, text='aiscript.bin', variable=self.bw, value=ScriptLocation.aiscript).pack(side=UI.LEFT)
		UI.Radiobutton(frame, text='bwscript.bin', variable=self.bw, value=ScriptLocation.bwscript).pack(side=UI.LEFT)
		UI.Radiobutton(frame, text='Either', variable=self.bw, value=ScriptLocation.either).pack(side=UI.LEFT)
		frame.pack(fill=UI.X)

		UI.Label(self, text='Flags', anchor=UI.W).pack(fill=UI.X)
		self.flagsentry = UI.Entry(self, textvariable=self.flags)
		self.flagsentry.pack(fill=UI.X)

		UI.Label(self, text='String ID', anchor=UI.W).pack(fill=UI.X)
		frame = UI.Frame(self)
		self.stringidentry = UI.Entry(frame, textvariable=self.stringid)
		self.stringidentry.pack(side=UI.LEFT, fill=UI.X, expand=1)
		UI.Button(frame, text='Browse...', width=10, command=self.browse, state=UI.ACTIVE if self.delegate.get_data_context().stattxt_tbl is not None else UI.DISABLED).pack(side=UI.RIGHT)
		frame.pack(fill=UI.X)

		UI.Label(self, text='String', anchor=UI.W).pack(fill=UI.X)
		self.stringentry = UI.Entry(self, textvariable=self.string)
		self.stringentry.pack(fill=UI.X)

		options = UI.Frame(self)
		UI.Checkbutton(options, text='Case Sensitive', variable=self.casesens).pack(side=UI.LEFT, padx=3)
		UI.Checkbutton(options, text='Regular Expressions', variable=self.regex).pack(side=UI.LEFT, padx=3)
		options.pack(pady=3)

		self.listbox = UI.ScrolledListbox(self, selectmode=UI.EXTENDED, font=UI.Font.fixed(), width=1, height=1)
		self.listbox.pack(fill=UI.BOTH, padx=2, pady=2, expand=1)
		self.listbox.bind(UI.WidgetEvent.Listbox.Select(), self.update_select_state)

		buttons = UI.Frame(self)
		UI.Button(buttons, text='Find', width=10, command=self.find, default=UI.NORMAL).pack(side=UI.LEFT, padx=3, pady=3)
		self.select = UI.Button(buttons, text='Select', width=10, command=self.select_item, state=UI.DISABLED)
		self.select.pack(side=UI.LEFT, padx=3, pady=3)
		UI.Button(buttons, text='Cancel', width=10, command=self.cancel).pack(side=UI.LEFT, padx=3, pady=3)
		buttons.pack()

		self.bind(UI.Key.Return(), self.find)

		return self.identry

	def setup_complete(self) -> None:
		self.minsize(300,325)
		self.config_.load_size(self)

	def update_select_state(self, _event: UI.Event | None = None) -> None:
		self.select['state'] = UI.NORMAL

	def updatecolor(self) -> None:
		if self.reset_entry:
			if self.reset_timer:
				self.after_managed_cancel(self.reset_timer)
				self.reset_timer = None
			self.reset_entry['bg'] = self.reset_color
			self.reset_entry = None

	def selectall(self, _event: UI.Event | None = None) -> None:
		if self.listbox.size():
			self.listbox.select_set(0, UI.END)
			self.select['state'] = UI.NORMAL

	def browse(self) -> None:
		try:
			initial_selection = [int(self.stringid.get())]
		except Exception:
			initial_selection = []
		ItemSelectDialog.ItemSelectDialog(parent=self, title='Select String', delegate=self, selected=initial_selection)

	def update_listbox(self) -> None:
		self.listbox.delete(0, UI.END)
		data_context = self.delegate.get_data_context()
		for script in self.matching_scripts:
			self.listbox.insert(UI.END, f"{script.id}     {'BW' if script.in_bwscript else '  '}     {binary(script.flags, 3)}     {script.string_id}: {data_context.stattxt_string(script.string_id)}")

	def find(self, _: UI.Event | None = None) -> None:
		self.updatecolor()
		self.listbox.delete(0,UI.END)
		self.select['state'] = UI.DISABLED

		def get_matcher(variable: UI.StringVar, entry: UI.Entry) -> re.Pattern | None:
			regex = variable.get()
			if not regex:
				return None
			if self.regex.get():
				if not regex.startswith('\\A'):
					regex = '.*' + regex
				if not regex.endswith('\\Z'):
					regex = regex + '.*'
			else:
				regex = f'.*{re.escape(regex)}.*'
			try:
				return re.compile(regex, re.I if self.casesens.get() else 0)
			except Exception:
				self.reset_entry = entry
				self.reset_color = entry['bg']
				entry['bg'] = '#FFB4B4'
				self.reset_timer = self.after_managed(1000, self.updatecolor)
				raise

		try:
			id_matcher = get_matcher(self.id, self.identry)
			flags_matcher = get_matcher(self.flags, self.flagsentry)
			stringid_matcher = get_matcher(self.stringid, self.stringidentry)
			string_matcher = get_matcher(self.string, self.stringentry)
		except Exception:
			return
		matches: list[AIScript] = []
		ai = self.delegate.get_ai_bin()
		data_context = self.delegate.get_data_context()
		for script in ai.list_scripts():
			if id_matcher and not id_matcher.match(script.id):
				continue
			if not ((script.in_bwscript + 1) & self.bw.get()):
				continue
			if flags_matcher and not flags_matcher.match(binary(script.flags, 3)):
				continue
			if stringid_matcher and not stringid_matcher.match(str(script.string_id)):
				continue
			string = data_context.stattxt_string(script.string_id)
			if string_matcher and (string is None or not string_matcher.match(string)):
				continue
			matches.append(script)
		self.matching_scripts = matches
		self.update_listbox()

	def select_item(self) -> None:
		script_ids = [self.matching_scripts[index].id for index in self.listbox.curselection()]
		self.delegate.select_scripts(script_ids)
		self.ok()

	def dismiss(self) -> None:
		self.config_.save_size(self)
		PyMSDialog.dismiss(self)

	# ItemSelectDialog.Delegate
	def get_items(self) -> Sequence[ItemSelectDialog.Item]:
		strings = self.delegate.get_data_context().stattxt_strings()
		if not strings:
			return []
		# return [ItemSelectDialog.DisplayItem(string, f'{index}: {string}') for index, string in enumerate(strings)]
		return strings

	def item_selected(self, index: int) -> bool:
		self.stringid.set(str(index))
		return True

	def items_selected(self, indexes: list[int]) -> bool:
		return True
