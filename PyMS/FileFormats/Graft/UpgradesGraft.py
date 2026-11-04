from __future__ import annotations

from .AbstractReqGraft import AbstractReqGraft
from .CodeHandlers.DataContext import DataContext
from .CodeHandlers.GraftLanguage import OtherRequirementsLanguage

class UpgradesGraft(AbstractReqGraft):
	FILE_NAME = 'Upgrades.graft'
	MPQ_PATH = 'datreq\\Upgrades.graft'
	DESCRIPTION = 'Upgrade Requirements'
	HEADER_KEYWORD = 'Upgrade'
	LANGUAGE = OtherRequirementsLanguage

	@staticmethod
	def entry_name(data_context: DataContext, entry_id: int) -> str | None:
		return data_context.upgrade_name(entry_id)
