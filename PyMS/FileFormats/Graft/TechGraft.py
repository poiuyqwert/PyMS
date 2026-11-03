from __future__ import annotations

from .AbstractReqGraft import AbstractReqGraft
from .Definitions import ParamKind
from .CodeHandlers.GraftLanguage import OtherRequirementsLanguage

# Requirements to use a tech (`ResearchGraft` is the requirements to research a tech)
class TechGraft(AbstractReqGraft):
	FILE_NAME = 'Tech.graft'
	MPQ_PATH = 'datreq\\Tech.graft'
	DESCRIPTION = 'Tech Use Requirements'
	HEADER_KEYWORD = 'Tech'
	ID_KIND = ParamKind.tech
	LANGUAGE = OtherRequirementsLanguage
