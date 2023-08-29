
from __future__ import annotations

from ..FileFormats.TBL import TBL, decompile_string, compile_string

from ..Utilities.Callback import Callback

from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from .DataContext import DataContext
	from .DataID import DataID

class TBLData(object):
	def __init__(self, data_context, data_id, setting, path): # type: (DataContext, DataID, str, str) -> None
		self.data_context = data_context
		self.data_id = data_id
		self.setting = setting
		self.path = path
		self.strings = () # type: tuple[str, ...]

		self.update_cb: Callback[DataID] = Callback()

	def load_strings(self): # type: () -> None
		path = self.data_context.settings.settings.files.get(self.setting, 'MPQ:' + self.path)
		file = self.data_context.mpqhandler.get_file(path)
		if file:
			tbl = TBL()
			tbl.load_file(file)
			self.strings = tuple(decompile_string(string) for string in tbl.strings)
		else:
			self.strings = ()
		self.update_cb(self.data_id)

	def save_data(self): # type: () -> bytes
		tbl = TBL()
		tbl.strings = [compile_string(string) for string in self.strings]
		return tbl.save_data()
