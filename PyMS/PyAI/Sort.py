
from ..FileFormats.AIBIN import AIBIN
from ..FileFormats import TBL

from enum import Enum

from typing import Callable

class SortBy(Enum):
	file_order = 'file_order'
	id = 'id'
	bw = 'bw'
	flags = 'flags'
	string = 'string'

	@property
	def sort(self) -> Callable[[list[AIBIN.AIScript], TBL.TBL | None], list[AIBIN.AIScript]]:
		match self:
			case SortBy.file_order:
				return Sort.by_file_order
			case SortBy.id:
				return Sort.by_id
			case SortBy.bw:
				return Sort.by_bw
			case SortBy.flags:
				return Sort.by_flags
			case SortBy.string:
				return Sort.by_string

class Sort:
	@staticmethod
	def by_file_order(headers: list[AIBIN.AIScript], tbl: TBL.TBL | None) -> list[AIBIN.AIScript]:
		return headers

	@staticmethod
	def by_id(headers: list[AIBIN.AIScript], tbl: TBL.TBL | None) -> list[AIBIN.AIScript]:
		return sorted(headers, key=lambda header: header.id)

	@staticmethod
	def by_bw(headers: list[AIBIN.AIScript], tbl: TBL.TBL | None) -> list[AIBIN.AIScript]:
		return sorted(headers, key=lambda header: (header.in_bwscript, header.id))

	@staticmethod
	def by_flags(headers: list[AIBIN.AIScript], tbl: TBL.TBL | None) -> list[AIBIN.AIScript]:
		return sorted(headers, key=lambda header: (header.flags, header.id))

	@staticmethod
	def by_string(headers: list[AIBIN.AIScript], tbl: TBL.TBL | None) -> list[AIBIN.AIScript]:
		return sorted(headers, key=lambda header: (tbl.strings[header.string_id] if tbl else header.string_id, header.id))
