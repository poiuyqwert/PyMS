
from ..Config import PyAIConfig
from ..CodeEditDialog import CodeEditDialog

from ...Utilities import UIKit as UI
from ...Utilities.PyMSDialog import PyMSDialog
from ...Utilities.Config import WindowGeometry

class PreviewScriptDialog(PyMSDialog):
	def __init__(self, parent: UI.Misc, *, code: str, title: str, window_geometry_config: WindowGeometry, highlights_config: PyAIConfig.Code.Highlights) -> None:
		self.code = code
		self.window_geometry_config = window_geometry_config
		self.highlights_config = highlights_config
		super().__init__(parent, title)

	def widgetize(self) -> UI.Misc | None:
		text = UI.CodeText(self)
		text.set_read_only(True)
		text.load(self.code)
		text.pack(fill=UI.BOTH, expand=True, padx=1, pady=1)

		self.syntax_highlighting = CodeEditDialog.build_syntax_highlighting(self.highlights_config)
		text.set_syntax_highlighting(self.syntax_highlighting)

		return None

	def setup_complete(self) -> None:
		self.window_geometry_config.load_size(self)

	def dismiss(self) -> None:
		self.window_geometry_config.save_size(self)
		super().dismiss()
