
from __future__ import annotations

from ..Utilities.UIKit import *
from ..Utilities.PyMSDialog import PyMSDialog
from ..Utilities import Config

from typing import Callable

class NameDialog(PyMSDialog):
	def __init__(self, parent: Misc, settings: Settings, title: str = 'Name', value: str = '', done: str = 'Done', callback: Callable[[NameDialog, str], bool] | None = None):
		self.settings = settings
		self.callback = callback
		self.name = StringVar()
		self.name.set(value)
		self.done = done
		PyMSDialog.__init__(self, parent, title, grabwait=True, resizable=(True,False))

	def widgetize(self) -> Misc | None:
		Label(self, text='Name:', width=30, anchor=W).pack(side=TOP, fill=X, padx=3)
		Entry(self, textvariable=self.name).pack(side=TOP, fill=X, padx=3)

		buts = Frame(self)
		done = Button(buts, text=self.done, command=self.ok)
		done.pack(side=LEFT)
		Button(buts, text='Cancel', command=self.cancel).pack(side=RIGHT)
		buts.pack(side=BOTTOM, fill=X, padx=3, pady=(0,3))

		return done

	def setup_complete(self) -> None:
		self.settings.windows.generator.load_window_size('name', self)

	def ok(self, event: Event | None = None) -> None:
		if self.callback and self.callback(self, self.name.get()) == False:
			return
		PyMSDialog.ok(self)

	def dismiss(self) -> None:
		self.settings.windows.generator.save_window_size('name', self)
		PyMSDialog.dismiss(self)
