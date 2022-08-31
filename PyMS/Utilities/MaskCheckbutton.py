
from .UIKit import Checkbutton, IntVar

class MaskCheckbutton(Checkbutton):
	def __init__(self, parent, **options):
		self._value = options['value']
		del options['value']
		self._real_variable = options['variable']
		self._real_variable.trace('w', self._update_state)
		self._variable = IntVar()
		self._variable.trace('w', self._update_value)
		options['variable'] = self._variable
		Checkbutton.__init__(self, parent, **options)
		self._update_state()

	def _update_state(self, *_):
		try:
			raw = self._real_variable.get()
		except:
			return
		on = ((raw & self._value) == self._value)
		if on != self._variable.get():
			self._variable.set(on)

	def _update_value(self, *_):
		value = self._real_variable.get()
		cur_on = ((value & self._value) == self._value)
		on = self._variable.get()
		if on and not cur_on:
			value |= self._value
			self._real_variable.set(value)
		elif not on and cur_on:
			value &= ~self._value
			self._real_variable.set(value)
