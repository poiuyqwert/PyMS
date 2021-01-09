
from ...utils import BASE_DIR

import os

DAT_DATA_REFERENCE = {
	'SelCircleSize.txt':'Selection Circle Sizes',
	'Rightclick.txt':'Right Click Actions',
	'Flingy.txt':'Flingy Entries',
	'Behaviours.txt':'Behaviours',
	'DamTypes.txt':'Damage Types',
	'Mapdata.txt':'Campaign Names',
	'Units.txt':'Default Units',
	'Remapping.txt':'Remapping',
	'DrawList.txt':'Draw Types', 
	'FlingyControl.txt':'Flingy Controlers',
	'Sprites.txt':'Default Sprites',
	'Animations.txt':'IScript Animations',
	'Orders.txt':'Default Orders',
	'IscriptIDList.txt':"IScript ID's",
	'Portdata.txt':'Default Campaign',
	'Weapons.txt':'Default Weapons',
	'UnitSize.txt':'Unit Sizes',
	'Techdata.txt':'Default Technologies',
	'ElevationLevels.txt':'Elevation Levels',
	'Images.txt':'Default Images',
	'Upgrades.txt':'Default Upgrades',
	'Explosions.txt':'Explosion Types',
	'Races.txt':'Races',
	'Icons.txt':'Icons',
	'Sfxdata.txt':'Sound Effects',
	'ShieldSize.txt':'Shield Sizes'
}

DAT_DATA_CACHE = {}
for d in DAT_DATA_REFERENCE.keys():
	f = open(os.path.join(BASE_DIR, 'Libs', 'Data', d),'r')
	DAT_DATA_CACHE[d] = [l.rstrip() for l in f.readlines()]
	f.close()