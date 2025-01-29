
from __future__ import annotations

from . import Tokens

from typing import TYPE_CHECKING, Any
if TYPE_CHECKING:
	from .CodeType import CodeType

class Variable:
	def __init__(self, name: str, value: Any, code_type: CodeType) -> None:
		self.name = name
		self.value = value
		self.type = code_type

class DefinitionsHandler:
	class SymbolToken(Tokens.LiteralsToken):
		_literals = ('=', '@', '(', ')')

	def __init__(self) -> None:
		self.variables: dict[str, Variable] = {}

	def set_variable(self, name: str, value: Any, code_type: CodeType) -> None:
		self.variables[name] = Variable(name, value, code_type)

	def get_variable(self, name: str) -> (Variable | None):
		return self.variables.get(name, None)

	def lookup_variable(self, value: Any, code_type: CodeType) -> (Variable | None):
		matching_variable: Variable | None = None
		matching_priority: int = 0
		for variable in self.variables.values():
			if variable.value == value and (priority := code_type.compatible(variable.type)) and priority > matching_priority:
				matching_variable = variable
				matching_priority = priority
		return matching_variable
