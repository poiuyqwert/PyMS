
from ..Utilities.PyMSDialog import PyMSDialog
from ..Utilities.UIKit import *
from ..Utilities import Assets

import os

class ExtractDialog(PyMSDialog):
	def __init__(self, parent, mpqhandler, settings):
		self.mpqhandler = mpqhandler
		self.search = StringVar()
		self.search.set('*')
		self.search.trace('w', self.updatesearch)
		self.settings = settings
		self.regex = IntVar()
		self.regex.set(0)
		self.files = []
		self.file = None
		self.resettimer = None
		self.searchtimer = None
		PyMSDialog.__init__(self, parent, 'Extract')

	def widgetize(self):
		self.listbox = ScrolledListbox(self, width=35, height=10)
		self.listbox.pack(fill=BOTH, padx=1, pady=1, expand=1)
		self.listbox.focus_set()

		frame = Frame(self)
		history = self.settings.extract.get('history',[])[::-1]
		self.textdrop = TextDropDown(frame, self.search, history)
		self.textdrop.entry.c = self.textdrop.entry['bg']
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

	def setup_complete(self):
		self.settings.windows.load_window_size('extract', self)

	def listfiles(self):
		def get_files_list(mpqhandler):
			files = []
			for file_entry in mpqhandler.list_files():
				if not file_entry.file_name in files:
					files.append(file_entry.file_name)
			for path,_,filenames in os.walk(Assets.mpq_dir):
				for filename in filenames:
					mpq_filename = Assets.mpq_file_path_to_file_name(os.path.join(path, filename))
					if not mpq_filename in files:
						files.append(mpq_filename)
			files.sort()
			return files
		def update_files_list(files):
			self.files = files
			self.updatelist()
		self.after_background(update_files_list, get_files_list, self.mpqhandler)

	def updatelist(self):
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

	def updatecolor(self):
		if self.resettimer:
			self.after_cancel(self.resettimer)
			self.resettimer = None
		self.textdrop.entry['bg'] = self.textdrop.entry.c

	def updatesearch(self, *_):
		if self.searchtimer:
			self.after_cancel(self.searchtimer)
		self.searchtimer = self.after(200, self.updatelist)

	def extract(self):
		pass

	def dismiss(self):
		self.settings.windows.save_window_size('extract', self)
		PyMSDialog.dismiss(self)
