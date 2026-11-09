from __future__ import annotations

from .AbstractReqGraft import AbstractReqGraft
from ...Utilities.DataContext import DataContext
from .CodeHandlers.GraftLanguage import OrderRequirementsLanguage

class OrdersGraft(AbstractReqGraft):
	FILE_NAME = 'Orders.graft'
	MPQ_PATH = 'datreq\\Orders.graft'
	LANGUAGE = OrderRequirementsLanguage

	@staticmethod
	def entry_name(data_context: DataContext, entry_id: int) -> str | None:
		return data_context.order_display_name(entry_id)
