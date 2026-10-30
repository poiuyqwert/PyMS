
from ..FileFormats.AIBIN.AIFlag import AIFlag

from ..Utilities import UIKit as UI
from ..Utilities.PyMSDialog import PyMSDialog

class FlagEditor(PyMSDialog):
	def __init__(self, parent: UI.AnyWindow, flags: int) -> None:
		self.flags = flags
		self.location = UI.BooleanVar(value=not not flags & AIFlag.requires_location)
		self.visible = UI.BooleanVar(value=not not flags & AIFlag.staredit_hidden)
		self.bwonly = UI.BooleanVar(value=not not flags & AIFlag.broodwar_only)
		PyMSDialog.__init__(self, parent, 'Flag Editor', resizable=(False, False))

	def widgetize(self) -> UI.Widget:
		choices = UI.Frame(self)
		UI.Checkbutton(choices, text='Requires a Location', variable=self.location).grid(sticky=UI.W)
		UI.Checkbutton(choices, text='Invisible in StarEdit', variable=self.visible).grid(sticky=UI.W)
		UI.Checkbutton(choices, text='BroodWar Only', variable=self.bwonly).grid(sticky=UI.W)
		choices.pack(pady=3, padx=3)
		buttons = UI.Frame(self)
		ok = UI.Button(buttons, text='Ok', width=10, command=self.ok)
		ok.pack(side=UI.LEFT, padx=1, pady=3)
		UI.Button(buttons, text='Cancel', width=10, command=self.cancel).pack(side=UI.LEFT, padx=1, pady=3)
		buttons.pack(pady=3, padx=3)
		return ok

	def ok(self, _event: UI.Event | None = None) -> None:
		self.flags = AIFlag.flags(self.location.get(), self.visible.get(), self.bwonly.get())
		PyMSDialog.ok(self)
