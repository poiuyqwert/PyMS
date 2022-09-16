
try:
	import Tkinter as Tk
except:
	import tkinter as Tk

# Return from event callbacks to break further processing of the event
Tk.Event.BREAK = 'break'
# Return from event callbacks to leave current processing but continue processing other bindings
Tk.Event.CONTINUE = 'continue'
