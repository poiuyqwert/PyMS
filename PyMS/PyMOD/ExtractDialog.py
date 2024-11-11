
from .Config import PyMODConfig

from ..Utilities.PyMSDialog import PyMSDialog
from ..Utilities.UIKit import *
from ..Utilities import Assets
from ..Utilities.MPQHandler import MPQHandler

import os

class ExtractDialog(PyMSDialog):
	def __init__(self, parent: Misc, mpqhandler: MPQHandler, config: PyMODConfig) -> None:
		self.mpqhandler = mpqhandler
		self.search = StringVar()
		self.search.set('*')
		self.search.trace('w', self.updatesearch)
		self.config_ = config
		self.regex = IntVar()
		self.regex.set(0)
		self.files: list[str] = []
		self.resettimer: str | None = None
		self.searchtimer: str | None = None
		PyMSDialog.__init__(self, parent, 'Extract')

	def widgetize(self) -> Widget:
		self.listbox = ScrolledListbox(self, width=35, height=10)
		self.listbox.pack(fill=BOTH, padx=1, pady=1, expand=1)
		self.listbox.focus_set()

		frame = Frame(self)
		self.textdrop = TextDropDown(frame, self.search, self.config_.extract.history.data)
		self.textdrop_entry_c = self.textdrop.entry['bg']
		self.textdrop.pack(side=LEFT, fill=X, padx=1, pady=2)
		Radiobutton(frame, text='Wildcard', variable=self.regex, value=0, command=self.updatelist).pack(side=LEFT, padx=1, pady=2)
		Radiobutton(frame, text='Regex', variable=self.regex, value=1, command=self.updatelist).pack(side=LEFT, padx=1, pady=2)
		frame.pack(fill=X)

		frame = Frame(self)
		self.extract_button = Button(frame, text='Extract', width=10, command=self.extract)
		self.extract_button.pack(side=LEFT, padx=1, pady=3)
		Button(frame, text='Done', width=10, command=self.cancel).pack(side=LEFT, padx=1, pady=3)
		frame.pack(side=BOTTOM)

		self.listfiles()

		return self.extract_button

	def setup_complete(self) -> None:
		self.config_.windows.extract.load_size(self)

	def listfiles(self) -> None:
		def get_files_list(mpqhandler: MPQHandler) -> list[str]:
			files: list[str] = []
			for file_entry in mpqhandler.list_files():
				if not file_entry.file_name in files:
					files.append(file_entry.file_name.decode('utf-8'))
			for path,_,filenames in os.walk(Assets.mpq_dir):
				for filename in filenames:
					mpq_filename = Assets.mpq_file_path_to_file_name(os.path.join(path, filename))
					if not mpq_filename in files:
						files.append(mpq_filename)
			files.sort()
			return files
		def update_files_list(files: list[str] | Exception | None) -> None:
			# TODO: Exception or None cases?
			if not isinstance(files, list):
				return
			self.files = files
			self.updatelist()
		self.after_background(update_files_list, get_files_list, self.mpqhandler)

	def updatelist(self) -> None:
		if self.searchtimer:
			self.after_cancel(self.searchtimer)
			self.searchtimer = None
		self.listbox.delete(0,END)
		s = self.search.get()
		if not self.regex.get():
			s = '^' + re.escape(s).replace('\\?','.').replace('\\*','.+?') + '$'
		try:
			r = re.compile(s)
		except:
			self.resettimer = self.after(1000, self.updatecolor)
			self.textdrop.entry['bg'] = '#FFB4B4'
		else:
			for f in filter(lambda p: r.match(p), self.files):
				self.listbox.insert(END,f)
		if self.listbox.size():
			self.listbox.select_set(0)
			self.extract_button['state'] = NORMAL
		else:
			self.extract_button['state'] = DISABLED

	def updatecolor(self) -> None:
		if self.resettimer:
			self.after_cancel(self.resettimer)
			self.resettimer = None
		self.textdrop.entry['bg'] = self.textdrop_entry_c

	def updatesearch(self, *_) -> None:
		if self.searchtimer:
			self.after_cancel(self.searchtimer)
		self.searchtimer = self.after(200, self.updatelist)

	def extract(self) -> None:
		pass

	def dismiss(self) -> None:
		self.config_.windows.extract.save_size(self)
		PyMSDialog.dismiss(self)
