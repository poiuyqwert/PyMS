
from logging import *


def do_tests(tests):
	total_tests = len(tests)
	succeeded = 0
	for n,test in enumerate(tests):
		if test.do_test.__doc__:
			name = test.do_test.__doc__.split('\n')[0]
		else:
			name = 'Unknown Test'
		print '%s+ Executing test "%s" (%d/%d)' % (INDENT, name, n+1, total_tests)
		try:
			success = (test.do_test() == True)
		except:
			print '%s- Test "%s" crashed:' % (INDENT*2, name)
			log_exception(INDENT*3)
		else:
			if success:
				succeeded += 1
			print '%s- Test group "%s" completed: %s' % (INDENT*2, name, 'SUCCESS' if success else 'FAIL')
	return (succeeded, total_tests)

def prepare(tests):
	return lambda t=tests: do_tests(t)