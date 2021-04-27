
from ...FileFormats.DAT import TechDAT


def run(path_to):
	"""techdata.dat load then save"""
	with open(path_to('techdata.dat'), 'rb') as f:
		raw_dat = f.read()

	dat = TechDAT()
	dat.load_data(raw_dat)

	save_dat = dat.save_data()

	if save_dat != raw_dat:
		return False

	return True
