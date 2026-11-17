
from .Delegates import MainDelegate

from ..FileFormats import TBL

from ..Utilities.PyMSDialog import PyMSDialog
from ..Utilities import UIKit as UI
from ..Utilities.TextPreview.Layout import TextLayout, TextStyle, TextRuns
from ..Utilities.TextPreview.HotkeyString import HotkeyString, TooltipCosts
from ..Utilities.TextPreview.TextDrawing import TextDrawing


class PreviewDialog(PyMSDialog):
	# The text is drawn this far from the top left of the canvas (inside its border)
	PADDING = 7
	MIN_WIDTH = 200

	def __init__(self, parent: UI.Misc, delegate: MainDelegate) -> None:
		self.delegate = delegate
		self.drawing: TextDrawing | None = None
		self.hotkey = UI.BooleanVar()
		self.hotkey.set(self.delegate.config_.preview.hotkey.value)
		self.endatnull = UI.BooleanVar()
		self.endatnull.set(self.delegate.config_.preview.end_at_null.value)
		PyMSDialog.__init__(self, parent, 'Text Previewer', resizable=(False,False))

	def preview(self) -> None:
		if self.drawing:
			self.drawing.delete()
			self.drawing = None
		data_context = self.delegate.data_context
		text = TBL.compile_string(self.delegate.text.get('1.0',UI.END)[:-1])
		hotkey_string = HotkeyString.parse(text, stop_at_null=self.endatnull.get()) if self.hotkey.get() else None
		runs: TextRuns
		if hotkey_string:
			runs = hotkey_string.tooltip_runs(TooltipCosts.placeholder(hotkey_string.kind), data_context)
			font = data_context.font8_fnt
		else:
			runs = TBL.end_at_null(text) if self.endatnull.get() else text
			font = data_context.font10_fnt
		colors = data_context.tfontgam_pcx
		width = PreviewDialog.MIN_WIDTH
		height = 16
		if text and font and colors:
			self.drawing = TextDrawing(TextLayout.from_runs(runs, TextStyle.ingame(font, colors)), data_context)
			width = max(width, self.drawing.width)
			height = self.drawing.height
			self.drawing.draw(self.canvas, PreviewDialog.PADDING, PreviewDialog.PADDING)
		self.canvas.config(width=width+10, height=height+10)

	def widgetize(self) -> (UI.Misc | None):
		self.canvas = UI.Canvas(self, width=200, height=16, background='#000000', bd=2, relief=UI.SUNKEN)
		self.canvas.pack(padx=5, pady=5)
		f = UI.Frame(self)
		UI.Checkbutton(f, text='Hotkey String', variable=self.hotkey, command=self.preview).pack(side=UI.LEFT)
		UI.Checkbutton(f, text='End at Null', variable=self.endatnull, command=self.preview).pack(side=UI.LEFT)
		f.pack()
		self.preview()
		ok = UI.Button(self, text='Ok', width=10, command=self.ok)
		ok.pack(pady=3)
		return ok

	def ok(self, _event: UI.Event | None = None) -> None:
		self.delegate.config_.preview.hotkey.value = self.hotkey.get()
		self.delegate.config_.preview.end_at_null.value = self.endatnull.get()
		PyMSDialog.ok(self)
