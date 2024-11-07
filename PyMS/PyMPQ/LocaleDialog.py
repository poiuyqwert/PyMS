
from .Locales import LOCALE_CHOICES

from ..Utilities.UIKit import *
from ..Utilities.PyMSDialog import PyMSDialog

class LocaleDialog(PyMSDialog):
	def __init__(self, parent: Misc, locale: int = 0, title: str = 'Change locale for files', message: str = 'Type or choose the new locale id for the select files') -> None:
		self.save = True
		self.result = IntegerVar(0,[0,65535])
		self.result.set(locale)
		self.message = message
		PyMSDialog.__init__(self, parent, title)

	def widgetize(self) -> Widget | None:
		Label(self, text=self.message + ':', anchor=W, justify=LEFT).pack(padx=5, pady=5)
		entry_dropdown = EntryDropDown(self, self.result, LOCALE_CHOICES, entry_width=5, dropdown_width=20)
		entry_dropdown.pack()

		buttons = Frame(self)
		ok = Button(buttons, text='Ok', width=10, command=self.ok)
		ok.pack(side=LEFT, padx=3, pady=3)
		Button(buttons, text='Cancel', width=10, command=self.cancel).pack(padx=3, pady=3)
		buttons.pack()

		return entry_dropdown.entry

	def cancel(self, e: Event | None = None) -> None:
		self.save = False
		PyMSDialog.cancel(self)
