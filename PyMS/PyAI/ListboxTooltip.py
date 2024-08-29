
from .Delegates import TooltipDelegate

from ..FileFormats.AIBIN.AIFlag import AIFlag
from ..FileFormats import TBL

from ..Utilities.utils import fit
from ..Utilities.UIKit import *

class ListboxTooltip(Tooltip):
	def __init__(self, parent: ScrolledListbox, delegate: TooltipDelegate, font: Font | None = None, delay: int = 750, press: bool = False):
		self.scrolled_listbox = parent
		self.delegate = delegate
		Tooltip.__init__(self, parent, '', font, delay, press)
		self.index: int | None = None

	def enter(self, e: Event | None = None) -> None:
		if self.parent.size():
			self.motion(e)
			Tooltip.enter(self,e)

	def leave(self, e: Event | None = None) -> None:
		Tooltip.leave(self,e)
		if e and e.type == '4':
			self.enter(e)

	def motion(self, e: Event | None = None) -> None:
		if not e:
			return
		if self.tip and self.index != self.scrolled_listbox.nearest(e.y):
			self.leave()
			self.enter(e)
		self.pos = (e.x,e.y)
		Tooltip.motion(self, e)

	def showtip(self) -> None:
		if self.tip:
			return
		self.tip = TooltipWindow(self.parent)
		self.tip.maxsize(640,400)
		self.tip.wm_overrideredirect(True)
		pos = list(self.parent.winfo_pointerxy())
		index = self.scrolled_listbox.listbox.nearest(pos[1] - self.parent.winfo_rooty())
		ai_header = self.delegate.get_list_entry(index)
		self.index = index
		in_bwbin = 'Yes' if ai_header.is_in_bw else 'No'
		flags = ''
		for name,flag in (('BroodWar Only',AIFlag.broodwar_only),('Invisible in StarEdit',AIFlag.staredit_hidden),('Requires a Location',AIFlag.requires_location)):
			if ai_header.flags & flag:
				if flags:
					flags += ', '
				flags += name
		if flags:
			flags = f'Flags             : {flags}\n'
		text = f"Script ID         : {ai_header.id}\nIn bwscript.bin   : {in_bwbin}\n{flags}String ID         : {ai_header.string_id}\n"
		data_context = self.delegate.get_data_context()
		if (string := data_context.stattxt_string(ai_header.string_id)):
			text += fit('String            : ', string, end=True)
		# if id in ai.aiinfo and ai.aiinfo[id][0]:
		# 	text += 'Extra Information : %s' % ai.aiinfo[id][0].replace('\n','\n                    ')
		# else:
		text = text[:-1]
		frame = Frame(self.tip, background='#FFFFC8', relief=SOLID, borderwidth=1)
		Label(frame, text=text, justify=LEFT, font=self.font, fg='#000', background='#FFFFC8', relief=FLAT).pack(padx=1, pady=1)
		frame.pack()
		self.tip.wm_geometry('+%d+%d' % (pos[0],pos[1]+22))
		self.tip.update_idletasks()
		move = False
		if pos[0] + self.tip.winfo_reqwidth() > self.tip.winfo_screenwidth():
			move = True
			pos[0] = self.tip.winfo_screenwidth() - self.tip.winfo_reqwidth()
		if pos[1] + self.tip.winfo_reqheight() + 22 > self.tip.winfo_screenheight():
			move = True
			pos[1] -= self.tip.winfo_reqheight() + 44
		if move:
			self.tip.wm_geometry('+%d+%d' % (pos[0],pos[1]+22))
