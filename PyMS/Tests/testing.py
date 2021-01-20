
from ..utils import isstr
from logging import *

import os, inspect


def run(tests):
	total_tests = len(tests)
	succeeded = 0
	for n,test in enumerate(tests):
		if test.run.__doc__:
			name = test.run.__doc__.split('\n')[0]
		else:
			name = 'Unknown Test'
		print '%s+ Executing test "%s" (%d/%d)' % (INDENT, name, n+1, total_tests)
		try:
			if len(inspect.getargspec(test.run).args):
				result = test.run(lambda path: os.path.abspath(os.path.join(os.path.dirname(test.__file__), path)))
			else:
				result = test.run()
			success = (result == True)
			message = ''
			if isstr(result):
				message = result
		except:
			print '%s- Test "%s" crashed:' % (INDENT*2, name)
			log_exception(INDENT*3)
		else:
			if success:
				succeeded += 1
			if message:
				message = ' (%s)' % message
			print '%s- Test group "%s" completed: %s%s' % (INDENT*2, name, 'SUCCESS' if success else 'FAIL', message)
	return (succeeded, total_tests)

def prepare(tests):
	return lambda t=tests: run(t)
