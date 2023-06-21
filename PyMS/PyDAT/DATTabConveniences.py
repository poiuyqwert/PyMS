
from __future__ import annotations

from __future__ import annotations

from ..Utilities.utils import fit, float_to_str
from ..Utilities.UIKit import *

from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from .Delegates import MainDelegate

class DATTabConveniences(object):
	delegate: MainDelegate

	def tip(self, obj, tipname, hint): # type: (Widget, str, str) -> None
		Tooltip(obj, '%s:\n' % tipname + fit('  ', self.delegate.data_context.hints[hint], end=True)[:-1])

	def makeCheckbox(self, frame, var, txt, hint): # type: (Misc, Variable, str, str) -> Checkbutton
		c = Checkbutton(frame, text=txt, variable=var)
		self.tip(c, txt, hint)
		return c

	def update_ticks(self, time, variable): # type: (int, IntegerVar) -> None
		# variable.check = False
		variable.set(int(float(time) * self.delegate.data_context.ticks_per_second))

	def update_time(self, ticks, variable): # type: (int, FloatVar) -> None
		variable.check = False
		variable.set(float_to_str(int(ticks) / float(self.delegate.data_context.ticks_per_second)))
