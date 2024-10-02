
from .Delegates import MainDelegate

from ..FileFormats.AIBIN.AIScript import AIScript

from ..Utilities.UIKit import *
from ..Utilities.PyMSDialog import PyMSDialog
from ..Utilities.Config import WindowGeometry
from ..Utilities.utils import binary

import re

class ScriptLocation:
	aiscript = 1
	bwscript = 2
	either = aiscript | bwscript

class FindScriptDialog(PyMSDialog):
	def __init__(self, parent: AnyWindow, config: WindowGeometry, delegate: MainDelegate):
		self.config_ = config
		self.delegate = delegate

		self.results = False
		self.id = StringVar()
		self.bw = IntVar(value=ScriptLocation.either)
		self.flags = StringVar()
		self.stringid = StringVar()
		self.string = StringVar()
		self.casesens = IntVar()
		self.regex = IntVar()

		self.reset_entry: Entry | None = None
		self.reset_color: str | None = None
		self.reset_timer: str | None = None

		self.matching_scripts: list[AIScript] = []

		PyMSDialog.__init__(self, parent, 'Find a Script')

	def widgetize(self) -> Widget:
		self.bind(Ctrl.a(), self.selectall)

		Label(self, text='AI ID', anchor=W).pack(fill=X)
		self.identry = Entry(self, textvariable=self.id)
		self.identry.pack(fill=X)

		frame = Frame(self)
		Radiobutton(frame, text='aiscript.bin', variable=self.bw, value=ScriptLocation.aiscript).pack(side=LEFT)
		Radiobutton(frame, text='bwscript.bin', variable=self.bw, value=ScriptLocation.bwscript).pack(side=LEFT)
		Radiobutton(frame, text='Either', variable=self.bw, value=ScriptLocation.either).pack(side=LEFT)
		frame.pack(fill=X)

		Label(self, text='Flags', anchor=W).pack(fill=X)
		self.flagsentry = Entry(self, textvariable=self.flags)
		self.flagsentry.pack(fill=X)

		Label(self, text='String ID', anchor=W).pack(fill=X)
		frame = Frame(self)
		self.stringidentry = Entry(frame, textvariable=self.stringid)
		self.stringidentry.pack(side=LEFT, fill=X, expand=1)
		Button(frame, text='Browse...', width=10, command=self.browse).pack(side=RIGHT)
		frame.pack(fill=X)

		Label(self, text='String', anchor=W).pack(fill=X)
		self.stringentry = Entry(self, textvariable=self.string)
		self.stringentry.pack(fill=X)

		options = Frame(self)
		Checkbutton(options, text='Case Sensitive', variable=self.casesens).pack(side=LEFT, padx=3)
		Checkbutton(options, text='Regular Expressions', variable=self.regex).pack(side=LEFT, padx=3)
		options.pack(pady=3)

		self.listbox = ScrolledListbox(self, selectmode=EXTENDED, font=Font.fixed(), width=1, height=1)
		self.listbox.pack(fill=BOTH, padx=2, pady=2, expand=1)
		self.listbox.bind(WidgetEvent.Listbox.Select(), self.update)

		buttons = Frame(self)
		Button(buttons, text='Find', width=10, command=self.find, default=NORMAL).pack(side=LEFT, padx=3, pady=3)
		self.select = Button(buttons, text='Select', width=10, command=self.select_item, state=DISABLED)
		self.select.pack(side=LEFT, padx=3, pady=3)
		Button(buttons, text='Cancel', width=10, command=self.cancel).pack(side=LEFT, padx=3, pady=3)
		buttons.pack()

		self.bind(Key.Return(), self.find)

		return self.identry

	def setup_complete(self) -> None:
		self.minsize(300,325)
		self.config_.load_size(self)

	def update(self, e: Event | None = None) -> None:
		self.select['state'] = NORMAL

	def updatecolor(self) -> None:
		if self.reset_entry:
			if self.reset_timer:
				self.after_cancel(self.reset_timer)
				self.reset_timer = None
			self.reset_entry['bg'] = self.reset_color
			self.reset_entry = None

	def selectall(self, e: Event | None = None) -> None:
		if self.listbox.size():
			self.listbox.select_set(0, END)
			self.select['state'] = NORMAL

	def browse(self) -> None:
		from . import StringEditor
		try:
			s = int(self.stringid.get())
		except:
			s = 0
		s = StringEditor.StringEditor(self, 'Select a String', True, s)
		if s.result is not None:
			self.stringid.set(s.result)

	def update_listbox(self) -> None:
		self.listbox.delete(0, END)
		data_context = self.delegate.get_data_context()
		for script in self.matching_scripts:
			self.listbox.insert(END, f"{script.id}     {'BW' if script.in_bwscript else '  '}     {binary(script.flags, 3)}     {script.string_id}: {data_context.stattxt_string(script.string_id)}")

	def find(self, _: Event | None = None) -> None:
		self.updatecolor()
		self.listbox.delete(0,END)
		self.select['state'] = DISABLED

		def get_matcher(variable: StringVar, entry: Entry) -> re.Pattern | None:
			regex = variable.get()
			if not regex:
				return None
			if self.regex.get():
				if not regex.startswith('\\A'):
					regex = '.*' + regex
				if not regex.endswith('\\Z'):
					regex = regex + '.*'
			else:
				regex = '.*%s.*' % re.escape(regex)
			try:
				return re.compile(regex, re.I if self.casesens.get() else 0)
			except:
				self.reset_entry = entry
				self.reset_color = entry['bg']
				entry['bg'] = '#FFB4B4'
				self.reset_timer = self.after(1000, self.updatecolor)
				raise

		try:
			id_matcher = get_matcher(self.id, self.identry)
			flags_matcher = get_matcher(self.flags, self.flagsentry)
			stringid_matcher = get_matcher(self.stringid, self.stringidentry)
			string_matcher = get_matcher(self.string, self.stringentry)
		except:
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
			if string_matcher and not string_matcher.match(string):
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
