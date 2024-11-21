
from __future__ import annotations

from ..Utilities.UIKit import *
from ..Utilities.PyMSDialog import PyMSDialog
from ..Utilities import Config
from ..Utilities.PyMSError import PyMSError
from ..Utilities.ErrorDialog import ErrorDialog

import os

class NameDialog(PyMSDialog):
	def __init__(self, parent: Misc, parent_path: str, window_geometry_config: Config.WindowGeometry):
		self.parent_path = parent_path
		self.window_geometry_config = window_geometry_config
		self.name_var = StringVar(value='')
		self.name: str | None = None
		PyMSDialog.__init__(self, parent, 'Project Name', grabwait=True, resizable=(True,False))

	def widgetize(self) -> Misc | None:
		Label(self, text='Name:', width=30, anchor=W).pack(side=TOP, fill=X, padx=3)
		entry = Entry(self, textvariable=self.name_var)
		entry.pack(side=TOP, fill=X, padx=3)

		buts = Frame(self)
		done = Button(buts, text='Save', command=self.ok)
		done.pack(side=LEFT)
		Button(buts, text='Cancel', command=self.cancel).pack(side=RIGHT)
		buts.pack(side=BOTTOM, fill=X, padx=3, pady=(0,3))

		return entry

	def setup_complete(self) -> None:
		self.window_geometry_config.load_size(self)

	def ok(self, event: Event | None = None) -> None:
		project_path = os.path.join(self.parent_path, self.name_var.get())
		if os.path.exists(project_path):
			ErrorDialog(self, PyMSError('New', f"Couldn't create project, `{project_path}` already exists"))
			return
		self.name = self.name_var.get()
		PyMSDialog.ok(self)

	def dismiss(self) -> None:
		self.window_geometry_config.save_size(self)
		PyMSDialog.dismiss(self)
