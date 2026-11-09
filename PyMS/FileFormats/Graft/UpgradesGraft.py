from __future__ import annotations

from .AbstractReqGraft import AbstractReqGraft
from ...Utilities.DataContext import DataContext
from .CodeHandlers.GraftLanguage import UpgradeRequirementsLanguage

class UpgradesGraft(AbstractReqGraft):
	FILE_NAME = 'Upgrades.graft'
	MPQ_PATH = 'datreq\\Upgrades.graft'
	LANGUAGE = UpgradeRequirementsLanguage

	@staticmethod
	def entry_name(data_context: DataContext, entry_id: int) -> str | None:
		return data_context.upgrade_display_name(entry_id)
