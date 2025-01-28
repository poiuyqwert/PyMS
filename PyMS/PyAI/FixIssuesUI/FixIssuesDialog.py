
from ..Config import PyAIConfig
from .Resolutions import *
from ..Delegates import MainDelegate
from .PreviewScriptDialog import PreviewScriptDialog

from ...FileFormats.AIBIN.AIBIN import AIBIN, LoadIssues, LoadIssue, LoadIssueReason
from ...FileFormats.AIBIN.AIScript import AIScript

from ...Utilities.UIKit import *
from ...Utilities.PyMSDialog import PyMSDialog
from ...Utilities.Callback import Callback
from ...Utilities.PyMSError import PyMSError
from ...Utilities.ErrorDialog import ErrorDialog

import io

class IssueResolution:
	def __init__(self, aibin: AIBIN, issue: LoadIssue):
		self.aibin = aibin
		self.issue = issue
		self.chosen_index = 0
		self.update_callback: Callback[[]] = Callback()
		self.resolution_options: list[Resolution]
		match issue.reason:
			case LoadIssueReason.unreferenced_bw:
				self.resolution_options = [DeleteResolution(from_bwscript=True), AddRefResolution()]
			case LoadIssueReason.duplicate_bw:
				self.resolution_options = [DeleteResolution(from_bwscript=True), DeleteResolution(from_bwscript=False), ChangeIDResolution(in_bwscript=True), ChangeIDResolution(in_bwscript=False)]
		for option in self.resolution_options:
			option.update_callback.add(self.update_callback)

	def reason_text(self) -> str:
		match self.issue.reason:
			case LoadIssueReason.unreferenced_bw:
				return "Script exists in bwscript.bin but is not defined in aiscript.bin"
			case LoadIssueReason.duplicate_bw:
				return "Script is in aiscript.bin but also exists in bwscript.bin"

	def list_name(self) -> str:
		detail = 'No resolution chosen'
		if self.chosen_index:
			resolution_chosen = self.resolution_options[self.chosen_index-1]
			if resolution_chosen.can_resolve(self.aibin, self.issue) is not None:
				detail = 'Incomplete resolution'
			else:
				detail = resolution_chosen.name()
		return f'{self.issue.script_id} ({detail})'

	def ui(self, parent: Misc) -> Widget | None:
		if not self.chosen_index:
			return None
		resolution_chosen = self.resolution_options[self.chosen_index-1]
		return resolution_chosen.ui(parent)

	def can_resolve(self) -> bool:
		if not self.chosen_index:
			return False
		resolution_chosen = self.resolution_options[self.chosen_index-1]
		if resolution_chosen.can_resolve(self.aibin, self.issue) is not None:
			return False
		return True

	def incomplete_text(self) -> str | None:
		if not self.chosen_index:
			return None
		resolution_chosen = self.resolution_options[self.chosen_index-1]
		return resolution_chosen.can_resolve(self.aibin, self.issue)

	def resolve(self) -> None:
		resolution_chosen = self.resolution_options[self.chosen_index-1]
		resolution_chosen.resolve(self.aibin, self.issue)

	def in_aiscript(self) -> bool:
		match self.issue.reason:
			case LoadIssueReason.unreferenced_bw:
				return False
			case LoadIssueReason.duplicate_bw:
				return True

	def in_bwscript(self) -> bool:
		return True

class FixIssuesDialog(PyMSDialog):
	def __init__(self, parent: Misc, aibin: AIBIN, issues: LoadIssues, delegate: MainDelegate, config: PyAIConfig) -> None:
		self.issue_resolutions = list(IssueResolution(aibin, issue) for issue in issues)
		for issue_resolution in self.issue_resolutions:
			issue_resolution.update_callback.add(self.issue_resolution_updated)
		self.cancelled = True
		self.delegate = delegate
		self.config_ = config
		super().__init__(parent, 'Resolve issues')

	def widgetize(self) -> Misc | None:
		WrappingLabel(self, text='There are issues with some scripts in the loaded files. This could be because the bwscript.bin loaded is not the correct pair of the loaded aiscrip.bin, or that the files are slightly broken. Please review each script and choose how to resolve their issues, or cancel the loading entirely.', justify=LEFT, anchor=W).pack(fill=X, padx=5, pady=5)

		details_frame = Frame(self)
		frame = Frame(details_frame)
		Label(frame, text='Scripts:', justify=LEFT, anchor=W).pack(fill=X)
		self.scripts_listbox = ScrolledListbox(frame, width=30)
		self.scripts_listbox.pack(fill=BOTH, expand=True)
		self.scripts_listbox.bind(WidgetEvent.Listbox.Select.event(), self.issue_selection_changed)
		frame.pack(side=LEFT, padx=5, pady=5, fill=BOTH, expand=True)

		frame = Frame(details_frame)
		Label(frame, text='Issue:', justify=LEFT, anchor=W).pack(fill=X)
		self.issue_text = StringVar()
		WrappingLabel(frame, textvariable=self.issue_text, justify=LEFT, anchor=W, font=Font.default().bolded()).pack(fill=X)
		buttons_frame = Frame(frame)
		self.preview_aiscript_button = Button(buttons_frame, text='Preview AI script', command=self.preview_aiscript)
		self.preview_aiscript_button.pack(side=LEFT)
		self.preview_bwscript_button = Button(buttons_frame, text='Preview BW script', command=self.preview_bwscript)
		self.preview_bwscript_button.pack(side=LEFT, padx=(10, 0))
		buttons_frame.pack(fill=X)
		Label(frame, text='Resolution:', justify=LEFT, anchor=W).pack(fill=X, pady=(5, 0))
		self.resolution_combobox = Combobox(frame, state=READONLY, values=[])
		self.resolution_combobox.bind(WidgetEvent.Combobox.Selected(), self.resolution_selection_changed)
		self.resolution_combobox.pack(fill=X)
		self.resolution_container = Frame(frame)
		self.resolution_container.pack(fill=BOTH, expand=True)
		self.resolution_ui: Widget | None = None
		self.resolution_incomplete = StringVar()
		WrappingLabel(frame, textvariable=self.resolution_incomplete, justify=LEFT, anchor=W, font=Font.default().bolded()).pack(fill=X)
		frame.pack(side=LEFT, fill=BOTH, expand=True, padx=5, pady=5)
		details_frame.pack(fill=BOTH, expand=True)

		frame = Frame(self)
		self.resolve_button = Button(frame, text='Resolve', width=10, command=self.resolve, state=DISABLED)
		self.resolve_button.pack(side=LEFT, padx=3)
		cancel_button = Button(frame, text='Cancel', width=10, command=self.cancel)
		cancel_button.pack(side=LEFT, padx=3)
		frame.pack(pady=10, padx=5)

		self.refresh_list()
		self.issue_selection_changed()

		return cancel_button

	def setup_complete(self) -> None:
		self.minsize(700, 420)
		self.config_.windows.fix_issues.resolutions.load_size(self)

	def preview_aiscript(self) -> None:
		issue_resolution = self.current_issue_resolution()
		try:
			output = io.StringIO()
			serialize_context = self.delegate.get_serialize_context(output)
			issue_resolution.aibin.decompile(serialize_context, [issue_resolution.issue.script_id])
			code = output.getvalue()
		except PyMSError as e:
			ErrorDialog(self, e)
			return
		PreviewScriptDialog(self, code, f'Preview script `{issue_resolution.issue.script_id}` from aiscript.bin', self.config_.windows.fix_issues.preview_code, self.config_.code.highlights)

	def preview_bwscript(self) -> None:
		issue_resolution = self.current_issue_resolution()
		try:
			output = io.StringIO()
			serialize_context = self.delegate.get_serialize_context(output)
			aibin = AIBIN()
			aibin.add_script(AIScript(issue_resolution.issue.script_id, 0, 0, issue_resolution.issue.entry_point, True))
			aibin.decompile(serialize_context, [issue_resolution.issue.script_id])
			code = output.getvalue()
		except PyMSError as e:
			ErrorDialog(self, e)
			return
		PreviewScriptDialog(self, code, f'Preview script `{issue_resolution.issue.script_id}` from bwscript.bin', self.config_.windows.fix_issues.preview_code, self.config_.code.highlights)

	def refresh_list(self) -> None:
		issue_index: int = 0
		if selection := self.scripts_listbox.curselection():
			issue_index = selection[0]
		rows = [issue_resolution.list_name() for issue_resolution in self.issue_resolutions]
		self.scripts_listbox.delete(0, END)
		self.scripts_listbox.insert(END, *rows)
		self.scripts_listbox.select_set(issue_index)

	def action_states(self) -> None:
		can_resolve = True
		for issue_resolution in self.issue_resolutions:
			if not issue_resolution.can_resolve():
				can_resolve = False
				break
		self.resolve_button['state'] = NORMAL if can_resolve else DISABLED

		issue_resolution = self.current_issue_resolution()
		self.preview_aiscript_button['state'] = NORMAL if issue_resolution.in_aiscript() else DISABLED
		self.preview_bwscript_button['state'] = NORMAL if issue_resolution.in_bwscript() else DISABLED

	def current_issue_resolution(self) -> IssueResolution:
		issue_index = 0
		if selection := self.scripts_listbox.curselection():
			issue_index = selection[0]
		return self.issue_resolutions[issue_index]

	def issue_selection_changed(self, event: Event | None = None) -> None:
		issue_resolution = self.current_issue_resolution()
		self.issue_text.set(issue_resolution.reason_text())
		self.resolution_combobox['values'] = ['[Choose a resolution]'] + [resolution.name() for resolution in issue_resolution.resolution_options]
		self.resolution_combobox.current(issue_resolution.chosen_index)
		self.resolution_selection_changed()
		self.action_states()

	def resolution_selection_changed(self, event: Event | None = None) -> None:
		issue_resolution = self.current_issue_resolution()
		if self.resolution_combobox.current() != issue_resolution.chosen_index:
			issue_resolution.chosen_index = self.resolution_combobox.current()
			self.refresh_list()
			self.action_states()
		self.issue_resolution_updated()
		if self.resolution_ui:
			self.resolution_ui.pack_forget()
		self.resolution_ui = issue_resolution.ui(self.resolution_container)

	def issue_resolution_updated(self) -> None:
		issue_resolution = self.current_issue_resolution()
		self.resolution_incomplete.set(issue_resolution.incomplete_text() or '')
		self.refresh_list()

	def resolve(self) -> None:
		for issue_resolution in self.issue_resolutions:
			issue_resolution.resolve()
		self.cancelled = False
		self.ok()

	def dismiss(self) -> None:
		self.config_.windows.fix_issues.resolutions.save_size(self)
		PyMSDialog.dismiss(self)
