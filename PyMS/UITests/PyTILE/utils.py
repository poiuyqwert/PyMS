from ..harness import UITestCase

from ...PyTILE.PyTILE import PyTILE
from ...FileFormats.Tileset.Tileset import Tileset
from ...FileFormats.Tileset.CV5 import CV5Group
from ...FileFormats.Tileset.VF4 import VF4Megatile
from ...FileFormats.Tileset.VX4 import VX4Megatile
from ...Utilities import UIKit as UI

import tkinter
from unittest import mock

from typing import Any

# These tests drive PyTILE through its real menubar, toolbar and shortcuts. The
# harness already neutralizes settings I/O, analytics, the update check, and the
# tracer for construction. Opening a tileset goes through the real Open flow with
# `Tileset.load` stubbed to build a small in-memory tileset, and tile images are
# stubbed with blank images so no palette or graphics data is needed.

TILESET_LOAD = 'PyMS.PyTILE.PyTILE.Tileset.load'
GET_TILE = 'PyMS.PyTILE.PyTILE.PyTILE.get_tile'


def _fill_tileset(tileset: Tileset, *_args: Any, **_kwargs: Any) -> None:
	tileset.new_file()
	for _ in range(2):
		tileset.vf4.add_megatile(VF4Megatile())
		tileset.vx4.add_megatile(VX4Megatile())
	for _ in range(20):
		group = CV5Group()
		group.megatile_ids = [0] * 16
		tileset.cv5.add_group(group)


class PyTILETestCase(UITestCase):
	def open_pytile(self) -> PyTILE:
		return self.make_window(PyTILE)

	def with_open_tileset(self) -> PyTILE:
		gui = self.open_pytile()
		blank = tkinter.PhotoImage(master=gui, width=32, height=32)
		patcher = mock.patch(GET_TILE, return_value=blank)
		patcher.start()
		self.addCleanup(patcher.stop)
		with mock.patch(TILESET_LOAD, autospec=True, side_effect=_fill_tileset):
			gui.open(file='test.cv5')
		self.pump(gui)
		return gui


def menu_entries(menu: UI.Menu) -> list[str]:
	# The labels of a menu's entries in order, with separators as '-'.
	entries: list[str] = []
	last = menu.index(UI.END)
	if last is None:
		return entries
	for index in range(last + 1):
		if menu.type(index) == 'separator':
			entries.append('-')
		else:
			entries.append(menu.entrycget(index, 'label'))
	return entries


def menubar_cascades(gui: PyTILE) -> dict[str, UI.Menu]:
	cascades: dict[str, UI.Menu] = {}
	last = gui.menu.index(UI.END)
	assert last is not None
	for index in range(last + 1):
		label = gui.menu.entrycget(index, 'label')
		cascades[label] = gui.nametowidget(gui.menu.entrycget(index, 'menu'))
	return cascades
