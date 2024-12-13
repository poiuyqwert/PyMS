
from __future__ import annotations

from . import Tokens
from .CodeType import CodeType, IntCodeType
from .CodeBlock import CodeBlock
from .ParseContext import ParseContext
from .DecompileContext import DecompileContext

from .. import Struct
from ..PyMSError import PyMSError
from ..BytesScanner import BytesScanner

from typing import TYPE_CHECKING, Sequence, Any
if TYPE_CHECKING:
	from .SerializeContext import SerializeContext
	from .ByteCodeCompiler import ByteCodeBuilderType

class CodeCommandDefinition(object):
	@staticmethod
	def find_by_name(name: str, cmd_defs: list[CodeCommandDefinition]) -> CodeCommandDefinition | None:
		for cmd_def in cmd_defs:
			if cmd_def.name == name:
				return cmd_def
		return None

	def __init__(self, name: str, help_text: str, byte_code_id: int | None, param_types: Sequence[CodeType] = (), *, ends_flow: bool = False, separate: bool = False) -> None:
		self.name = name
		self.help_text = help_text
		self.byte_code_id = byte_code_id
		self.param_types = param_types
		self.ends_flow = ends_flow
		self.separate = separate

	def decompile(self, scanner: BytesScanner, context: DecompileContext) -> CodeCommand:
		params = []
		param_repeat = 1
		for param_type in self.param_types:
			for _ in range(param_repeat):
				value = param_type.decompile(scanner, context)
				params.append(value)
			if isinstance(param_type, IntCodeType) and param_type.param_repeater:
				param_repeat = value
			else:
				param_repeat = 1
		return CodeCommand(self, params)

	def parse(self, parse_context: ParseContext) -> CodeCommand:
		parse_context.command_in_parens = False
		params: list[Any] = []
		token = parse_context.lexer.next_token(peek=True)
		if isinstance(token, Tokens.LiteralsToken) and token.raw_value == '(':
			_ = parse_context.lexer.next_token()
			parse_context.command_in_parens = True
		param_repeat = 1
		for param_index,param_type in enumerate(self.param_types):
			for _ in range(param_repeat):
				if parse_context.command_in_parens and param_index > 0:
					token = parse_context.lexer.next_token()
					if not isinstance(token, Tokens.LiteralsToken) or token.raw_value != ',':
						raise parse_context.error('Parse', f"Unexpected token '{token.raw_value}' (expected `,` separating parameters)")
				value: Any = parse_context.lookup_param_value(param_type)
				if value is None:
					try:
						value = param_type.parse(parse_context)
					except PyMSError as e:
						parse_context.attribute_error(e)
						raise e
					except:
						raise
				params.append(value)
			if isinstance(param_type, IntCodeType) and param_type.param_repeater:
				param_repeat = value
			else:
				param_repeat = 1
		if parse_context.command_in_parens:
			token = parse_context.lexer.next_token()
			if not isinstance(token, Tokens.LiteralsToken) or token.raw_value != ')':
				raise parse_context.error('Parse', f"Unexpected token '{token.raw_value}' (expected `)` to end parameters)")
		token = parse_context.lexer.next_token()
		if not isinstance(token, (Tokens.NewlineToken, Tokens.EOFToken)):
			raise parse_context.error('Parse', "Unexpected token '%s' (expected end of line or file)" % token.raw_value)
		return CodeCommand(self, params, parse_context.active_block)

	def full_help_text(self) -> str:
		command = f'{self.name}('
		description = self.help_text
		params_help = ''
		type_counts: dict[str, int] = {}
		for param_type in self.param_types:
			type_counts[param_type.name] = type_counts.get(param_type.name, 0) + 1
		param_counts: dict[str, int] = {}
		for n, param_type in enumerate(self.param_types):
			param_name = param_type.name
			param_counts[param_type.name] = param_counts.get(param_type.name, 0) + 1
			if param_counts[param_name] == 1:
				params_help += f'\n{param_type.name}: {param_type.help_text}'
			if type_counts[param_type.name] > 1:
				param_name += f'({param_counts[param_name]})'
			description = description.replace(f'{{{n + 1}}}', f'`{param_name}`')
			if n:
				command += ', '
			command += param_name
		command += ')'
		help_text = f'{command}\n    {description}'
		if params_help:
			help_text += '\n'
			help_text += params_help
		return help_text

class CodeCommand(object):
	def __init__(self, definition: CodeCommandDefinition, params: list[Any], parent_block: CodeBlock | None = None) -> None:
		self.definition = definition
		self.params = params
		self.parent_block = parent_block
		self.original_location: int | None = None # Byte address or Source line

	def compile(self, context: ByteCodeBuilderType) -> None:
		assert self.definition.byte_code_id is not None
		context.add_data(Struct.l_u8.pack(self.definition.byte_code_id))
		param_repeat = 1
		param_index = 0
		for param_type in self.definition.param_types:
			for _ in range(param_repeat):
				param = self.params[param_index]
				param_type.compile(param, context)
				param_index += 1
			if isinstance(param_type, IntCodeType) and param_type.param_repeater:
				param_repeat = param
			else:
				param_repeat = 1

	def serialize(self, context: SerializeContext) -> None:
		parameters: list[str] = []
		comments: list[str] = []
		param_repeat = 1
		param_index = 0
		for param_type in self.definition.param_types:
			for _ in range(param_repeat):
				param = self.params[param_index]
				parameters.append(param_type.serialize(param, context))
				comment = param_type.comment(param, context)
				if comment is not None:
					comments.append(comment)
				param_index += 1
			if isinstance(param_type, IntCodeType) and param_type.param_repeater:
				param_repeat = param
			else:
				param_repeat = 1
		context.write(context.formatters.command.serialize(self.definition.name, parameters))
		if comments:
			context.write(context.formatters.comment.serialize(comments))
		context.write('\n')
