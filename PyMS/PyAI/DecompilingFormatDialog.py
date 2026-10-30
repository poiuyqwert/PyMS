
from .Config import PyAIConfig
from .DecompilingFormat import BlockFormat, CommandFormat, CommentFormat

from ..Utilities import UIKit as UI
from ..Utilities.PyMSDialog import PyMSDialog

class DecompilingFormatDialog(PyMSDialog):
	def __init__(self, parent: UI.Misc, config: PyAIConfig.Code.DecompFormat):
		self.config_ = config
		PyMSDialog.__init__(self, parent, 'Decompiling Format', resizable=(False, False))

	def widgetize(self) -> UI.Widget | None:
		frame = UI.Frame(self)
		UI.Label(frame, text='Block:', anchor=UI.E).grid(row=0, column=0, sticky=UI.EW)
		self.block_combobox = UI.Combobox(frame, state=UI.READONLY, values=[format.label for format in BlockFormat.all()])
		self.block_combobox.current(BlockFormat.all().index(self.config_.block.value))
		self.block_combobox.grid(row=0, column=1, sticky=UI.EW)
		UI.Label(frame, text='Command:', anchor=UI.E).grid(row=1, column=0, sticky=UI.EW)
		self.command_combobox = UI.Combobox(frame, state=UI.READONLY, values=[format.label for format in CommandFormat.all()])
		self.command_combobox.current(CommandFormat.all().index(self.config_.command.value))
		self.command_combobox.grid(row=1, column=1, sticky=UI.EW)
		UI.Label(frame, text='Comment:', anchor=UI.E).grid(row=2, column=0, sticky=UI.EW)
		self.comment_combobox = UI.Combobox(frame, state=UI.READONLY, values=[format.label for format in CommentFormat.all()])
		self.comment_combobox.current(CommentFormat.all().index(self.config_.comment.value))
		self.comment_combobox.grid(row=2, column=1, sticky=UI.EW)
		frame.grid_columnconfigure(0, weight=0)
		frame.grid_columnconfigure(1, weight=1)
		frame.pack(pady=3, padx=3, fill=UI.X)

		UI.Label(self, text='Note: Code can be parsed in any of the above formats.\nThis just controls your preferred default format when decompiling.').pack(pady=10, padx=3, fill=UI.X)

		buttons = UI.Frame(self)
		ok = UI.Button(buttons, text='Ok', width=10, command=self.ok)
		ok.pack(side=UI.LEFT, padx=(1, 10), pady=3)
		UI.Button(buttons, text='Cancel', width=10, command=self.cancel).pack(side=UI.LEFT, padx=(10, 1), pady=3)
		buttons.pack(side=UI.BOTTOM, pady=3, padx=3)

		return ok

	def ok(self, _event: UI.Event | None = None) -> None:
		self.config_.block.value = BlockFormat.all()[self.block_combobox.current()]
		self.config_.command.value = CommandFormat.all()[self.command_combobox.current()]
		self.config_.comment.value = CommentFormat.all()[self.comment_combobox.current()]
		PyMSDialog.ok(self)
