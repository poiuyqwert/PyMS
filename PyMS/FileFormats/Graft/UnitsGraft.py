from __future__ import annotations

from .AbstractReqGraft import AbstractReqGraft
from .Definitions import ParamKind
from .CodeHandlers.GraftLanguage import UnitRequirementsLanguage

class UnitsGraft(AbstractReqGraft):
	FILE_NAME = 'Units.graft'
	MPQ_PATH = 'datreq\\Units.graft'
	DESCRIPTION = 'Unit Requirements'
	HEADER_KEYWORD = 'Unit'
	ID_KIND = ParamKind.unit
	LANGUAGE = UnitRequirementsLanguage
