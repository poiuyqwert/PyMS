
from .utils import PyGOTTestCase

from ...FileFormats import GOT
from ...Utilities import UIKit as UI

from unittest import mock


class Test_PyGOT_edited_tracking(PyGOTTestCase):
	def test_new_document_starts_unedited(self) -> None:
		gui = self.make_pygot()
		gui.new()
		self.assertFalse(gui.edited)

	def test_league_id_change_marks_edited(self) -> None:
		gui = self.make_pygot()
		gui.new()
		gui.mark_edited(False)
		gui.league_id.set(5)
		self.assertTrue(gui.edited)


class Test_PyGOT_value_entry_states(PyGOTTestCase):
	def test_value_entry_follows_dropdown_selection(self) -> None:
		gui = self.make_pygot()
		gui.new()
		self.assertEqual(str(gui.victory_condition_entry['state']), UI.DISABLED)
		gui.victory_condition.set(GOT.VictoryCondition.resources.value)
		self.assertEqual(str(gui.victory_condition_entry['state']), UI.NORMAL)
		gui.victory_condition.set(GOT.VictoryCondition.map_default.value)
		self.assertEqual(str(gui.victory_condition_entry['state']), UI.DISABLED)
		gui.resources.set(GOT.Resources.fixed_value.value)
		self.assertEqual(str(gui.resources_entry['state']), UI.NORMAL)

	def test_value_entries_disabled_after_close(self) -> None:
		gui = self.make_pygot()
		gui.new()
		gui.victory_condition.set(GOT.VictoryCondition.resources.value)
		gui.resources.set(GOT.Resources.income.value)
		with mock.patch('tkinter.messagebox.askyesnocancel', return_value=False):
			gui.close()
		self.assertEqual(str(gui.victory_condition_entry['state']), UI.DISABLED)
		self.assertEqual(str(gui.resources_entry['state']), UI.DISABLED)


class Test_PyGOT_file_open_state(PyGOTTestCase):
	def test_file_open_reflects_document_presence(self) -> None:
		gui = self.make_pygot()
		self.assertFalse(gui.is_file_open())
		gui.new()
		self.assertTrue(gui.is_file_open())
