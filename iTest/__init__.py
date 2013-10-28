# -*- coding: utf-8 -*-
#


__docformat__ = 'restructuredtext en'
try:
    __version__ = __import__('pkg_resources').get_distribution('Bitten').version
except:
    try:
        __version__ = __import__('pkg_resources').get_distribution(
                                                    'BittenSlave').version
    except:
        pass

# The master-slave protocol/configuration version
PROTOCOL_VERSION = 2
