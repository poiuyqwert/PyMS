
from __future__ import annotations

from . import Tokens
from .CodeType import CodeType, AddressCodeType, CodeBlock
from .ParseContext import ParseContext, CommandParamBlockReferenceResolver

from .. import Struct
from ..PyMSError import PyMSError
from ..BytesScanner import BytesScanner

from typing import TYPE_CHECKING, Sequence, Any
if TYPE_CHECKING:
	from .SerializeContext import SerializeContext
	from .Lexer import Lexer

class CodeCommandDefinition(object):
	def __init__(self, name: str, byte_code_id: int | None, param_types: Sequence[CodeType] = (), *, ends_flow: bool = False, separate: bool = False, ephemeral: bool = False) -> None:
		self.name = name
		self.byte_code_id = byte_code_id
		self.param_types = param_types
		self.ends_flow = ends_flow
		self.separate = separate
		self.ephemeral = ephemeral # Command is ephemeral, so will not take part in things like block reference resolving

	def decompile(self, scanner: BytesScanner) -> CodeCommand:
		params = []
		for param_type in self.param_types:
			params.append(param_type.decompile(scanner))
		return CodeCommand(self, params)

	def parse(self, lexer: Lexer, parse_context: ParseContext) -> CodeCommand:
		# TODO: Support braces
		parens = False
		params: list[Any] = []
		token = lexer.next_token(peek=True)
		if isinstance(token, Tokens.LiteralsToken) and token.raw_value == '(':
			_ = lexer.next_token()
			parens = True
		missing_blocks: list[tuple[str, int, int | None]] = []
		for param_index,param_type in enumerate(self.param_types):
			if param_index > 0:
				token = lexer.next_token()
				if not isinstance(token, Tokens.LiteralsToken) or token.raw_value != ',':
					raise PyMSError('Parse', f"Unexpected token '{token.raw_value}' (expected `,` separating parameters)")
			token = lexer.next_token(peek=True)
			value: Any | None = None
			if isinstance(token, Tokens.IdentifierToken) and parse_context.definitions:
				variable = parse_context.definitions.get_variable(token.raw_value)
				if variable and param_type.accepts(variable.type):
					value = variable.value
					_ = lexer.next_token()
			if value is None:
				value = param_type.lex(lexer, parse_context)
			if isinstance(param_type, AddressCodeType):
				block = parse_context.lookup_block(value)
				if not block:
					missing_blocks.append((value, param_index, lexer.line))
				else:
					value = block
			params.append(value)
		if parens:
			token = lexer.next_token()
			if not isinstance(token, Tokens.LiteralsToken) or token.raw_value != ')':
				raise PyMSError('Parse', f"Unexpected token '{token.raw_value}' (expected `)` to end parameters)")
		token = lexer.next_token()
		if not isinstance(token, (Tokens.NewlineToken, Tokens.EOFToken)):
			raise PyMSError('Parse', "Unexpected token '%s' (expected end of line or file)" % token.raw_value, line=lexer.line)
		cmd = CodeCommand(self, params)
		if not self.ephemeral:
			for block_name,param_index,source_line in missing_blocks:
				parse_context.missing_block(block_name, CommandParamBlockReferenceResolver(cmd, param_index, source_line))
		return cmd

class CodeCommand(object):
	def __init__(self, definition: CodeCommandDefinition, params: list[Any], originl_address: int | None = None) -> None:
		self.definition = definition
		self.params = params
		self.original_address = originl_address

	def compile(self) -> bytes:
		assert self.definition.byte_code_id is not None
		data = Struct.l_u8.pack(self.definition.byte_code_id)
		for param,param_type in zip(self.params, self.definition.param_types):
			data += param_type.compile(param)
		return data

	def serialize(self, context: SerializeContext) -> str:
		parameters: list[str] = []
		comments: list[str] = []
		for param,param_type in zip(self.params, self.definition.param_types):
			parameters.append(param_type.serialize(param, context))
			comment = param_type.comment(param, context)
			if comment is not None:
				comments.append(comment)
			if isinstance(param, CodeBlock):
				context.add_next_block(param)
		result = context.formatters.command.serialize(self.definition.name, parameters)
		if comments:
			result += f' {context.formatters.comment.serialize(comments)}'
		return result
