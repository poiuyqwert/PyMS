
import sys, traceback


INDENT = '  '

def log_exception(indent):
	print indent + ''.join(l.replace('\n', '\n' + indent) for l in traceback.format_exception(*sys.exc_info()))
