
from ...FileFormats.DAT import OrdersDAT

from ..utils import resource_path

import unittest

class Test_Orders(unittest.TestCase):
	def test_load_and_save(self):
		with open(resource_path('orders.dat', __file__), 'rb') as f:
			expected = f.read()

		dat = OrdersDAT()
		dat.load_data(expected)

		result = dat.save_data()

		self.assertEqual(result, expected)
