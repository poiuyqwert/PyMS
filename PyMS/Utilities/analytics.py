
from .gapy.ga import GAScreen, GATarget, ga
from . import Assets
from .PyMSConfig import PYMS_CONFIG

import platform

# TODO: Update analytics
ga.set_tracking_id(PYMS_CONFIG.analytics.tid.value or '')
cid = ga.set_client_id(PYMS_CONFIG.analytics.cid.value)
PYMS_VERSION = ga.Custom.register(1, 'PYMS_VERSION')
PYTHON_VERSION = ga.Custom.register(2, 'PYTHON_VERSION')
OS_NAME = ga.Custom.register(3, 'OS_NAME')
OS_VERSION = ga.Custom.register(4, 'OS_VERSION')
OS_BITS = ga.Custom.register(5, 'OS_BITS')
ga[PYMS_VERSION] = Assets.version('PyMS')
ga[PYTHON_VERSION] = platform.python_version()
ga[OS_NAME] = GATarget.os_name()
ga[OS_VERSION] = GATarget.os_version()
ga[OS_BITS] = GATarget.os_bits()

ga.enabled = PYMS_CONFIG.analytics.allow.value

if cid != PYMS_CONFIG.analytics.cid.value:
	PYMS_CONFIG.analytics.cid.value = cid
	PYMS_CONFIG.save()
