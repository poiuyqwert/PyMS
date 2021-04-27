
from ...FileFormats.DAT import CampaignDAT


def run(path_to):
	"""mapdata.dat load then save"""
	with open(path_to('mapdata.dat'), 'rb') as f:
		raw_dat = f.read()

	dat = CampaignDAT()
	dat.load_data(raw_dat)

	save_dat = dat.save_data()

	if save_dat != raw_dat:
		return False

	return True
