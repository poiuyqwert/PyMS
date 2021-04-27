
from ...FileFormats.DAT import SoundsDAT


def run(path_to):
	"""sfxdata.dat load then save"""
	with open(path_to('sfxdata.dat'), 'rb') as f:
		raw_dat = f.read()

	dat = SoundsDAT()
	dat.load_data(raw_dat)

	save_dat = dat.save_data()

	if save_dat != raw_dat:
		return False

	return True
