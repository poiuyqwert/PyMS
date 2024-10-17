
from __future__ import annotations

from .DataContext import DataContext

from ....Utilities.CodeHandlers.ParseContext import ParseContext
from ....Utilities.CodeHandlers.Lexer import Lexer

from collections import OrderedDict

from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from ..IScript import IScript

class ICEParseContext(ParseContext):
	def __init__(self, lexer: Lexer, data_context: DataContext) -> None:
		ParseContext.__init__(self, lexer)
		self.data_context = data_context
		self.scripts: OrderedDict[int, tuple[IScript, int]] = OrderedDict()
