
from ....FileFormats.AIBIN.AIBIN import AIBIN, LoadIssue

from ....Utilities.UIKit import Misc, Widget
from ....Utilities.Callback import Callback

from typing import Protocol

class Resolution(Protocol):
	update_callback: Callback[[]]

	def name(self) -> str:
		...

	def ui(self, parent: Misc) -> Widget | None:
		...

	# Return a `str` for reason why can't resolve, or `None` for can resolve
	def can_resolve(self, ai: AIBIN, issue: LoadIssue) -> str | None:
		...

	def resolve(self, ai: AIBIN, issue: LoadIssue):
		...
