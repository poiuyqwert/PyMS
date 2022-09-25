
from .Locales import LOCALE_CHOICES

from ..Utilities.UIKit import *
from ..Utilities.IntegerVar import IntegerVar
from ..Utilities.PyMSDialog import PyMSDialog
from ..Utilities.EntryDropDown import EntryDropDown

class LocaleDialog(PyMSDialog):
	def __init__(self, parent, locale=0, title='Change locale for files', message='Type or choose the new locale id for the select files'):
		self.save = True
		self.result = IntegerVar(0,[0,65535])
		self.result.set(locale)
		self.message = message
		PyMSDialog.__init__(self, parent, title)

	def widgetize(self):
		Label(self, text=self.message + ':', anchor=W, justify=LEFT).pack(padx=5, pady=5)
		entry_dropdown = EntryDropDown(self, self.result, LOCALE_CHOICES, entry_width=5, dropdown_width=20)
		entry_dropdown.pack()

		buttons = Frame(self)
		ok = Button(buttons, text='Ok', width=10, command=self.ok)
		ok.pack(side=LEFT, padx=3, pady=3)
		Button(buttons, text='Cancel', width=10, command=self.cancel).pack(padx=3, pady=3)
		buttons.pack()

		return entry_dropdown.entry

	def cancel(self):
		self.save = False
		PyMSDialog.cancel(self)
