
from ...FileFormats.DAT import SpritesDAT


def run(path_to):
	"""sprites.dat load then save"""
	with open(path_to('sprites.dat'), 'rb') as f:
		raw_dat = f.read()

	dat = SpritesDAT()
	dat.load_data(raw_dat)

	save_dat = dat.save_data()

	if save_dat != raw_dat:
		return False

	return True
