
from .AIFlag import AIFlag
from .CodeHandlers import CodeCommands

from ...Utilities.CodeHandlers.CodeCommand import CodeCommand
from ...Utilities.CodeHandlers.CodeHeader import CodeHeader
from ...Utilities.CodeHandlers.CodeType import CodeBlock

from dataclasses import dataclass

@dataclass
class AIScript(CodeHeader):
	id: str
	flags: int
	string_id: int
	entry_point: CodeBlock
	in_bwscript: bool

	@staticmethod
	def blank_entry_point() -> CodeBlock:
		entry_point = CodeBlock()
		entry_point.add_command(CodeCommand(CodeCommands.Stop, []))
		return entry_point

	def get_name(self) -> str:
		return self.id

	def get_entry_points(self) -> list[tuple[CodeBlock, str | None]]:
		return [(self.entry_point, 'EntryPoint')]

	def serialize(self, serialize_context: CodeCommands.SerializeContext) -> None:
		serialize_context.write(f'\nscript {self.id} {{\n')
		serialize_context.indent()
		CodeCommand(CodeCommands.HeaderNameString, [self.string_id]).serialize(serialize_context)
		CodeCommand(CodeCommands.HeaderBinFile, [self.in_bwscript]).serialize(serialize_context)
		CodeCommand(CodeCommands.BroodwarOnly, [1 if self.flags & AIFlag.broodwar_only else 0]).serialize(serialize_context)
		CodeCommand(CodeCommands.StarEditHidden, [1 if self.flags & AIFlag.staredit_hidden else 0]).serialize(serialize_context)
		CodeCommand(CodeCommands.RequiresLocation, [1 if self.flags & AIFlag.requires_location else 0]).serialize(serialize_context)
		CodeCommand(CodeCommands.EntryPoint, [self.entry_point]).serialize(serialize_context)
		serialize_context.dedent()
		serialize_context.write('}\n')
