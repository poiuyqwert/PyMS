
from __future__ import annotations

from ..Project import Project

from ...Utilities import UIKit as UI
from ...Utilities.PyMSError import PyMSError

import os

# Where in the project an extracted file lands. Every extractor gets this, so the target folder and
# path rules only have to be written (and validated) once
class DestinationView(UI.LabelFrame):
	PROJECT_ROOT_NAME = '<project root>'

	def __init__(self, parent: UI.Misc, *, project: Project, mpq_file_name: str) -> None:
		UI.LabelFrame.__init__(self, parent, text='Destination')

		self.project = project
		# The project root is always offered last as a fallback, so there is a valid target even
		# before any `.mpq` folder exists
		self.roots: list[str] = [mpq_folder.path for mpq_folder in project.mpq_folders()]
		self.roots.append(project.path)

		self.root_index = UI.IntVar()
		self.sub_path = UI.StringVar()
		self.sub_path.set(DestinationView.default_sub_path(mpq_file_name))
		self.full_path = UI.StringVar()

		UI.Label(self, text='Folder:', anchor=UI.W, justify=UI.LEFT).pack(side=UI.TOP, fill=UI.X, padx=3, pady=(3,0))
		UI.DropDown(self, self.root_index, self.root_names(), self.choose_root).pack(side=UI.TOP, fill=UI.X, padx=3)
		if len(self.roots) == 1:
			UI.Label(self, text="This project has no `.mpq` folder yet, so nothing extracted into it will be packaged.", anchor=UI.W, justify=UI.LEFT).pack(side=UI.TOP, fill=UI.X, padx=3)

		UI.Label(self, text='Path:', anchor=UI.W, justify=UI.LEFT).pack(side=UI.TOP, fill=UI.X, padx=3, pady=(3,0))
		UI.Entry(self, textvariable=self.sub_path).pack(side=UI.TOP, fill=UI.X, padx=3)

		UI.Label(self, textvariable=self.full_path, anchor=UI.W, justify=UI.LEFT).pack(side=UI.TOP, fill=UI.X, padx=3, pady=(3,3))

		self.sub_path.trace_add('write', self.update_full_path)
		self.update_full_path()

	# `unit\terran\marine.grp` in the archive is `unit/terran/marine.grp` on disk, which is exactly
	# the source layout `PackageMPQ` turns back into the archive path
	@staticmethod
	def default_sub_path(mpq_file_name: str) -> str:
		components = [component for component in mpq_file_name.split('\\') if component]
		if not components:
			return ''
		return os.path.join(*components)

	def root_names(self) -> list[str]:
		names: list[str] = []
		for root in self.roots[:-1]:
			names.append(os.path.relpath(root, self.project.path))
		names.append(DestinationView.PROJECT_ROOT_NAME)
		return names

	def selected_root(self) -> str:
		return self.roots[self.root_index.get()]

	def choose_root(self, _index: int) -> None:
		self.update_full_path()

	def update_full_path(self, *_) -> None:
		try:
			# Shown relative to the project: it is the part that identifies the file, and an
			# absolute path would stretch the dialog to the width of wherever the project lives
			self.full_path.set(os.path.relpath(self.destination_path(), self.project.path))
		except PyMSError as e:
			self.full_path.set(e.error)

	def destination_path(self) -> str:
		root = self.selected_root()
		sub_path = self.sub_path.get().strip()
		if not sub_path:
			raise PyMSError('Extract', 'Enter a path for the extracted file')
		if os.path.isabs(sub_path):
			raise PyMSError('Extract', f'`{sub_path}` must be a path relative to the destination folder')
		destination_path = os.path.normpath(os.path.join(root, sub_path))
		if not os.path.basename(destination_path):
			raise PyMSError('Extract', f'`{sub_path}` does not name a file')
		relative_path = os.path.relpath(destination_path, root)
		if relative_path == os.pardir or relative_path.startswith(os.pardir + os.sep):
			raise PyMSError('Extract', f'`{sub_path}` is not inside the destination folder')
		return destination_path
