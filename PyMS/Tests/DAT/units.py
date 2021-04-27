
from ...FileFormats.DAT import UnitsDAT


def run(path_to):
	"""units.dat load then save"""
	with open(path_to('units.dat'), 'rb') as f:
		raw_dat = f.read()

	dat = UnitsDAT()
	dat.load_data(raw_dat)

	save_dat = dat.save_data()

	if save_dat != raw_dat:
		return False

	return True
