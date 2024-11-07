
from .CodeBlock import CodeBlock
from .SerializeContext import SerializeContext

from typing import Protocol, runtime_checkable

@runtime_checkable
class CodeHeader(Protocol):
	def get_name(self) -> str:
		...

	def get_entry_points(self) -> list[tuple[CodeBlock, str | None]]:
		...

	def has_entry_point(self, entry_point: CodeBlock) -> bool:
		return entry_point in self.get_entry_points()

	def serialize(self, serialize_context: SerializeContext) -> None:
		...
