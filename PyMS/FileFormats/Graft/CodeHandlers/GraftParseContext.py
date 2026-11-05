from __future__ import annotations

from .GraftLanguage import GraftLanguage, ButtonsLanguage
from ....Utilities.DataContext import DataContext

from ....Utilities.CodeHandlers.ParseContext import ParseContext, ParseSettings
from ....Utilities.CodeHandlers.Lexer import Lexer

class GraftParseContext(ParseContext[ParseSettings]):
	# `language` is the `LANGUAGE` of the file being compiled (`ButtonsLanguage` when not given)
	def __init__(self, lexer: Lexer, data_context: DataContext | None = None, language: GraftLanguage | None = None) -> None:
		ParseContext.__init__(self, lexer, language if language is not None else ButtonsLanguage(), ParseSettings())
		self.data_context = data_context
