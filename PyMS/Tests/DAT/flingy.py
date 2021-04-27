
from ...FileFormats.DAT import FlingyDAT


def run(path_to):
	"""flingy.dat load then save"""
	with open(path_to('flingy.dat'), 'rb') as f:
		raw_dat = f.read()

	dat = FlingyDAT()
	dat.load_data(raw_dat)

	save_dat = dat.save_data()

	if save_dat != raw_dat:
		return False

	return True
