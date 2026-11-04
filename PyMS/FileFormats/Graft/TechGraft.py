from __future__ import annotations

from .AbstractReqGraft import AbstractReqGraft
from .CodeHandlers.DataContext import DataContext
from .CodeHandlers.GraftLanguage import OtherRequirementsLanguage

# Requirements to use a tech (`ResearchGraft` is the requirements to research a tech)
class TechGraft(AbstractReqGraft):
	FILE_NAME = 'Tech.graft'
	MPQ_PATH = 'datreq\\Tech.graft'
	DESCRIPTION = 'Tech Use Requirements'
	HEADER_KEYWORD = 'Tech'
	LANGUAGE = OtherRequirementsLanguage

	@staticmethod
	def entry_name(data_context: DataContext, entry_id: int) -> str | None:
		return data_context.tech_name(entry_id)
