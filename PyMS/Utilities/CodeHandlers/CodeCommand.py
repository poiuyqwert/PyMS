
from __future__ import annotations

from . import Tokens
from .CodeType import CodeType, AddressCodeType
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
		# TODO: Support braces?
		params: list[Any] = []
		missing_blocks: list[tuple[str, int, int | None]] = []
		for param_index,param_type in enumerate(self.param_types):
			value = param_type.lex(lexer, parse_context)
			if isinstance(param_type, AddressCodeType):
				block = parse_context.lookup_block(value)
				if not block:
					missing_blocks.append((value, param_index, lexer.line))
				else:
					value = block
			params.append(value)
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
		data = Struct.Value.pack(self.definition.byte_code_id, Struct.FieldType.u8())
		for param,param_type in zip(self.params, self.definition.param_types):
			data += param_type.compile(param)
		return data

	def serialize(self, context: SerializeContext) -> str:
		result = self.definition.name
		for param,param_type in zip(self.params, self.definition.param_types):
			result += ' '
			result += param_type.serialize(param, context)
		return result
