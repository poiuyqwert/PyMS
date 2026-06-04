
from . import CodeGenerator
from ..Config import PyICEConfig

from ...Utilities import UIKit as UI
from ...Utilities import JSON
from ...Utilities.PyMSError import PyMSError
from ...Utilities import Config

import re
from dataclasses import dataclass

from typing import Self, Callable

@dataclass
class CodeGeneratorTypeMath(CodeGenerator.CodeGeneratorType):
	math: str

	@classmethod
	def type_name(cls) -> str:
		return 'math'

	@classmethod
	def from_json(cls, json: JSON.Object) -> Self:
		return cls(JSON.get(json, 'math', str))

	def to_json(self) -> JSON.Object:
		json = CodeGenerator.CodeGeneratorType.to_json(self)
		json['math'] = self.math
		return json

	def count(self) -> int | None:
		return None

	VARIABLE_RE = re.compile(r'\$([a-zA-Z0-9_]+)')
	MATH_RE = re.compile(r'^[0-9.+-/*() \t]+$')
	def value(self, lookup_value: Callable[[str], str]) -> str:
		math = CodeGeneratorTypeMath.VARIABLE_RE.sub(lambda m: lookup_value(m.group(1)), self.math)
		if not CodeGeneratorTypeMath.MATH_RE.match(math):
			raise PyMSError('Generate', f"Invalid math expression '{math}' (only numbers, +, -, /, *, (, ), and whitespace allowed)")
		try:
			return eval(math) # pylint: disable=eval-used
		except Exception as exc:
			raise PyMSError('Generate', f"Error evaluating math expression '{math}'") from exc

	def description(self) -> str:
		return self.math

	def build_editor(self, parent: UI.Misc, config: PyICEConfig) -> CodeGenerator.CodeGeneratorEditor:
		return CodeGeneratorEditorMath(parent, self, config.windows.generator.editor.math)

class CodeGeneratorEditorMath(CodeGenerator.CodeGeneratorEditor[CodeGeneratorTypeMath]):
	def __init__(self, parent: UI.Misc, generator: CodeGeneratorTypeMath, window_geometry_config: Config.WindowGeometry) -> None:
		CodeGenerator.CodeGeneratorEditor.__init__(self, parent, generator, window_geometry_config)

		self.math = UI.StringVar()
		self.math.set(self.generator.math)

		UI.Label(self, text='Math:', anchor=UI.W).pack(side=UI.TOP, fill=UI.X)
		UI.Entry(self, textvariable=self.math).pack(side=UI.TOP, fill=UI.X)

	def save(self) -> None:
		self.generator.math = self.math.get()

	def is_resizable(self) -> tuple[bool, bool]:
		return (True, False)

CodeGenerator.register_type(CodeGeneratorTypeMath)
