
from .gapy.ga import *
from . import Assets
from .PyMSConfig import PYMS_CONFIG

ga.set_tracking_id(PYMS_CONFIG.analytics.tid.value)
cid = ga.set_client_id(PYMS_CONFIG.analytics.cid.value)
ga.Custom.register(1, 'PYMS_VERSION')
ga.Custom.register(2, 'PYTHON_VERSION')
ga.Custom.register(3, 'OS_NAME')
ga.Custom.register(4, 'OS_VERSION')
ga.Custom.register(5, 'OS_BITS')
ga[ga.Custom.PYMS_VERSION] = Assets.version('PyMS')
ga[ga.Custom.PYTHON_VERSION] = platform.python_version()
ga[ga.Custom.OS_NAME] = GATarget.os_name()
ga[ga.Custom.OS_VERSION] = GATarget.os_version()
ga[ga.Custom.OS_BITS] = GATarget.os_bits()

ga.enabled = PYMS_CONFIG.analytics.allow.value

if cid != PYMS_CONFIG.analytics.cid.value:
	PYMS_CONFIG.analytics.cid.value = cid
	PYMS_CONFIG.save()
