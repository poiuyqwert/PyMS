
from ..FileFormats.TBL import TBL, decompile_string

def convert_string(string):
	string = decompile_string(string)
	if string.endswith('<0>'):
		string = string[:-3]
	return string

class TBLData(object):
	def __init__(self, setting, path):
		self.setting = setting
		self.path = path
		# TODO: Make tuple
		self.strings = []

	def load_strings(self, mpqhandler, settings):
		tbl = TBL()
		tbl.load_file(mpqhandler.get_file(settings.settings.files.get(self.setting, 'MPQ:' + self.path)))
		self.strings = [convert_string(string) for string in tbl.strings]
