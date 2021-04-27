
import units
import weapons
import flingy
import sprites
import images
import upgrades
import techdata
import sfxdata
import portdata
import mapdata
import orders

tests = [
	units,
	weapons,
	flingy,
	sprites,
	images,
	upgrades,
	techdata,
	sfxdata,
	portdata,
	mapdata,
	orders
]

from .. import testing


do_tests = testing.prepare(tests)
