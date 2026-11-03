from __future__ import annotations

from .AbstractReqGraft import AbstractReqGraft
from .Definitions import ParamKind
from .CodeHandlers.GraftLanguage import OtherRequirementsLanguage

class OrdersGraft(AbstractReqGraft):
	FILE_NAME = 'Orders.graft'
	MPQ_PATH = 'datreq\\Orders.graft'
	DESCRIPTION = 'Order Requirements'
	HEADER_KEYWORD = 'Order'
	ID_KIND = ParamKind.order
	LANGUAGE = OtherRequirementsLanguage
