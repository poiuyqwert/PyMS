
from ..FileFormats.AIBIN.AIFlag import AIFlag

from ..Utilities.UIKit import *
from ..Utilities.PyMSDialog import PyMSDialog

class FlagEditor(PyMSDialog):
	def __init__(self, parent: AnyWindow, flags: int) -> None:
		self.flags = flags
		self.location = BooleanVar(value=not not flags & AIFlag.requires_location)
		self.visible = BooleanVar(value=not not flags & AIFlag.staredit_hidden)
		self.bwonly = BooleanVar(value=not not flags & AIFlag.broodwar_only)
		PyMSDialog.__init__(self, parent, 'Flag Editor', resizable=(False, False))

	def widgetize(self) -> Widget:
		choices = Frame(self)
		Checkbutton(choices, text='Requires a Location', variable=self.location).grid(sticky=W)
		Checkbutton(choices, text='Invisible in StarEdit', variable=self.visible).grid(sticky=W)
		Checkbutton(choices, text='BroodWar Only', variable=self.bwonly).grid(sticky=W)
		choices.pack(pady=3, padx=3)
		buttons = Frame(self)
		ok = Button(buttons, text='Ok', width=10, command=self.ok)
		ok.pack(side=LEFT, padx=1, pady=3)
		Button(buttons, text='Cancel', width=10, command=self.cancel).pack(side=LEFT, padx=1, pady=3)
		buttons.pack(pady=3, padx=3)
		return ok

	def ok(self, event: Event | None = None) -> None:
		self.flags = AIFlag.flags(self.location.get(), self.visible.get(), self.bwonly.get())
		PyMSDialog.ok(self)
