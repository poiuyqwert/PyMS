from __future__ import annotations

from .DataContext import DataContext

from ....Utilities.CodeHandlers.SerializeContext import SerializeContext
from ....Utilities.CodeHandlers import Formatters

from typing import IO

class GraftSerializeContext(SerializeContext):
	def __init__(self, output: IO[str], data_context: DataContext | None = None) -> None:
		formatters = Formatters.Formatters(
			indent_bodies=True,
			indent='\t'
		)
		super().__init__(output, formatters=formatters)
		self.data_context = data_context
