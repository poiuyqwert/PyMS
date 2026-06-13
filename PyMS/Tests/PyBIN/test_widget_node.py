
from ...PyBIN.WidgetNode import WidgetNode
from ...PyBIN.Delegates import NodeDelegate
from ...FileFormats.DialogBIN import BINWidget

import unittest
from unittest.mock import Mock
from typing import cast


def _delegate(show_hidden: bool = False, asset: object | None = None) -> NodeDelegate:
	delegate = Mock()
	delegate.get_show_hidden.return_value = show_hidden
	delegate.get_dialog_asset.return_value = asset
	return cast(NodeDelegate, delegate)


def _node(widget: BINWidget | None = None, delegate: NodeDelegate | None = None) -> WidgetNode:
	return WidgetNode(delegate or cast(NodeDelegate, Mock()), widget)


def _widget(widget_type: int, *, box: tuple[int, int, int, int] = (0, 0, 0, 0), string: str = '') -> BINWidget:
	widget = BINWidget(widget_type)
	widget.x1, widget.y1, widget.x2, widget.y2 = box
	widget.string = string
	return widget


class Test_construction(unittest.TestCase):
	def test_group_node_has_child_list(self) -> None:
		self.assertEqual(_node().children, [])

	def test_dialog_widget_is_a_group(self) -> None:
		self.assertEqual(_node(_widget(BINWidget.TYPE_DIALOG)).children, [])

	def test_non_dialog_widget_is_a_leaf(self) -> None:
		self.assertIsNone(_node(_widget(BINWidget.TYPE_CHECKBOX)).children)


class Test_get_name(unittest.TestCase):
	def test_group_default(self) -> None:
		self.assertEqual(_node().get_name(), 'Group')

	def test_explicit_name_wins(self) -> None:
		node = _node()
		node.name = 'Custom'
		self.assertEqual(node.get_name(), 'Custom')

	def test_widget_without_text_uses_type_name(self) -> None:
		# An image widget has no display text.
		self.assertEqual(_node(_widget(BINWidget.TYPE_IMAGE)).get_name(), 'Image')

	def test_widget_with_text(self) -> None:
		node = _node(_widget(BINWidget.TYPE_LABEL_LEFT_ALIGN, string='Hello'))
		self.assertEqual(node.get_name(), 'Hello [Label (Left Align)]')


class Test_tree_mutation(unittest.TestCase):
	def test_add_child_sets_parent_and_appends(self) -> None:
		parent = _node()
		child = _node(_widget(BINWidget.TYPE_BUTTON))
		parent.add_child(child)
		self.assertEqual(parent.children, [child])
		self.assertIs(child.parent, parent)

	def test_add_child_at_index(self) -> None:
		parent = _node()
		first = _node(_widget(BINWidget.TYPE_BUTTON))
		second = _node(_widget(BINWidget.TYPE_BUTTON))
		parent.add_child(first)
		parent.add_child(second, index=0)
		assert parent.children is not None
		self.assertEqual(parent.children, [second, first])

	def test_add_child_reparents(self) -> None:
		old_parent = _node()
		new_parent = _node()
		child = _node(_widget(BINWidget.TYPE_BUTTON))
		old_parent.add_child(child)
		new_parent.add_child(child)
		self.assertEqual(old_parent.children, [])
		self.assertEqual(new_parent.children, [child])
		self.assertIs(child.parent, new_parent)

	def test_add_child_to_leaf_is_noop(self) -> None:
		leaf = _node(_widget(BINWidget.TYPE_CHECKBOX))
		child = _node(_widget(BINWidget.TYPE_BUTTON))
		leaf.add_child(child)
		self.assertIsNone(leaf.children)
		self.assertIsNone(child.parent)

	def test_remove_from_parent(self) -> None:
		parent = _node()
		child = _node(_widget(BINWidget.TYPE_BUTTON))
		parent.add_child(child)
		child.remove_from_parent()
		self.assertEqual(parent.children, [])
		self.assertIsNone(child.parent)

	def test_remove_without_parent_is_noop(self) -> None:
		node = _node(_widget(BINWidget.TYPE_BUTTON))
		node.remove_from_parent()  # should not raise
		self.assertIsNone(node.parent)


class Test_visibility(unittest.TestCase):
	def test_visible_when_flag_set(self) -> None:
		# BINWidget defaults to FLAG_VISIBLE.
		node = _node(_widget(BINWidget.TYPE_BUTTON), _delegate(show_hidden=False))
		self.assertTrue(node.visible())

	def test_hidden_widget_respects_show_hidden(self) -> None:
		widget = _widget(BINWidget.TYPE_BUTTON)
		widget.flags &= ~BINWidget.FLAG_VISIBLE
		self.assertFalse(_node(widget, _delegate(show_hidden=False)).visible())
		self.assertTrue(_node(widget, _delegate(show_hidden=True)).visible())

	def test_group_is_always_visible(self) -> None:
		self.assertTrue(_node().visible())

	def test_enabled_by_default(self) -> None:
		self.assertTrue(_node(_widget(BINWidget.TYPE_BUTTON)).enabled())

	def test_disabled_flag(self) -> None:
		widget = _widget(BINWidget.TYPE_BUTTON)
		widget.flags |= BINWidget.FLAG_DISABLED
		self.assertFalse(_node(widget).enabled())


class Test_bounding_box(unittest.TestCase):
	def test_widget_bounding_box(self) -> None:
		node = _node(_widget(BINWidget.TYPE_BUTTON, box=(10, 20, 30, 40)))
		self.assertEqual(node.bounding_box(), (10, 20, 30, 40))

	def test_group_union_of_children(self) -> None:
		group = _node()
		group.add_child(_node(_widget(BINWidget.TYPE_BUTTON, box=(10, 10, 20, 20))))
		group.add_child(_node(_widget(BINWidget.TYPE_BUTTON, box=(30, 5, 40, 25))))
		self.assertEqual(group.bounding_box(), (10, 5, 40, 25))

	def test_leaf_without_widget_is_zero(self) -> None:
		node = _node()
		node.children = None
		self.assertEqual(node.bounding_box(), (0, 0, 0, 0))


class Test_text_box(unittest.TestCase):
	def test_applies_text_offsets(self) -> None:
		widget = _widget(BINWidget.TYPE_LABEL_LEFT_ALIGN, box=(10, 10, 50, 30))
		widget.text_offset_x = 3
		widget.text_offset_y = 4
		self.assertEqual(_node(widget).text_box(), (13, 14, 50, 30))

	def test_checkbox_offsets_by_asset_width(self) -> None:
		asset = Mock()
		asset.size = (12, 10)
		node = _node(_widget(BINWidget.TYPE_CHECKBOX, box=(0, 0, 100, 20)), _delegate(asset=asset))
		self.assertEqual(node.text_box(), (16, 0, 100, 20))

	def test_option_button_offsets_by_asset_width(self) -> None:
		asset = Mock()
		asset.size = (8, 8)
		node = _node(_widget(BINWidget.TYPE_OPTION_BTN, box=(0, 0, 100, 20)), _delegate(asset=asset))
		self.assertEqual(node.text_box(), (12, 0, 100, 20))

	def test_checkbox_without_asset(self) -> None:
		node = _node(_widget(BINWidget.TYPE_CHECKBOX, box=(0, 0, 100, 20)), _delegate(asset=None))
		self.assertEqual(node.text_box(), (0, 0, 100, 20))
