
from __future__ import annotations

from .DestinationView import DestinationView
from .MPQConfigView import MPQConfigView

from ..Config import PyMODConfig
from ..Project import Project
from .. import Source

from ...Utilities import UIKit as UI
from ...Utilities import Config
from ...Utilities import JSON
from ...Utilities import fileutils
from ...Utilities.MPQHandler import MPQHandler
from ...Utilities.PyMSDialog import PyMSDialog
from ...Utilities.PyMSError import PyMSError
from ...Utilities.ErrorDialog import ErrorDialog
from ...Utilities import trace

import os, json

# Base for the dialogs that pull a file out of an MPQ and into a project as a source. Subclasses
# only describe the file types they handle (`matches`), any format specific options
# (`widgetize_options`), and how the source files get written (`perform_extract`); the destination,
# the MPQ config, the overwrite checks, and writing `config.json` are handled here so every
# extractor behaves the same
class ExtractorDialog(PyMSDialog):
	# Confidence (0 to 1) that this extractor handles `mpq_file_name`, which is the full backslash
	# separated name inside the archive (e.g. `unit\terran\marine.grp`) so an extractor can key on
	# where a file lives as well as what it's called
	@classmethod
	def matches(cls, mpq_file_name: str) -> float:
		raise NotImplementedError(cls.__name__ + '.matches()')

	def __init__(self, parent: UI.Misc, *, mpqhandler: MPQHandler, project: Project, config: PyMODConfig, mpq_file_name: str, title: str = 'Extract File') -> None:
		self.mpqhandler = mpqhandler
		self.project = project
		self.config_ = config
		self.mpq_file_name = mpq_file_name
		self.extracted = False
		PyMSDialog.__init__(self, parent, title, escape=True, resizable=(True,False))

	def window_geometry_config(self) -> Config.WindowGeometry:
		return self.config_.windows.extractors.default

	def widgetize(self) -> UI.Misc | None:
		UI.Label(self, text=f'Extracting `{self.mpq_file_name}`', anchor=UI.W, justify=UI.LEFT).pack(side=UI.TOP, fill=UI.X, padx=3, pady=3)

		self.widgetize_options(self)

		self.destination_view = DestinationView(self, project=self.project, mpq_file_name=self.mpq_file_name)
		self.destination_view.pack(side=UI.TOP, fill=UI.X, padx=3, pady=(0,3))

		self.mpq_config_view = MPQConfigView(self)
		self.mpq_config_view.pack(side=UI.TOP, fill=UI.X, padx=3, pady=(0,3))

		buttons = UI.Frame(self)
		extract_button = UI.Button(buttons, text='Extract', width=10, command=self.ok)
		extract_button.pack(side=UI.LEFT, padx=1)
		UI.Button(buttons, text='Cancel', width=10, command=self.cancel).pack(side=UI.LEFT, padx=1)
		buttons.pack(side=UI.BOTTOM, pady=(0,3))

		return extract_button

	# Format specific options, displayed above the shared destination and MPQ config views. The
	# default extractor has none, which is what makes it MPQ config only
	def widgetize_options(self, parent: UI.Misc) -> None:
		pass

	def setup_complete(self) -> None:
		self.window_geometry_config().load_size(self)

	# Writes the source files for `destination_path` and returns any format specific keys to store
	# in the extracted item's `config.json` (the MPQ config is merged in by `ok`)
	def perform_extract(self, destination_path: str) -> JSON.Object:
		raise NotImplementedError(self.__class__.__name__ + '.perform_extract()')

	def ok(self, _event: UI.Event | None = None) -> None:
		try:
			destination_path = self.destination_view.destination_path()
		except PyMSError as e:
			ErrorDialog(self, e)
			return
		if os.path.exists(destination_path):
			if not UI.MessageBox.askyesno(parent=self, title='Overwrite?', message=f'`{destination_path}` already exists. Overwrite it?'):
				return
			if not fileutils.check_allow_overwrite_internal_file(destination_path):
				return
		try:
			config_json = self.perform_extract(destination_path)
		except PyMSError as e:
			ErrorDialog(self, e)
			return
		except Exception as e:
			if tracer := trace.get_tracer():
				tracer.trace_error()
			ErrorDialog(self, PyMSError('Extract', f"Couldn't extract `{self.mpq_file_name}`", cause=e))
			return
		config_json.update(self.mpq_config_view.config_json())
		if config_json:
			# `config_path_for` resolves against the filesystem, so the source files must already be
			# written for a folder source to get `config.json` inside it rather than beside it
			config_path = Source.config_path_for(destination_path)
			try:
				with open(config_path, 'w', encoding='utf-8') as config_file:
					json.dump(config_json, config_file, indent=4)
			except Exception as e:
				if tracer := trace.get_tracer():
					tracer.trace_error()
				ErrorDialog(self, PyMSError('Extract', f"Couldn't write `{config_path}`", cause=e))
				return
		self.extracted = True
		PyMSDialog.ok(self)

	def dismiss(self) -> None:
		self.window_geometry_config().save_size(self)
		PyMSDialog.dismiss(self)
