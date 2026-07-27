
from .utils import PySPKTestCase

from unittest import mock

ASKYESNO = 'tkinter.messagebox.askyesno'


class Test_PySPK_stars_tab_move_buttons(PySPKTestCase):
	def test_move_down_button_moves_selected_star_toward_end(self) -> None:
		gui = self.with_layers_of_stars()
		assert gui.spk is not None
		first = gui.spk.layers[0].stars[0]
		gui.selected_stars.append(first)
		gui.update_selection()
		self.invoke(gui.stars_tab.move_down_button)
		self.assertEqual(gui.spk.layers[0].stars.index(first), 1)

	def test_move_up_button_moves_selected_star_toward_start(self) -> None:
		gui = self.with_layers_of_stars()
		assert gui.spk is not None
		second = gui.spk.layers[0].stars[1]
		gui.selected_stars.append(second)
		gui.update_selection()
		self.invoke(gui.stars_tab.move_up_button)
		self.assertEqual(gui.spk.layers[0].stars.index(second), 0)


class Test_PySPK_stars_list_rows(PySPKTestCase):
	def test_rows_only_cover_visible_unlocked_layers(self) -> None:
		gui = self.with_layers_of_stars(layers=2, stars_per_layer=2)
		# Hide layer 0: its stars must vanish from the list, and the remaining
		# rows must map to layer 1's stars by index.
		gui.visible.set(gui.visible.get() & ~1)
		self.pump(gui)
		rows = gui.stars_tab.get_listbox_rows()
		assert gui.spk is not None
		self.assertEqual([star for star, _ in rows], gui.spk.layers[1].stars)
		self.assertEqual([layer for _, layer in rows], [1, 1])
		self.assertEqual(gui.stars_tab.listbox.size(), 2)

	def test_selection_highlight_uses_row_index_space(self) -> None:
		gui = self.with_layers_of_stars(layers=2, stars_per_layer=2)
		gui.visible.set(gui.visible.get() & ~1)
		self.pump(gui)
		assert gui.spk is not None
		gui.selected_stars.append(gui.spk.layers[1].stars[0])
		gui.stars_tab.update_selection()
		self.assertEqual(gui.stars_tab.listbox.curselection(), (0,))


class Test_PySPK_delete_stars(PySPKTestCase):
	def test_delete_removes_selected_star_from_its_layer(self) -> None:
		gui = self.with_layers_of_stars(layers=2, stars_per_layer=2)
		assert gui.spk is not None
		star = gui.spk.layers[0].stars[0]
		untouched = list(gui.spk.layers[1].stars)
		gui.selected_stars.append(star)
		gui.update_selection()
		with mock.patch(ASKYESNO, return_value=True):
			gui.delete_stars()
		self.assertNotIn(star, gui.spk.layers[0].stars)
		self.assertEqual(gui.spk.layers[1].stars, untouched)
		self.assertEqual(gui.selected_stars, [])
		self.assertNotIn(star, gui.item_map)

	def test_delete_declined_keeps_stars(self) -> None:
		gui = self.with_layers_of_stars()
		assert gui.spk is not None
		star = gui.spk.layers[0].stars[0]
		gui.selected_stars.append(star)
		gui.update_selection()
		with mock.patch(ASKYESNO, return_value=False):
			gui.delete_stars()
		self.assertIn(star, gui.spk.layers[0].stars)
