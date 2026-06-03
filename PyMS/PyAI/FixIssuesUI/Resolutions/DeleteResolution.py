
from .Resolution import Resolution

from ....FileFormats.AIBIN.AIBIN import AIBIN, LoadIssue, AIScript

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
		if self.from_bwscript:
			return None
		script = ai.get_script(issue.script_id)
		if script is None:
			return None
		# Replacing the aiscript.bin entry point with the (possibly larger) bwscript.bin block could overflow aiscript.bin
		simulated = AIScript(script.id, script.flags, script.string_id, issue.entry_point, False)
		ai_size, _ = ai.can_add_scripts([simulated])
		if ai_size is not None:
			return f"There is not enough room in aiscript.bin for this script (would be {ai_size}B out of the max {ai.max_size()}B)"
		return None

	def resolve(self, ai: AIBIN, issue: LoadIssue) -> None:
		if self.from_bwscript:
			return
		script = ai.get_script(issue.script_id)
		assert script is not None
		script.entry_point = issue.entry_point
