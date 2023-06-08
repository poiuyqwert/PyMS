
from ..Utilities.PyMSDialog import PyMSDialog
from ..Utilities.UIKit import *
from ..Utilities.Settings import Settings

from typing import TYPE_CHECKING, Callable
if TYPE_CHECKING:
	from .DATData import DATData

class EntryCountDialog(PyMSDialog):
	def __init__(self, parent, callback, dat_data, settings): # type: (Widget, Callable[[int], None], DATData, Settings) -> None
		assert dat_data.dat is not None
		self.callback = callback
		self.dat_data = dat_data
		self.resulting_count_var = None # type: StringVar | None
		self.result = IntegerVar(dat_data.entry_count(), [1,dat_data.dat.FORMAT.expanded_max_entries])
		self.settings = settings
		PyMSDialog.__init__(self, parent, 'How many entries?', resizable=(True,False))

	def widgetize(self): # type: () -> (Misc | None)
		assert self.dat_data.dat is not None
		Label(self, text='How many entres to set for %s?' % self.dat_data.dat.FILE_NAME).pack(padx=5, pady=5)
		Entry(self, textvariable=self.result).pack(padx=5, fill=X)

		details = []
		if self.dat_data.dat.FORMAT.expanded_min_entries:
			details.append(' - Minimum expanded entries: %d' % self.dat_data.dat.FORMAT.expanded_min_entries)
		if self.dat_data.dat.FORMAT.expanded_max_entries:
			details.append(' - Maximum expanded entries: %d' % self.dat_data.dat.FORMAT.expanded_max_entries)
		if self.dat_data.dat.FORMAT.expanded_entries_multiple:
			details.append(' - Expanded entries multiple: %d' % self.dat_data.dat.FORMAT.expanded_entries_multiple)
		if self.dat_data.dat.FORMAT.expanded_entries_reserved:
			details.append(' - Some entries are reserved')
		if details:
			Label(self, text='Constraints:\n' + '\n'.join(details), justify=LEFT, anchor=W).pack(padx=5,pady=5, fill=X)
			self.resulting_count_var = StringVar()
			Label(self, textvariable=self.resulting_count_var, justify=LEFT, anchor=W).pack(padx=5,pady=(0,5), fill=X)
			self.result.trace('w', self.update_resulting_count)
			self.update_resulting_count()

		buttons = Frame(self)
		ok = Button(buttons, text='Ok', width=10, command=self.ok)
		ok.pack(side=LEFT, padx=3, pady=3)
		Button(buttons, text='Cancel', width=10, command=self.cancel).pack(padx=3, pady=3)
		buttons.pack()

		return ok

	def update_resulting_count(self, *_): # type: (Any) -> None
		assert self.dat_data.dat is not None
		if not self.resulting_count_var:
			return
		resulting_count = self.dat_data.dat.expanded_count(self.result.get())
		self.resulting_count_var.set('Resulting entry count: %d' % resulting_count)

	def setup_complete(self): # type: () -> None
		self.settings.window.load_window_size('entry_count', self)

	def ok(self, _=None): # type: (Event | None) -> None
		current_entry_count = self.dat_data.entry_count()
		if self.result.get() < current_entry_count:
			MessageBox.showerror(parent=self, title='Invalid Entry Count', message="The entry count can't be set to less than the current entries (%d)." % current_entry_count)
			self.result.set(current_entry_count)
			return
		self.callback(self.result.get())
		PyMSDialog.ok(self)

	def dismiss(self): # type: () -> None
		self.settings.window.save_window_size('entry_count', self)
		PyMSDialog.dismiss(self)
