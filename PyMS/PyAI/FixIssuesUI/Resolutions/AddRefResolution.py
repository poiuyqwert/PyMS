
from .Resolution import Resolution

from ....FileFormats.AIBIN.AIBIN import AIBIN, LoadIssue, AIScript

from ....Utilities.UIKit import Misc, Widget
from ....Utilities.Callback import Callback

class AddRefResolution(Resolution):
	def __init__(self) -> None:
		self.update_callback = Callback()

	def name(self) -> str:
		return f'Add definition to aiscript.bin'

	def ui(self, parent: Misc) -> Widget | None:
		return None

	def can_resolve(self, ai: AIBIN, issue: LoadIssue) -> str | None:
		return None

	def resolve(self, ai: AIBIN, issue: LoadIssue):
		script = AIScript(issue.script_id, 0, 0, issue.entry_point, False)
		ai.add_script(script)
