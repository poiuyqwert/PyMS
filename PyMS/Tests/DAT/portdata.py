
from ...FileFormats.DAT import PortraitsDAT


def run(path_to):
	"""portdata.dat load then save"""
	with open(path_to('portdata.dat'), 'rb') as f:
		raw_dat = f.read()

	dat = PortraitsDAT()
	dat.load_data(raw_dat)

	save_dat = dat.save_data()

	if save_dat != raw_dat:
		return False

	return True
