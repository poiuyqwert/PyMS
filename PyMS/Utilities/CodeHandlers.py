
from . import Struct
from .PyMSError import PyMSError

class Scanner(object):
	def __init__(self, data, address=0): # type: (bytes, int) -> Scanner
		self.data = data
		self.address = 0

	def scan(self, type): # type: (str) -> Any
		result = Struct.Value.unpack(self.data, type, self.address)
		self.address += Struct.Type.size(type)
		return result

	def clone(self, address=None): # type: (int | None) -> Scanner
		if address == None:
			address = self.address
		return Scanner(self.data, address)

	def at_end(self):
		return self.address == len(self.data)

class SerializeContext(object):
	def __init__(self, label_prefix):
		self._label_prefix = label_prefix
		self._block_labels = {} # type: dict[CodeBlock, str]
		self._blocks_serialized = set()

	def block_label(self, block): # type: (CodeBlock) -> str
		if not block in self._block_labels:
			self._block_labels[block] = '%s_%04d' % (self._label_prefix, len(self._block_labels))
		return self._block_labels[block]

	def is_block_serialized(self, block): # type: (CodeBlock) -> bool
		return block in self._blocks_serialized

	def mark_block_serialized(self, block): # type: (CodeBlock) -> None
		self._blocks_serialized.add(block)

class CodeBlock(object):
	def __init__(self):
		self.commands = [] # type: list[CodeCommand]
		self.prev_block = None # type: CodeBlock
		self.next_block = None # type: CodeBlock

	def serialize(self, context): # type: (SerializeContext) -> str
		result = ':' + context.block_label(self)
		for cmd in self.commands:
			if len(result):
				result += '\n'
			result += cmd.serialize(context)
			if cmd._separate or cmd._ends_flow:
				result += '\n'
			for param in cmd.params:
				if isinstance(param, CodeBlock) and not context.is_block_serialized(param):
					context.mark_block_serialized(param)
					result = param.serialize(context) + '\n\n' + result
		if self.next_block and not context.is_block_serialized(self.next_block):
			context.mark_block_serialized(self.next_block)
			result += '\n\n' + self.next_block.serialize(context)
		return result

class ByteCodeHandler(object):
	def __init__(self, data): # type: (bytes) -> ByteCodeHandler
		self.data = data
		self.cmd_defs = {} # type: dict[type, Type[CodeCommand]]
		self.block_refs = {} # type: dict[int, CodeBlock]
		self.cmd_refs = {} # type: dict[int, tuple[CodeBlock, CodeCommand]]

	def register_command(self, cmd_def): # type: (Type[CodeCommand]) -> None
		self.cmd_defs[cmd_def._id] = cmd_def

	def decompile_block(self, address): # type: (int) -> CodeBlock
		if address in self.block_refs:
			return self.block_refs[address]
		elif address in self.cmd_refs:
			block = CodeBlock()
			self.block_refs[address] = block
			prev_block, start_cmd = self.cmd_refs[address]
			index = prev_block.commands.index(start_cmd)
			while index < len(prev_block.commands):
				cmd = prev_block.commands.pop(index)
				self.cmd_refs[cmd.original_address] = (block, cmd)
				block.commands.append(cmd)
			block.prev_block = prev_block
			prev_block.next_block = block
			return block
		else:
			scanner = Scanner(self.data, address)
			block = CodeBlock()
			self.block_refs[address] = block
			while not scanner.at_end():
				cmd_address = scanner.address
				cmd_id = scanner.scan(Struct.Type.u8())
				cmd_def = self.cmd_defs.get(cmd_id)
				if not cmd_def:
					raise PyMSError('Byte Code', "Invalid command id '%d'" % cmd_id)
				cmd = cmd_def.decompile(scanner)
				cmd.original_address = cmd_address
				block.commands.append(cmd)
				self.cmd_refs[cmd_address] = (block, cmd)
				for n,param_type in enumerate(cmd._param_types):
					if param_type._block_reference:
						cmd.params[n] = self.decompile_block(cmd.params[n])
				if cmd._ends_flow:
					break
				if scanner.address in self.block_refs:
					block.next_block = self.block_refs[scanner.address]
					block.next_block.prev_block = block
					break
			return block

class SourceCodeHandler(object):
	pass

class Lexer(object):
	pass

class CodeCommand(object):
	_id = None # type: int
	_name = None # type: str
	_param_types = [] # type: list[Type[CodeType]]
	_ends_flow = False
	_separate = False

	def __init__(self, params): # type: (list[CodeType], int | None) -> None
		self.params = params
		self.original_address = None

	@classmethod
	def decompile(cls, scanner): # type: (Scanner) -> Self
		params = []
		for param_type in list(cls._param_types): # TODO: Why do we need to wrap in `list(...)`?
			params.append(param_type.decompile(scanner))
		return cls(params)

	def compile(self): # type: () -> bytes
		data = Struct.Value.pack(self._id, Struct.Type.u8())
		for param,param_type in zip(self.params, self._param_types):
			data += param_type.compile(param)
		return data

	def serialize(self, context): # type: (SerializeContext) -> str
		result = self._name
		for param,param_type in zip(self.params, self._param_types):
			result += ' '
			result += param_type.serialize(param, context)
		return result

class CodeType(object):
	_name = None # type: str
	_bytecode_type = None # type: str
	_block_reference = False

	@classmethod
	def decompile(cls, scanner): # type: (Scanner) -> Any
		return scanner.scan(cls._bytecode_type)

	@classmethod
	def compile(cls, value): # type: (Any) -> bytes
		return Struct.Value.pack(value, cls._bytecode_type)

	@classmethod
	def serialize(cls, value, context): # type: (Any, SerializeContext) -> str
		return str(value)

	@classmethod
	def parse(cls, token): # type: (str) -> Any
		raise NotImplementedError(cls.__name__ + '.parse()')

class IntCodeType(CodeType):
	@classmethod
	def parse(cls, token): # type: (str) -> Any
		try:
			num = int(token)
		except:
			raise PyMSError('Parse', "Invalid value '%s' for '%s'" % (token, cls._name))
		min,max = Struct.Type.numeric_limits(cls._bytecode_type)
		if num < min:
			raise PyMSError('Parse', "Value is too small for '%s' (got '%d', minimum is '%d')" % (cls._name, num, min))
		if num > max:
			raise PyMSError('Parse', "Value is too large for '%s' (got '%d', maximum is '%d')" % (cls._name, num, max))
		return num

class FloatCodeType(CodeType):
	@classmethod
	def parse(cls, token): # type: (str) -> Any
		try:
			num = float(token)
		except:
			raise PyMSError('Parse', "Invalid value '%s' for '%s'" % (token, cls._name))
		min,max = Struct.Type.numeric_limits(cls._bytecode_type)
		if num < min:
			raise PyMSError('Parse', "Value is too small for '%s' (got '%f', minimum is '%f')" % (cls._name, num, min))
		if num > max:
			raise PyMSError('Parse', "Value is too large for '%s' (got '%f', maximum is '%f')" % (cls._name, num, max))
		return num

class BlockCodeType(CodeType):
	_block_reference = True

	@classmethod
	def serialize(cls, block, context): # type: (CodeBlock, SerializeContext) -> str
		return context.block_label(block)







class Word(IntCodeType):
	_name = 'word'
	_bytecode_type = Struct.Type.u16()

class BlockReference(BlockCodeType):
	_name = 'block'
	_bytecode_type = Struct.Type.u16()

class Goto(CodeCommand):
	_id = 0
	_name = 'goto'
	_param_types = [BlockReference]
	_ends_flow = True

class Wait(CodeCommand):
	_id = 1
	_name = 'wait'
	_param_types = [Word]
	_separate = True

class StartTown(CodeCommand):
	_id = 2
	_name = 'start_town'

class AIByteCodeHandler(ByteCodeHandler):
	def __init__(self, data):
		ByteCodeHandler.__init__(self, data)
		self.register_command(Goto)
		self.register_command(Wait)
		self.register_command(StartTown)
