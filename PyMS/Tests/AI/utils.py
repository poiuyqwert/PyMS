
from ...FileFormats.AIBIN.AICodeHandlers.AIParseContext import AIParseContext
from ...FileFormats.AIBIN.AICodeHandlers.AILexer import AILexer
from ...FileFormats.AIBIN.AICodeHandlers.AIDefinitionsHandler import AIDefinitionsHandler
from ...FileFormats.AIBIN.DataContext import DataContext
from ...FileFormats.AIBIN.AICodeHandlers.AISerializeContext import AISerializeContext

from ...Utilities.CodeHandlers.SerializeContext import SerializeContext
from ...Utilities.CodeHandlers.Formatters import Formatters

import io

def parse_context(code: str, definitions_handler: AIDefinitionsHandler | None = None, data_context: DataContext | None = None) -> AIParseContext:
	lexer = AILexer(code)
	if definitions_handler is None:
		definitions_handler = AIDefinitionsHandler()
	if data_context is None:
		data_context = DataContext()
	return AIParseContext(lexer, definitions_handler, data_context)

def serialize_context(definitions_handler: AIDefinitionsHandler | None = None, formatters: Formatters | None = None, data_context: DataContext | None = None) -> tuple[io.StringIO, AISerializeContext]:
	output = io.StringIO()
	if definitions_handler is None:
		definitions_handler = AIDefinitionsHandler()
	if formatters is None:
		formatters = Formatters()
	if data_context is None:
		data_context = DataContext()
	return (output, AISerializeContext(output, definitions_handler, formatters, data_context))