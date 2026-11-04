from __future__ import annotations

from .AbstractReqGraft import AbstractReqGraft
from .CodeHandlers.DataContext import DataContext
from .CodeHandlers.GraftLanguage import OtherRequirementsLanguage

class OrdersGraft(AbstractReqGraft):
	FILE_NAME = 'Orders.graft'
	MPQ_PATH = 'datreq\\Orders.graft'
	DESCRIPTION = 'Order Requirements'
	HEADER_KEYWORD = 'Order'
	LANGUAGE = OtherRequirementsLanguage

	@staticmethod
	def entry_name(data_context: DataContext, entry_id: int) -> str | None:
		return data_context.order_name(entry_id)
