
import save_load
import image_bounds

tests = [
	save_load,
	image_bounds
]

from .. import testing


do_tests = testing.prepare(tests)
