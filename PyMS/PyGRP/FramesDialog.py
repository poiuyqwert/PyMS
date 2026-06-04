
from ..Utilities.PyMSDialog import PyMSDialog
from ..Utilities import UIKit as UI
from ..Utilities import Config

class FramesDialog(PyMSDialog):
	def __init__(self, parent: UI.Misc, window_geometry_config: Config.WindowGeometry):
		self.window_geometry_config = window_geometry_config
		self.result = UI.IntegerVar(1, [1,None])
		PyMSDialog.__init__(self, parent, 'How many frames?', resizable=(True,False))

	def widgetize(self) -> (UI.Misc | None):
		UI.Label(self, text='How many frames are contained in the BMP?').pack(padx=5, pady=5)
		UI.Entry(self, textvariable=self.result).pack(padx=5, fill=UI.X)

		buttons = UI.Frame(self)
		ok = UI.Button(buttons, text='Ok', width=10, command=self.ok)
		ok.pack(side=UI.LEFT, padx=3, pady=3)
		UI.Button(buttons, text='Cancel', width=10, command=self.cancel).pack(padx=3, pady=3)
		buttons.pack()

		return ok

	def setup_complete(self) -> None:
		self.window_geometry_config.load_size(self)

	def cancel(self, _event: UI.Event | None = None) -> None:
		self.result.set(0)
		PyMSDialog.cancel(self)

	def dismiss(self) -> None:
		self.window_geometry_config.save_size(self)
		PyMSDialog.dismiss(self)
