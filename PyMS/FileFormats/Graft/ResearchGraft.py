from __future__ import annotations

from .AbstractReqGraft import AbstractReqGraft
from ...Utilities.DataContext import DataContext
from .CodeHandlers.GraftLanguage import ResearchRequirementsLanguage

# Requirements to research a tech (`TechGraft` is the requirements to use a tech)
class ResearchGraft(AbstractReqGraft):
	FILE_NAME = 'Research.graft'
	MPQ_PATH = 'datreq\\Research.graft'
	LANGUAGE = ResearchRequirementsLanguage

	@staticmethod
	def entry_name(data_context: DataContext, entry_id: int) -> str | None:
		return data_context.tech_display_name(entry_id)
