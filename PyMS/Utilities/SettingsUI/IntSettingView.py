
from .SettingView import SettingView

from .. import Config
from ..UIKit import *
from ..EditedState import EditedState

class IntSettingView(SettingView):
	def __init__(self, parent: Misc, edited_state: EditedState, name: str, description: str, setting: Config.Int) -> None:
		super().__init__(parent, edited_state)
		self.setting = setting
		
		self.variable = IntegerVar(0)
		width = 10
		if setting.limits is not None:
			self.variable.range = setting.limits
			width = len(str(setting.limits[1]))
		if setting.value is not None:
			self.variable.set(setting.value)
		self.variable.trace('w', self.changed)

		Label(self, text=name, font=Font.default().bolded(), anchor=W).pack(fill=X, expand=1)
		Label(self, text=description, anchor=W).pack(fill=X, expand=1)
		Entry(self, textvariable=self.variable, width=width).pack(side=LEFT)

	def changed(self, *_) -> None:
		edited = self.variable.get() != self.setting.value
		self.edited_state.mark_edited(edited)

	def save(self) -> None:
		self.setting.value = self.variable.get()
