
from .Resolution import Resolution

from ....FileFormats.AIBIN.AIBIN import AIBIN, LoadIssue

from ....Utilities.UIKit import Misc, Widget
from ....Utilities.Callback import Callback

class DeleteResolution(Resolution):
	def __init__(self, from_bwscript: bool) -> None:
		self.from_bwscript = from_bwscript
		self.update_callback = Callback()

	def name(self) -> str:
		if self.from_bwscript:
			return 'Delete script from bwscript.bin'
		return 'Replace script in aiscript.bin with one in bwscript.bin'

	def ui(self, parent: Misc) -> Widget | None:
		return None

	def can_resolve(self, ai: AIBIN, issue: LoadIssue) -> str | None:
		# TODO: Check file size
		return None

	def resolve(self, ai: AIBIN, issue: LoadIssue) -> None:
		if self.from_bwscript:
			return
		script = ai.get_script(issue.script_id)
		assert script is not None
		script.entry_point = issue.entry_point
