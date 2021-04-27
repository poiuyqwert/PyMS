
from ...FileFormats.DAT import UpgradesDAT


def run(path_to):
	"""upgrades.dat load then save"""
	with open(path_to('upgrades.dat'), 'rb') as f:
		raw_dat = f.read()

	dat = UpgradesDAT()
	dat.load_data(raw_dat)

	save_dat = dat.save_data()

	if save_dat != raw_dat:
		return False

	return True
