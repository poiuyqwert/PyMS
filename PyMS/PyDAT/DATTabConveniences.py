
from ..Utilities.utils import fit, float_to_str
from ..Utilities.Tooltip import Tooltip
from ..Utilities.UIKit import Checkbutton

class DATTabConveniences(object):
	def tip(self, obj, tipname, hint):
		Tooltip(obj, '%s:\n' % tipname + fit('  ', self.toplevel.data_context.hints[hint], end=True)[:-1])

	def makeCheckbox(self, frame, var, txt, hint):
		c = Checkbutton(frame, text=txt, variable=var)
		self.tip(c, txt, hint)
		return c

	def update_ticks(self, time, variable):
		variable.check = False
		variable.set(int(float(time) * self.toplevel.data_context.ticks_per_second))

	def update_time(self, ticks, variable):
		variable.check = False
		variable.set(float_to_str(int(ticks) / float(self.toplevel.data_context.ticks_per_second)))
