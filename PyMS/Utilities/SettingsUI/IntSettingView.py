
from .SettingView import SettingView

from .. import Config
from .. import UIKit as UI
from ..EditedState import EditedState

from typing import Any

class IntSettingView(SettingView):
	def __init__(self, *, parent: UI.Misc, edited_state: EditedState, name: str, description: str, setting: Config.Int) -> None:
		super().__init__(parent, edited_state)
		self.setting = setting

		self.variable = UI.IntegerVar(0)
		width = 10
		if setting.limits is not None:
			self.variable.range = setting.limits
			width = len(str(setting.limits[1]))
		if setting.value is not None:
			self.variable.set(setting.value)
		self.variable.trace_add('write', self.changed)

		UI.Label(self, text=name, font=UI.Font.default().bolded(), anchor=UI.W).pack(fill=UI.X, expand=1)
		UI.Label(self, text=description, anchor=UI.W).pack(fill=UI.X, expand=1)
		UI.Entry(self, textvariable=self.variable, width=width).pack(side=UI.LEFT)

	def changed(self, *_: Any) -> None:
		edited = self.variable.get() != self.setting.value
		self.edited_state.mark_edited(edited)

	def save(self) -> None:
		self.setting.value = self.variable.get()
