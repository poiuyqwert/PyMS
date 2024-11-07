
from ..FileFormats import JSON

from ..Utilities.UIKit import *
from ..Utilities import Assets

import uuid, json

from typing import TypeAlias, Literal

ItemID: TypeAlias = str

PathComponent: TypeAlias = int | str
Path = list[PathComponent]

Data = JSON.JSON.Array | JSON.JSON.Object

class DataSource:
	def __init__(self, data: Data | None = None) -> None:
		self.data = data
		self._itemid_to_path: dict[ItemID, Path] = {}
		self._treeview: Treeview | None = None
		self._treeview_font: Font
		self._treeview_arrow_width: int
		self._treeview_indent_width: int
		self.name_key: str | None = None
		self.all_keys: set[str] = set()

	def _is_flat(self, data: Data) -> bool:
		if isinstance(data, dict):
			for value in data.values():
				if isinstance(value, (dict, list)):
					return False
		elif isinstance(data, list):
			for value in data:
				if isinstance(value, (dict, list)):
					return False
		return True

	def _icon_for(self, value: JSON.JSON.Value) -> Image | None:
		if isinstance(value, dict):
			return Assets.get_image('debug')
		elif isinstance(value, list):
			return Assets.get_image('order')
		else:
			return None

	def _item_id(self, key: str | None = None) -> ItemID:
		item_id = uuid.uuid4().hex
		if key:
			item_id += f':{key}'
		return item_id

	def _object_name(self, data: JSON.JSON.Object) -> str:
		if self.name_key is not None and self.name_key in data:
			return str(data[self.name_key])
		return json.dumps(data)

	def _insert_object(self, data: JSON.JSON.Object, parent: str | None, index: int | Literal['end'] = END) -> None:
		if not self._treeview:
			return
		if self._is_flat(data):
			self._treeview.insert(parent or '', index, iid=self._item_id(), text=self._object_name(data))
			for key in data.keys():
				self.all_keys.add(key)
		else:
			for key, value in data.items():
				new_parent = self._treeview.insert(parent or '', index, iid=self._item_id(key), text=key, image=self._icon_for(value), open=True) # type: ignore[arg-type]
				self._insert_value(value, new_parent)
				self.all_keys.add(key)

	def _insert_array(self, data: JSON.JSON.Array, parent: str | None, index: int | Literal['end'] = END) -> None:
		if not self._treeview:
			return
		for value in data:
			self._insert_value(value, parent)

	def _insert_value(self, value: JSON.JSON.Value, parent: str | None = None, index: int | Literal['end'] = END):
		if not self._treeview:
			return
		if isinstance(value, dict):
			self._insert_object(value, parent, index)
		elif isinstance(value, list):
			self._insert_array(value, parent, index)
		else:
			self._treeview.insert(parent or '', index, iid=self._item_id(), text=str(value))

	def _item_depth(self, item_id: ItemID) -> int:
		if not self._treeview:
			return 0
		depth = 0
		parent_id = self._treeview.parent(item_id)
		if parent_id:
			depth += 1 + self._item_depth(parent_id)
		return depth

	def _item_width(self, item_id: ItemID, depth: int | None = None) -> int:
		if not self._treeview:
			return 0
		check_children = depth is not None
		if depth is None:
			depth = self._item_depth(item_id)
		max_width = (self._treeview_arrow_width + self._treeview_indent_width) * depth
		text = self._treeview.item(item_id, 'text')
		if text:
			max_width += self._treeview_font.measure(text)
		icon_name = self._treeview.item(item_id, 'image')
		if icon_name:
			max_width += self._treeview.tk.call('image', 'width', icon_name)
		children = self._treeview.get_children(item_id)
		if children:
			max_width += self._treeview_arrow_width
		if check_children:
			for child_id in children:
				max_width = max(max_width, self._item_width(child_id, depth+1))
		return max_width

	def _refresh_width(self) -> None:
		if not self._treeview:
			return
		max_width = 0
		for child_id in self._treeview.get_children(''):
			max_width = max(max_width, self._item_width(child_id, 0))
		self._treeview.column('#0', width=max_width, stretch=False)

	def _update_width(self, item_id: ItemID):
		if not self._treeview:
			return
		max_width = max(self._item_width(item_id), self._treeview.column('#0', 'width'))
		self._treeview.column('#0', width=max_width, stretch=False)

	def _refresh(self) -> None:
		if not self._treeview:
			return
		for item_id in self._treeview.get_children():
			self._treeview.delete(item_id)
		if not self.data:
			return
		self._insert_value(self.data)
		self._refresh_width()

	def attach(self, treeview: Treeview) -> None:
		Style().configure('Treeview', indent=25)
		self._treeview = treeview
		self._treeview_font = Font.named(Style().lookup('Treeview', 'font')) or Font.default()
		self._treeview_arrow_width = 16
		self._treeview_indent_width = Style().lookup('Treeview', 'indent')
		self._refresh()

	def set_data(self, data: Data | None) -> None:
		self.data = data
		self._refresh()

	def item_path(self, item_id: ItemID) -> Path:
		path: Path = []
		if not self._treeview:
			return path
		
		parent_id = self._treeview.parent(item_id)
		if parent_id:
			path = self.item_path(parent_id)
		
		component: str | int
		if ':' in item_id:
			component = item_id.split(':', 1)[-1]
		else:
			component = self._treeview.index(item_id)
		path.append(component)
		
		return path

	def value_at(self, path: Path) -> JSON.JSON.Value:
		data: JSON.JSON.Value = self.data
		for component in path:
			if isinstance(component, str):
				assert isinstance(data, dict)
				data = data[component]
			else:
				assert isinstance(data, list)
				data = data[component]
		return data

	def value_for(self, item_id: ItemID) -> JSON.JSON.Value:
		path = self.item_path(item_id)
		return self.value_at(path)
