
from ..FileFormats.TBL import TBL, decompile_string

def convert_string(string):
	string = decompile_string(string)
	if string.endswith('<0>'):
		string = string[:-3]
	return string

class TBLData(object):
	def __init__(self, data_context, setting, path):
		self.data_context = data_context
		self.setting = setting
		self.path = path
		self.strings = ()

	def load_strings(self):
		tbl = TBL()
		path = self.data_context.settings.settings.files.get(self.setting, 'MPQ:' + self.path)
		tbl.load_file(self.data_context.mpqhandler.get_file(path))
		self.strings = tuple(convert_string(string) for string in tbl.strings)
