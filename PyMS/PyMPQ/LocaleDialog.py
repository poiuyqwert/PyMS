
from .Locales import LOCALE_CHOICES

from ..Utilities import UIKit as UI
from ..Utilities.PyMSDialog import PyMSDialog

class LocaleDialog(PyMSDialog):
	def __init__(self, parent: UI.Misc, locale: int = 0, title: str = 'Change locale for files', message: str = 'Type or choose the new locale id for the select files') -> None:
		self.save = True
		self.result = UI.IntegerVar(0,[0,65535])
		self.result.set(locale)
		self.message = message
		PyMSDialog.__init__(self, parent, title)

	def widgetize(self) -> UI.Widget | None:
		UI.Label(self, text=self.message + ':', anchor=UI.W, justify=UI.LEFT).pack(padx=5, pady=5)
		entry_dropdown = UI.EntryDropDown(self, self.result, LOCALE_CHOICES, entry_width=5, dropdown_width=20)
		entry_dropdown.pack()

		buttons = UI.Frame(self)
		ok = UI.Button(buttons, text='Ok', width=10, command=self.ok)
		ok.pack(side=UI.LEFT, padx=3, pady=3)
		UI.Button(buttons, text='Cancel', width=10, command=self.cancel).pack(padx=3, pady=3)
		buttons.pack()

		return entry_dropdown.entry

	def cancel(self, _event: UI.Event | None = None) -> None:
		self.save = False
		PyMSDialog.cancel(self)
