
from . import CodeGenerator
from ..Config import PyICEConfig
from ..Delegates import VariableEditorDelegate

from ...Utilities.UIKit import *
from ...Utilities.PyMSDialog import PyMSDialog
from ...Utilities import JSON

import re
from dataclasses import dataclass

from typing import Self

@dataclass
class CodeGeneratorVariable(JSON.Codable):
	name: str
	generator: CodeGenerator.CodeGeneratorType

	@classmethod
	def from_json(cls, json: JSON.Object) -> Self:
		return cls(
			JSON.get(json, 'name', str),
			JSON.get_obj(json, 'generator', CodeGenerator.discriminate_type)
		)

	def to_json(self) -> JSON.Object:
		return {
			'name': self.name,
			'generator': self.generator.to_json()
		}

class CodeGeneratorVariableEditor(PyMSDialog):
	def __init__(self, parent: Misc, delegate: VariableEditorDelegate, variable: CodeGeneratorVariable, config: PyICEConfig):
		self.delegate = delegate
		self.variable = variable
		self.config_ = config
		PyMSDialog.__init__(self, parent, 'Variable Editor', grabwait=True)

	def widgetize(self) -> Widget:
		self.name = StringVar()
		self.name.set(self.variable.name)
		def strip_name(*_) -> None:
			strip_re = re.compile(r'[^a-zA-Z0-9_]')
			name = self.name.get()
			stripped = strip_re.sub('', name)
			if stripped != name:
				self.name.set(stripped)
		self.name.trace('w', strip_name)

		Label(self, text='Name:', anchor=W).pack(side=TOP, fill=X, padx=3)
		Entry(self, textvariable=self.name).pack(side=TOP, fill=X, padx=3)

		self.editor = self.variable.generator.build_editor(self, self.config_)
		self.editor.pack(side=TOP, fill=BOTH, expand=1, padx=3, pady=3)

		buts = Frame(self)
		done = Button(buts, text='Done', command=self.ok)
		done.pack(side=LEFT)
		Button(buts, text='Cancel', command=self.cancel).pack(side=RIGHT)
		buts.pack(side=BOTTOM, fill=X, padx=3, pady=(0,3))

		return done

	def setup_complete(self) -> None:
		self.set_resizable(*self.editor.is_resizable())
		self.editor.window_geometry_config.load_size(self)

	def ok(self, event: Event | None = None) -> None:
		self.variable.name = self.delegate.unique_name(self.name.get(), self.variable)
		self.editor.save()
		self.delegate.update_list()
		PyMSDialog.ok(self)

	def dismiss(self) -> None:
		self.editor.window_geometry_config.save_size(self)
		PyMSDialog.dismiss(self)
