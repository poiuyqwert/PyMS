from __future__ import annotations

from .AbstractReqGraft import AbstractReqGraft
from ...Utilities.DataContext import DataContext
from .CodeHandlers.GraftLanguage import TechRequirementsLanguage

# Requirements to use a tech (`ResearchGraft` is the requirements to research a tech)
class TechGraft(AbstractReqGraft):
	FILE_NAME = 'Tech.graft'
	MPQ_PATH = 'datreq\\Tech.graft'
	LANGUAGE = TechRequirementsLanguage

	@staticmethod
	def entry_name(data_context: DataContext, entry_id: int) -> str | None:
		return data_context.tech_display_name(entry_id)
