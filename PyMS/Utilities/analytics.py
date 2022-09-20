
from gapy.ga import *
from . import Assets
from setutils import PYMS_SETTINGS

ga.set_tracking_id(PYMS_SETTINGS.analytics.get('tid', 'UA-42320973-2', autosave=False))
PYMS_SETTINGS.analytics.cid = ga.set_client_id(PYMS_SETTINGS.analytics.get('cid', autosave=False))
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

ga.enabled = PYMS_SETTINGS.analytics.get('allow', True)
PYMS_SETTINGS.save()