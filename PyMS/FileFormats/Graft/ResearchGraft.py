from __future__ import annotations

from .AbstractReqGraft import AbstractReqGraft
from .Definitions import ParamKind
from .CodeHandlers.GraftLanguage import OtherRequirementsLanguage

# Requirements to research a tech (`TechGraft` is the requirements to use a tech)
class ResearchGraft(AbstractReqGraft):
	FILE_NAME = 'Research.graft'
	MPQ_PATH = 'datreq\\Research.graft'
	DESCRIPTION = 'Tech Research Requirements'
	HEADER_KEYWORD = 'Research'
	ID_KIND = ParamKind.tech
	LANGUAGE = OtherRequirementsLanguage
