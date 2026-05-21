
from .Resolution import Resolution

from ....FileFormats.AIBIN.AIBIN import AIBIN, LoadIssue, AIScript

from ....Utilities.UIKit import *
from ....Utilities.Callback import Callback

class ChangeIDResolution(Resolution):
	def __init__(self, in_bwscript: bool) -> None:
		self.in_bwscript = in_bwscript
		self.new_id = StringVar()
		self.update_callback = Callback()
		self.new_id.trace_add('write', lambda a,b,c: self.update_callback())

	def name(self) -> str:
		return f'Change script ID in {"bw" if self.in_bwscript else "ai"}script.bin'

	def ui(self, parent: Misc) -> Widget | None:
		ui = ChangeIDUI(parent, self.new_id)
		ui.pack(side=LEFT)
		return ui

	def can_resolve(self, ai: AIBIN, issue: LoadIssue) -> str | None:
		new_id = self.new_id.get()
		if len(new_id) != 4:
			return 'Invalid script ID (must be 4 characters)'
		if ' ' in new_id or '\t' in new_id:
			return 'Invalid script ID (can\'t contain whitespace)'
		if ai.get_script(new_id) is not None:
			return 'Script ID already exists'
		return None

	def resolve(self, ai: AIBIN, issue: LoadIssue) -> None:
		new_id = self.new_id.get()
		ai_script = ai.get_script(issue.script_id)
		assert ai_script is not None
		if self.in_bwscript:
			bw_script = AIScript(new_id, ai_script.flags, ai_script.string_id, issue.entry_point, True)
			ai.add_script(bw_script)
		else:
			ai.remove_script(issue.script_id)
			ai_script.id = new_id
			ai.add_script(ai_script)

class ChangeIDUI(Frame):
	def __init__(self, parent: Misc, new_id: StringVar) -> None:
		super().__init__(parent)

		Label(self, text='New script ID: ').pack(side=LEFT)
		Entry(self, textvariable=new_id, width=4).pack(side=LEFT)
