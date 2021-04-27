
from ...FileFormats.DAT import WeaponsDAT


def run(path_to):
	"""weapons.dat load then save"""
	with open(path_to('weapons.dat'), 'rb') as f:
		raw_dat = f.read()

	dat = WeaponsDAT()
	dat.load_data(raw_dat)

	save_dat = dat.save_data()

	if save_dat != raw_dat:
		return False

	return True
