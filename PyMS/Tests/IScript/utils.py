
from ...FileFormats.IScriptBIN.CodeHandlers import ICEParseContext, ICELexer, DataContext, ICESerializeContext

from ...Utilities.CodeHandlers.Formatters import Formatters

import io

def parse_context(code: str, data_context: DataContext | None = None) -> ICEParseContext:
	lexer = ICELexer(code)
	if data_context is None:
		data_context = DataContext()
	return ICEParseContext(lexer, data_context)

def serialize_context(data_context: DataContext | None = None) -> tuple[io.StringIO, ICESerializeContext]:
	output = io.StringIO()
	if data_context is None:
		data_context = DataContext()
	return (output, ICESerializeContext(output, data_context))
