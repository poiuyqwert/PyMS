
from ..FileFormats.TBL import TBL, decompile_string

from ..Utilities.Callback import Callback

def convert_string(string):
	string = decompile_string(string)
	if string.endswith('<0>'):
		string = string[:-3]
	return string

class TBLData(object):
	def __init__(self, data_context, data_id, setting, path):
		self.data_context = data_context
		self.data_id = data_id
		self.setting = setting
		self.path = path
		self.strings = ()

		self.update_cb = Callback()

	def load_strings(self):
		tbl = TBL()
		path = self.data_context.settings.settings.files.get(self.setting, 'MPQ:' + self.path)
		tbl.load_file(self.data_context.mpqhandler.get_file(path))
		self.strings = tuple(convert_string(string) for string in tbl.strings)
		self.update_cb(self.data_id)
