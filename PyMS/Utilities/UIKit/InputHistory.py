
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from .. import Config

__all__ = [
	'InputHistory'
]

class InputHistory:
	def __init__(self, limit: int = 10, config: Config.List[str] | None = None) -> None:
		self.limit = limit
		self._config = config
		self._entries: list[str] = []

	@property
	def entries(self) -> list[str]:
		# Config-backed history must read through to the live list, since
		# `Config.List` rebinds `.data` on decode/reset/restore_state
		if self._config is not None:
			return self._config.data
		return self._entries

	def record(self, entry: str) -> None:
		if not entry:
			return
		entries = self.entries
		if entry in entries:
			entries.remove(entry)
		entries.insert(0, entry)
		del entries[self.limit:]
