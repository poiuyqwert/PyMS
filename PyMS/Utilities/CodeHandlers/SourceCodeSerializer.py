
from __future__ import annotations

from .CodeHeader import CodeHeader

from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from .SerializeContext import SerializeContext
	from .DecompileStrategy import DecompileStrategy

class SourceCodeSerializer:
	def decompile(self, serialize_context: SerializeContext, decompile_strategy: DecompileStrategy) -> None:
		serialize_context.strategy = decompile_strategy
		for item in serialize_context.strategy.items:
			if isinstance(item, CodeHeader):
				item.serialize(serialize_context)
			else:
				item.serialize(serialize_context)
