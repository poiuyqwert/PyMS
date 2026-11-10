from __future__ import annotations

from ....Utilities.CodeHandlers.CodeCommand import CodeCommandDefinition
from ....Utilities.CodeHandlers.CodeType import CodeType

class GraftCommandDefinition(CodeCommandDefinition):
	# A game function, stored in Buttons.graft as its index in its list of functions, with the function's parameter (if it uses one)
	def __init__(self, name: str, display_name: str, help_text: str, param_type: CodeType | None = None) -> None:
		super().__init__(name, help_text, None, () if param_type is None else (param_type,))
		self.display_name = display_name # Readable name
		self.function_index = -1 # Index stored in Buttons.graft, set by `number_functions`

def number_functions(functions: list[GraftCommandDefinition]) -> list[GraftCommandDefinition]:
	# Sets each function's index to its position in its list
	for index, function in enumerate(functions):
		function.function_index = index
	return functions
