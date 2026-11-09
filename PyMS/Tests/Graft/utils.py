from ...FileFormats.Graft import AbstractReqGraft, ReqScript, ButtonsGraft
from ...FileFormats.Graft.CodeHandlers import GraftLexer, GraftParseContext, GraftSerializeContext, GraftLanguage
from ...Utilities.DataContext import DataContext
from ...FileFormats.TBL import TBL
from ...FileFormats.DAT import UnitsDAT, UpgradesDAT, TechDAT, OrdersDAT
from ...Utilities import Assets
from ...Utilities import Struct

import io
import struct
from functools import cache

def words(*values: int) -> bytes:
	return Struct.l_au16(len(values)).pack(list(values))

@cache
def vanilla_data_context() -> DataContext:
	# The bundled vanilla stat_txt.tbl and DAT files, so names match the game (shared, so must not be modified)
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

def parse_context(code: str, data_context: DataContext | None = None, language: GraftLanguage | None = None) -> GraftParseContext:
	return GraftParseContext(GraftLexer(code), data_context if data_context is not None else vanilla_data_context(), language)

def decompile_req(graft: AbstractReqGraft, data_context: DataContext | None = None) -> str:
	output = io.StringIO()
	graft.decompile(GraftSerializeContext(output, data_context if data_context is not None else vanilla_data_context()))
	return output.getvalue()

def compile_req(code: str, graft_type: type[AbstractReqGraft], data_context: DataContext | None = None) -> list[ReqScript]:
	return graft_type.compile(parse_context(code, data_context, graft_type.LANGUAGE()))

def decompile_req_script(graft: AbstractReqGraft, entry_id: int, data_context: DataContext | None = None) -> str:
	output = io.StringIO()
	graft.decompile_script(GraftSerializeContext(output, data_context if data_context is not None else vanilla_data_context()), entry_id)
	return output.getvalue()

def compile_req_script(code: str, graft_type: type[AbstractReqGraft], entry_id: int, data_context: DataContext | None = None) -> ReqScript:
	return ReqScript.compile(parse_context(code, data_context, graft_type.LANGUAGE()), entry_id, graft_type.LANGUAGE)

def decompile_buttons(graft: ButtonsGraft, data_context: DataContext | None = None) -> str:
	output = io.StringIO()
	graft.decompile(GraftSerializeContext(output, data_context if data_context is not None else vanilla_data_context()))
	return output.getvalue()

def compile_buttons(code: str, data_context: DataContext | None = None) -> ButtonsGraft:
	return ButtonsGraft.compile(parse_context(code, data_context))

def button_bytes(position: int, icon: int, condition: int, action: int, *, condition_param: int = 0, action_param: int = 0, enabled_string: int = 0, disabled_string: int = 0) -> bytes:
	return struct.pack('<HHIIHHHH', position, icon, condition, action, condition_param, action_param, enabled_string, disabled_string)

def buttons_file(buttons: list[bytes], units: list[tuple[int, int, int, int]], stat_info: list[tuple[int, int, int]]) -> bytes:
	data = struct.pack('<III', len(buttons), len(units), len(stat_info))
	data += b''.join(buttons)
	data += b''.join(struct.pack('<IIHH', *unit) for unit in units)
	data += b''.join(struct.pack('<III', *info) for info in stat_info)
	return data

def fgp_chunk(tag: bytes, data: bytes) -> bytes:
	return tag + struct.pack('<I', len(data)) + data

def fgp_file(*chunks: bytes, version: bytes = b'1.16.1') -> bytes:
	return fgp_chunk(b'FgPa', version + b'\x00') + b''.join(chunks)
