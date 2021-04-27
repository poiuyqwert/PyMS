
from ...FileFormats.DAT import ImagesDAT


def run(path_to):
	"""images.dat load then save"""
	with open(path_to('images.dat'), 'rb') as f:
		raw_dat = f.read()

	dat = ImagesDAT()
	dat.load_data(raw_dat)

	save_dat = dat.save_data()

	if save_dat != raw_dat:
		return False

	return True
