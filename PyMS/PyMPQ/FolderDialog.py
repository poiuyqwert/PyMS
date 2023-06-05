
from ..Utilities.UIKit import *
from ..Utilities.PyMSDialog import PyMSDialog
from ..Utilities.Settings import Settings

class FolderDialog(PyMSDialog):
	def __init__(self, parent, settings): # type: (Misc, Settings) -> None
		self.settings = settings
		self.save = True
		self.result = StringVar()
		self.result.set(self.settings['import'].get('add_folder', ''))
		PyMSDialog.__init__(self, parent, 'Folder name...')

	def widgetize(self): # type: () -> (Widget | None)
		Label(self, text='The text in the box below will be put at the beginnings of the\nnames of every file you selected.\n\nExample: If "title.wav" is the original filename, and you type\n"music\\" the file will become "music\\title.wav"', anchor=W, justify=LEFT).pack(padx=5, pady=5)
		entry = Entry(self, textvariable=self.result)
		entry.icursor(END)
		entry.pack(padx=5, fill=X)

		buttons = Frame(self)
		Button(buttons, text='Ok', width=10, command=self.ok).pack(side=LEFT, padx=3, pady=3)
		Button(buttons, text='Cancel', width=10, command=self.cancel).pack(padx=3, pady=3)
		buttons.pack()

		self.bind(Key.Return(), self.ok)
		def select_all(*_):
			entry.select_to(END)
			entry.icursor(END)
		self.bind(Ctrl.a(), select_all)

		return entry

	def cancel(self, e=None): # type: (Event | None) -> None
		self.save = False
		PyMSDialog.cancel(self)

	def ok(self, *_): # type: (Event | None) -> None
		self.settings['import'].add_folder = self.result.get()
		PyMSDialog.ok(self)
