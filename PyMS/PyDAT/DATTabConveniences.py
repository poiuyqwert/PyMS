
from __future__ import annotations

from ..Utilities.utils import fit, float_to_str
from ..Utilities import UIKit as UI

from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from .Delegates import MainDelegate

class DATTabConveniences:
	delegate: MainDelegate

	def tip(self, obj: UI.Widget, tipname: str, hint: str) -> None:
		hint_text = self.delegate.data_context.hints.get(hint)
		if hint_text is None:
			body = f"  Could not load hint '{hint}'"
		else:
			body = fit("  ", hint_text, end=True)[:-1]
		UI.Tooltip(obj, f'{tipname}:\n{body}')

	def makeCheckbox(self, frame: UI.Misc, var: UI.Variable, txt: str, hint: str) -> UI.Checkbutton:
		c = UI.Checkbutton(frame, text=txt, variable=var)
		self.tip(c, txt, hint)
		return c

	def update_ticks(self, time: int, variable: UI.IntegerVar) -> None:
		# variable.check = False
		variable.set(int(float(time) * self.delegate.data_context.ticks_per_second))

	def update_time(self, ticks: int, variable: UI.FloatVar) -> None:
		variable.check = False
		variable.set(float_to_str(int(ticks) / float(self.delegate.data_context.ticks_per_second)))
