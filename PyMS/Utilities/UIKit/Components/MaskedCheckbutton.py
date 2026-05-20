
from ..Widgets import *

from typing import Any

class MaskedCheckbutton(Checkbutton):
	def __init__(self, parent: Misc, **options: Any) -> None:
		self._value = options['value']
		del options['value']
		self._real_variable: IntVar = options['variable']
		self._real_variable.trace_add('write', self._update_state)
		self._variable = IntVar()
		self._variable.trace_add('write', self._update_value)
		options['variable'] = self._variable
		Checkbutton.__init__(self, parent, **options)
		self._update_state()

	def _update_state(self, *_: Any) -> None:
		try:
			raw = self._real_variable.get()
		except:
			return
		on = ((raw & self._value) == self._value)
		if on != self._variable.get():
			self._variable.set(on)

	def _update_value(self, *_: Any) -> None:
		value = self._real_variable.get()
		cur_on = ((value & self._value) == self._value)
		on = self._variable.get()
		if on and not cur_on:
			value |= self._value
			self._real_variable.set(value)
		elif not on and cur_on:
			value &= ~self._value
			self._real_variable.set(value)
