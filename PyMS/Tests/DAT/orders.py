
from ...FileFormats.DAT import OrdersDAT


def run(path_to):
	"""orders.dat load then save"""
	with open(path_to('orders.dat'), 'rb') as f:
		raw_dat = f.read()

	dat = OrdersDAT()
	dat.load_data(raw_dat)

	save_dat = dat.save_data()

	if save_dat != raw_dat:
		return False

	return True
