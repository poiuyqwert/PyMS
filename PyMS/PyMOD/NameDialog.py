
from __future__ import annotations

from ..Utilities import UIKit as UI
from ..Utilities.PyMSDialog import PyMSDialog
from ..Utilities import Config
from ..Utilities.PyMSError import PyMSError
from ..Utilities.ErrorDialog import ErrorDialog

import os

class NameDialog(PyMSDialog):
	def __init__(self, parent: UI.Misc, parent_path: str, window_geometry_config: Config.WindowGeometry):
		self.parent_path = parent_path
		self.window_geometry_config = window_geometry_config
		self.name_var = UI.StringVar(value='')
		self.name: str | None = None
		PyMSDialog.__init__(self, parent, 'Project Name', grabwait=True, resizable=(True,False))

	def widgetize(self) -> UI.Misc | None:
		UI.Label(self, text='Name:', width=30, anchor=UI.W).pack(side=UI.TOP, fill=UI.X, padx=3)
		entry = UI.Entry(self, textvariable=self.name_var)
		entry.pack(side=UI.TOP, fill=UI.X, padx=3)

		buts = UI.Frame(self)
		done = UI.Button(buts, text='Save', command=self.ok)
		done.pack(side=UI.LEFT)
		UI.Button(buts, text='Cancel', command=self.cancel).pack(side=UI.RIGHT)
		buts.pack(side=UI.BOTTOM, fill=UI.X, padx=3, pady=(0,3))

		return entry

	def setup_complete(self) -> None:
		self.window_geometry_config.load_size(self)

	def ok(self, _event: UI.Event | None = None) -> None:
		project_path = os.path.join(self.parent_path, self.name_var.get())
		if os.path.exists(project_path):
			ErrorDialog(self, PyMSError('New', f"Couldn't create project, `{project_path}` already exists"))
			return
		self.name = self.name_var.get()
		PyMSDialog.ok(self)

	def dismiss(self) -> None:
		self.window_geometry_config.save_size(self)
		PyMSDialog.dismiss(self)
