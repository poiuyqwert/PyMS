
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
	def sort(self) -> Callable[[list[AIBIN.AIScriptHeader], TBL.TBL | None], list[AIBIN.AIScriptHeader]]:
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
	def by_file_order(headers: list[AIBIN.AIScriptHeader], tbl: TBL.TBL | None) -> list[AIBIN.AIScriptHeader]:
		return headers

	@staticmethod
	def by_id(headers: list[AIBIN.AIScriptHeader], tbl: TBL.TBL | None) -> list[AIBIN.AIScriptHeader]:
		return sorted(headers, key=lambda header: header.id)

	@staticmethod
	def by_bw(headers: list[AIBIN.AIScriptHeader], tbl: TBL.TBL | None) -> list[AIBIN.AIScriptHeader]:
		return sorted(headers, key=lambda header: (header.is_in_bw, header.id))

	@staticmethod
	def by_flags(headers: list[AIBIN.AIScriptHeader], tbl: TBL.TBL | None) -> list[AIBIN.AIScriptHeader]:
		return sorted(headers, key=lambda header: (header.flags, header.id))

	@staticmethod
	def by_string(headers: list[AIBIN.AIScriptHeader], tbl: TBL.TBL | None) -> list[AIBIN.AIScriptHeader]:
		return sorted(headers, key=lambda header: (tbl.strings[header.string_id] if tbl else header.string_id, header.id))
