
import GRP

groups = [
	GRP
]

from logging import *


def run():
	total_groups = len(groups)
	for n,group in enumerate(groups):
		name = group.__name__
		print '+ Executing test group "%s" (%d/%d)' % (name, n+1, total_groups)
		try:
			succeeded,total = group.do_tests()
		except:
			print '%s- Test group "%s" crashed:' % (INDENT, name)
			log_exception(INDENT)
		else:
			print '%s- Test group "%s" completed: %d/%d succeeded' % (INDENT, name, succeeded, total)
