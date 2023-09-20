
from .SettingView import SettingView

from ..UIKit import *
from ..EditedState import EditedState
from .. import Config

class CheckboxSettingView(SettingView):
	def __init__(self, parent: Misc, edited_state: EditedState, name: str, setting: Config.Boolean):
		super().__init__(parent, edited_state)
		self.setting = setting
		self.variable = BooleanVar()
		self.variable.set(setting.value)
		Checkbutton(self, text=name, variable=self.variable, command=self.changed).pack()

	def changed(self, *_) -> None:
		edited = self.variable.get() != self.setting.value
		self.edited_state.mark_edited(edited)

	def save(self) -> None:
		self.setting.value = self.variable.get()
