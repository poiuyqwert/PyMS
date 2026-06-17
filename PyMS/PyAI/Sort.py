
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
	def by_file_order(headers: list[AIBIN.AIScript], _tbl: TBL.TBL | None) -> list[AIBIN.AIScript]:
		return headers

	@staticmethod
	def by_id(headers: list[AIBIN.AIScript], _tbl: TBL.TBL | None) -> list[AIBIN.AIScript]:
		return sorted(headers, key=lambda header: header.id)

	@staticmethod
	def by_bw(headers: list[AIBIN.AIScript], _tbl: TBL.TBL | None) -> list[AIBIN.AIScript]:
		return sorted(headers, key=lambda header: (header.in_bwscript, header.id))

	@staticmethod
	def by_flags(headers: list[AIBIN.AIScript], _tbl: TBL.TBL | None) -> list[AIBIN.AIScript]:
		return sorted(headers, key=lambda header: (header.flags, header.id))

	@staticmethod
	def by_string(headers: list[AIBIN.AIScript], tbl: TBL.TBL | None) -> list[AIBIN.AIScript]:
		if tbl is None:
			return sorted(headers, key=lambda header: (header.string_id, header.id))
		# Guard against string IDs outside the TBL's range (corrupt/foreign file, or a
		# different TBL than the one used originally); such scripts sort first.
		def string_key(header: AIBIN.AIScript) -> str:
			if 0 <= header.string_id < len(tbl.strings):
				return tbl.strings[header.string_id]
			return ''
		return sorted(headers, key=lambda header: (string_key(header), header.id))
