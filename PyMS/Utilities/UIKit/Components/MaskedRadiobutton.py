
from ..Widgets import *

from typing import Any

class MaskedRadiobutton(Radiobutton):
	def __init__(self, parent: Misc, **options: Any) -> None:
		self._mask: int = options['mask']
		del options['mask']
		self._real_variable: IntVar = options['variable']
		self._real_variable.trace_add('write', self._update_state)
		if not hasattr(self._real_variable, '_masked_radio_variable'):
			setattr(self._real_variable, '_masked_radio_variables', {})
		_masked_radio_variables: dict[int, IntVar] = getattr(self._real_variable, '_masked_radio_variables')
		if not self._mask in _masked_radio_variables:
			_masked_radio_variables[self._mask] = IntVar()
			_masked_radio_variables[self._mask].trace_add('write', self._update_value)
		self._variable = _masked_radio_variables[self._mask]
		options['variable'] = self._variable
		Radiobutton.__init__(self, parent, **options)
		self._update_state()

	def _update_state(self, *_: Any) -> None:
		try:
			raw = self._real_variable.get()
		except Exception:
			return
		value = (raw & self._mask)
		if value != self._variable.get():
			self._variable.set(value)

	def _update_value(self, *_: Any) -> None:
		value = self._variable.get()
		cur_value = self._real_variable.get()
		if value != (cur_value & self._mask):
			value |= (cur_value & ~self._mask)
			self._real_variable.set(value)
