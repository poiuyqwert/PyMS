
from .Config import PyAIConfig
from .DecompilingFormat import BlockFormat, CommandFormat, CommentFormat

from ..Utilities.UIKit import *
from ..Utilities.PyMSDialog import PyMSDialog

class DecompilingFormatDialog(PyMSDialog):
	def __init__(self, parent, config: PyAIConfig.Code.DecompFormat):
		self.config_ = config
		PyMSDialog.__init__(self, parent, 'Decompiling Format', resizable=(False, False))

	def widgetize(self) -> Widget | None:
		frame = Frame(self)
		Label(frame, text='Block:', anchor=E).grid(row=0, column=0, sticky=EW)
		self.block_combobox = Combobox(frame, state=READONLY, values=[format.label for format in BlockFormat.all()])
		self.block_combobox.current(BlockFormat.all().index(self.config_.block.value))
		self.block_combobox.grid(row=0, column=1, sticky=EW)
		Label(frame, text='Command:', anchor=E).grid(row=1, column=0, sticky=EW)
		self.command_combobox = Combobox(frame, state=READONLY, values=[format.label for format in CommandFormat.all()])
		self.command_combobox.current(CommandFormat.all().index(self.config_.command.value))
		self.command_combobox.grid(row=1, column=1, sticky=EW)
		Label(frame, text='Comment:', anchor=E).grid(row=2, column=0, sticky=EW)
		self.comment_combobox = Combobox(frame, state=READONLY, values=[format.label for format in CommentFormat.all()])
		self.comment_combobox.current(CommentFormat.all().index(self.config_.comment.value))
		self.comment_combobox.grid(row=2, column=1, sticky=EW)
		frame.grid_columnconfigure(0, weight=0)
		frame.grid_columnconfigure(1, weight=1)
		frame.pack(pady=3, padx=3, fill=X)

		Label(self, text='Note: Code can be parsed in any of the above formats.\nThis just controls your preferred default format when decompiling.').pack(pady=10, padx=3, fill=X)

		buttons = Frame(self)
		ok = Button(buttons, text='Ok', width=10, command=self.ok)
		ok.pack(side=LEFT, padx=(1, 10), pady=3)
		Button(buttons, text='Cancel', width=10, command=self.cancel).pack(side=LEFT, padx=(10, 1), pady=3)
		buttons.pack(side=BOTTOM, pady=3, padx=3)

		return ok

	def ok(self, event: Event | None = None) -> None:
		self.config_.block.value = BlockFormat.all()[self.block_combobox.current()]
		self.config_.command.value = CommandFormat.all()[self.command_combobox.current()]
		self.config_.comment.value = CommentFormat.all()[self.comment_combobox.current()]
		PyMSDialog.ok(self)
