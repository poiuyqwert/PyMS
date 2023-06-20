
from ..Widgets import *

class MaskedRadiobutton(Radiobutton):
	def __init__(self, parent: Misc, **options) -> None:
		self._mask = options['mask']
		del options['mask']
		self._real_variable: IntVar = options['variable']
		self._real_variable.trace('w', self._update_state)
		if not hasattr(self._real_variable, '_masked_radio_variable'):
			setattr(self._real_variable, '_masked_radio_variables', {})
		_masked_radio_variables = getattr(self._real_variable, '_masked_radio_variables')
		if not self._mask in _masked_radio_variables:
			_masked_radio_variables[self._mask] = IntVar()
			_masked_radio_variables[self._mask].trace('w', self._update_value)
		self._variable = _masked_radio_variables[self._mask]
		options['variable'] = self._variable
		Radiobutton.__init__(self, parent, **options)
		self._update_state()

	def _update_state(self, *_) -> None:
		try:
			raw = self._real_variable.get()
		except:
			return
		value = (raw & self._mask)
		if value != self._variable.get():
			self._variable.set(value)

	def _update_value(self, *_) -> None:
		value = self._variable.get()
		cur_value = self._real_variable.get()
		if value != (cur_value & self._mask):
			value |= (cur_value & ~self._mask)
			self._real_variable.set(value)
