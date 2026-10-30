
from ..Utilities import UIKit as UI
from ..Utilities.PyMSDialog import PyMSDialog
from ..Utilities import Config

class FolderDialog(PyMSDialog):
	def __init__(self, parent: UI.Misc, prefix_config: Config.String) -> None:
		self.prefix_config = prefix_config
		self.save = True
		self.result = UI.StringVar()
		self.result.set(self.prefix_config.value or '')
		PyMSDialog.__init__(self, parent, 'Folder name...')

	def widgetize(self) -> UI.Widget | None:
		UI.Label(self, text='The text in the box below will be put at the beginnings of the\nnames of every file you selected.\n\nExample: If "title.wav" is the original filename, and you type\n"music\\" the file will become "music\\title.wav"', anchor=UI.W, justify=UI.LEFT).pack(padx=5, pady=5)
		entry = UI.Entry(self, textvariable=self.result)
		entry.icursor(UI.END)
		entry.pack(padx=5, fill=UI.X)

		buttons = UI.Frame(self)
		UI.Button(buttons, text='Ok', width=10, command=self.ok).pack(side=UI.LEFT, padx=3, pady=3)
		UI.Button(buttons, text='Cancel', width=10, command=self.cancel).pack(padx=3, pady=3)
		buttons.pack()

		self.bind(UI.Key.Return(), self.ok)
		def select_all(_event: UI.Event) -> None:
			entry.select_to(UI.END)
			entry.icursor(UI.END)
		self.bind(UI.Ctrl.a(), select_all)

		return entry

	def cancel(self, _event: UI.Event | None = None) -> None:
		self.save = False
		PyMSDialog.cancel(self)

	def ok(self, _event: UI.Event | None = None) -> None:
		self.prefix_config.value = self.result.get()
		PyMSDialog.ok(self)
