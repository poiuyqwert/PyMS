from __future__ import annotations

from .AbstractReqGraft import AbstractReqGraft
from .Definitions import ParamKind
from .CodeHandlers.GraftLanguage import OtherRequirementsLanguage

class UpgradesGraft(AbstractReqGraft):
	FILE_NAME = 'Upgrades.graft'
	MPQ_PATH = 'datreq\\Upgrades.graft'
	DESCRIPTION = 'Upgrade Requirements'
	HEADER_KEYWORD = 'Upgrade'
	ID_KIND = ParamKind.upgrade
	LANGUAGE = OtherRequirementsLanguage
