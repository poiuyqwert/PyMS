
from .GraftData import UnitsGraftData, UpgradesGraftData, ResearchGraftData, TechGraftData, OrdersGraftData, ButtonsGraftData, AnyGraftData

from ..FileFormats.TBL import TBL
from ..FileFormats.DAT import UnitsDAT, UpgradesDAT, TechDAT, OrdersDAT

from ..Utilities.DataContext import DataContext
from ..Utilities import Assets

# The file types, in the order of the CLI options
FILE_TYPES = ('units', 'upgrades', 'research', 'tech', 'orders', 'buttons')

def graft_data(file_type: str) -> AnyGraftData:
	match file_type:
		case 'units':
			return UnitsGraftData()
		case 'upgrades':
			return UpgradesGraftData()
		case 'research':
			return ResearchGraftData()
		case 'tech':
			return TechGraftData()
		case 'orders':
			return OrdersGraftData()
		case 'buttons':
			return ButtonsGraftData()
	raise ValueError(f'Unknown Graft file type `{file_type}`')

def vanilla_data_context() -> DataContext:
	# The bundled vanilla stat_txt.tbl and DAT files, so names in the code match the game
	stat_txt = TBL()
	stat_txt.load(Assets.mpq_file_path('rez', 'stat_txt.tbl'))
	units_dat = UnitsDAT()
	units_dat.load(Assets.mpq_file_path('arr', 'units.dat'))
	upgrades_dat = UpgradesDAT()
	upgrades_dat.load(Assets.mpq_file_path('arr', 'upgrades.dat'))
	techdata_dat = TechDAT()
	techdata_dat.load(Assets.mpq_file_path('arr', 'techdata.dat'))
	orders_dat = OrdersDAT()
	orders_dat.load(Assets.mpq_file_path('arr', 'orders.dat'))
	return DataContext(stat_txt_tbl=stat_txt, units_dat=units_dat, upgrades_dat=upgrades_dat, techdata_dat=techdata_dat, orders_dat=orders_dat)

def decompile_graft(file_type: str, input_path: str, output_path: str) -> None:
	data = graft_data(file_type)
	for warning in data.load(input_path):
		print(repr(warning))
	data.export_text(output_path, vanilla_data_context())

def compile_graft(file_type: str, input_path: str, output_path: str) -> None:
	data = graft_data(file_type)
	data.import_text(input_path, vanilla_data_context())
	data.save(output_path)
