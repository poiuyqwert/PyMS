from __future__ import annotations

from .GraftLanguage import GraftLanguage
from ....Utilities.DataContext import DataContext

from ....Utilities.CodeHandlers.ParseContext import ParseContext, ParseSettings
from ....Utilities.CodeHandlers.Lexer import Lexer

class GraftParseContext(ParseContext[ParseSettings]):
	# `language` is the language of the file being compiled
	def __init__(self, lexer: Lexer, data_context: DataContext | None, language: GraftLanguage) -> None:
		ParseContext.__init__(self, lexer, language, ParseSettings())
		self.data_context = data_context
