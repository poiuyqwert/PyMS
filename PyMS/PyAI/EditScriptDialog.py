
from .Delegates import EditScriptDelegate
from .FlagEditor import FlagEditor

from ..Utilities import UIKit as UI
from ..Utilities.PyMSDialog import PyMSDialog
from ..Utilities.PyMSError import PyMSError
from ..Utilities.Config import WindowGeometry
from ..Utilities import ItemSelectDialog

from typing import Sequence, Any

class EditScriptDialog(PyMSDialog, ItemSelectDialog.Delegate):
	def __init__(self, parent: UI.AnyWindow, *, delegate: EditScriptDelegate, config: WindowGeometry, script_id: str = 'MYAI', flags: int = 0, string_index: int = 0, title: str = 'Edit AI', initial: str = ''):
		self.delegate = delegate
		self.config_ = config
		self.initialid = initial
		self.validid = script_id
		self.script_id = UI.StringVar()
		self.script_id.set(script_id)
		self.script_id.trace_add('write', self.editid)
		self.flags = flags
		self.validstring = string_index
		self.string = UI.StringVar()
		self.string.set(str(string_index))
		self.string.trace_add('write', lambda _a,_b,_c: self.editstring())
		self.actualstring = UI.StringVar()
		self.actualstring.set(delegate.get_data_context().stattxt_string(string_index) or '')

		PyMSDialog.__init__(self, parent, title)

	def widgetize(self) -> UI.Widget:
		frame = UI.Frame(self)

		##Entries
		entries = UI.Frame(frame)
		id_frame = UI.Frame(entries)
		UI.Label(id_frame, text='AI ID:', width=10, anchor=UI.E).pack(side=UI.LEFT)
		identry = UI.Entry(id_frame, justify=UI.LEFT, textvariable=self.script_id, width=10, validate='key', vcmd=self.editid)
		identry.pack(side=UI.LEFT)
		UI.Button(id_frame, text='Flags', width=10, command=self.editflags).pack(side=UI.RIGHT, padx=1, pady=2)
		id_frame.pack(fill=UI.X)
		string = UI.Frame(entries)
		UI.Label(string, text='String:', width=10, anchor=UI.E).pack(side=UI.LEFT)
		stringid = UI.Entry(string, justify=UI.LEFT, textvariable=self.string, width=10)
		stringid.pack(side=UI.LEFT)
		UI.Label(string, textvariable=self.actualstring, anchor=UI.W, width=1).pack(side=UI.LEFT, fill=UI.X, expand=1)
		UI.Button(string, text='Browse...', width=10, command=self.browse).pack(side=UI.RIGHT, padx=1, pady=2)
		string.pack(fill=UI.X)

		# ##Extra info
		# aiinfo = Frame(entries)
		# Label(aiinfo, text='Extra Info:', width=10, anchor=NE).pack(side=LEFT, fill=Y)
		# vscroll = Scrollbar(aiinfo)
		# self.info = Text(aiinfo, yscrollcommand=vscroll.set, width=1, height=1, wrap=WORD)
		# self.info.insert(1.0, self.aiinfo)
		# self.info.pack(side=LEFT, fill=BOTH, expand=1)
		# vscroll.config(command=self.info.yview)
		# vscroll.pack(side=RIGHT, fill=Y)
		# aiinfo.pack(fill=BOTH, expand=1)

		entries.pack(side=UI.LEFT, fill=UI.BOTH, expand=1)
		frame.pack(fill=UI.BOTH, expand=1)

		##Buttons
		buttonframe = UI.Frame(self)
		self.okbtn = UI.Button(buttonframe, text='Ok', width=10, command=self.ok)
		self.okbtn.pack(side=UI.LEFT, padx=3, pady=3)
		UI.Button(buttonframe, text='Cancel', width=10, command=self.cancel).pack(side=UI.LEFT, padx=3, pady=3)
		buttonframe.pack()

		return identry

	def setup_complete(self) -> None:
		self.minsize(500, 100)
		self.maxsize(1000, 100)
		self.config_.load_size(self)

	def editflags(self) -> None:
		f = FlagEditor(self, self.flags)
		if f.flags is not None:
			self.flags = f.flags

	def editid(self, *_: Any) -> bool:
		new = self.script_id.get()
		if len(new) > 4 or [x for x in ',():' if x in new]:
			self.script_id.set(self.validid)
		else:
			self.validid = new
		if hasattr(self, 'okbtn'):
			if len(new) < 4:
				self.okbtn['state'] = UI.DISABLED
			elif len(new) == 4:
				self.okbtn['state'] = UI.NORMAL
		return True

	def editstring(self) -> bool:
		string_index = 0
		string_index_raw = self.string.get()
		if string_index_raw:
			try:
				string_index = int(string_index_raw)
				if string_index < 0:
					raise PyMSError('Internal', 'Invalid string ID')
			except Exception:
				string_index = self.validstring
			else:
				if (stattxt_tbl := self.delegate.get_data_context().stattxt_tbl):
					strs = len(stattxt_tbl.strings)-1
					string_index = min(string_index, strs)
			self.string.set(str(string_index))
		self.validstring = string_index
		self.actualstring.set(self.delegate.get_data_context().stattxt_string(string_index) or '')
		return True

	def browse(self) -> None:
		initial_selection = [int(self.string.get())]
		ItemSelectDialog.ItemSelectDialog(parent=self, title='Select String', delegate=self, selected=initial_selection)
		# s = StringEditor(self, 'Select a String', True, self.string.get())
		# if s.result is not None:
		# 	self.string.set(s.result)

	# ItemSelectDialog.Delegate
	def get_items(self) -> Sequence[ItemSelectDialog.Item]:
		strings = self.delegate.get_data_context().stattxt_strings()
		if not strings:
			return []
		return strings

	def item_selected(self, index: int) -> bool:
		self.string.set(str(index))
		return True

	def items_selected(self, indexes: list[int]) -> bool:
		return True

	def ok(self, _event: UI.Event | None = None) -> None:
		script_id = self.script_id.get()
		aibin = self.delegate.get_ai_bin()
		if self.initialid != script_id and aibin.get_script(script_id) is not None:
			replace = UI.MessageBox.askyesnocancel(parent=self, title='Replace Script?', message=f"The script with ID '{script_id}' already exists, replace it?", default=UI.MessageBox.YES)
			if replace is None:
				return
			if not replace:
				self.cancel()
				return
		if not self.string.get():
			self.string.set('0')
		PyMSDialog.ok(self)

	def cancel(self, _event: UI.Event | None = None) -> None:
		self.script_id.set('')
		PyMSDialog.ok(self)

	def dismiss(self) -> None:
		self.config_.save_size(self)
		PyMSDialog.dismiss(self)
