
from .UIKit import Radiobutton, IntVar

class MaskedRadiobutton(Radiobutton):
	def __init__(self, parent, **options):
		self._mask = options['mask']
		del options['mask']
		self._real_variable = options['variable']
		self._real_variable.trace('w', self._update_state)
		if not hasattr(self._real_variable, '_masked_radio_variable'):
			self._real_variable._masked_radio_variables = {}
		if not self._mask in self._real_variable._masked_radio_variables:
			self._real_variable._masked_radio_variables[self._mask] = IntVar()
			self._real_variable._masked_radio_variables[self._mask].trace('w', self._update_value)
		self._variable = self._real_variable._masked_radio_variables[self._mask]
		options['variable'] = self._variable
		Radiobutton.__init__(self, parent, **options)
		self._update_state()

	def _update_state(self, *_):
		try:
			raw = self._real_variable.get()
		except:
			return
		value = (raw & self._mask)
		if value != self._variable.get():
			self._variable.set(value)

	def _update_value(self, *_):
		value = self._variable.get()
		cur_value = self._real_variable.get()
		if value != (cur_value & self._mask):
			value |= (cur_value & ~self._mask)
			self._real_variable.set(value)
