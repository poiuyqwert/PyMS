from __future__ import annotations

from .AbstractReqGraft import AbstractReqGraft
from ...Utilities.DataContext import DataContext
from .CodeHandlers.GraftLanguage import UnitRequirementsLanguage

class UnitsGraft(AbstractReqGraft):
	FILE_NAME = 'Units.graft'
	MPQ_PATH = 'datreq\\Units.graft'
	LANGUAGE = UnitRequirementsLanguage

	@staticmethod
	def entry_name(data_context: DataContext, entry_id: int) -> str | None:
		return data_context.unit_display_name(entry_id)
