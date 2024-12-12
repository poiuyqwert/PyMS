
from __future__ import annotations

from . import Tokens

from typing import TYPE_CHECKING, Any
if TYPE_CHECKING:
	from .CodeType import CodeType

class Variable(object):
	def __init__(self, name: str, value: Any, type: CodeType) -> None:
		self.name = name
		self.value = value
		self.type = type

class DefinitionsHandler(object):
	class SymbolToken(Tokens.LiteralsToken):
		_literals = ('=', '@', '(', ')')

	def __init__(self) -> None:
		self.variables: dict[str, Variable] = {}

	def set_variable(self, name: str, value: Any, type: CodeType) -> None:
		self.variables[name] = Variable(name, value, type)

	def get_variable(self, name: str) -> (Variable | None):
		return self.variables.get(name, None)

	def lookup_variable(self, value: Any, type: CodeType) -> (Variable | None):
		matching_variable: Variable | None = None
		matching_priority: int = 0
		for variable in self.variables.values():
			if variable.value == value and (priority := type.compatible(variable.type)) and priority > matching_priority:
				matching_variable = variable
				matching_priority = priority
		return matching_variable
