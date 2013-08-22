import os
import sys

from etk11 import is_frozen
from etk11.uname import GetApplicationDir, IsRunningOn64BitMachine, GetUserHomeDir


#=======================================================================================================================
# Test
#=======================================================================================================================
class Test():

    def testIsRunningOn64BitMachine(self):
        assert IsRunningOn64BitMachine


    def testGetUserHomeDir(self):
        assert GetUserHomeDir() == '%(HOMEDRIVE)s%(HOMEPATH)s' % os.environ


    def testGetApplicationDir(self):
        # When in development...
        is_frozen_ = is_frozen.SetIsFrozen(False)
        assert GetApplicationDir() == sys.path[0]

        # When in a executable...
        is_frozen.SetIsFrozen(True)
        assert GetApplicationDir() == os.path.dirname(os.path.dirname(sys.executable))

        # Restore
        is_frozen.SetIsFrozen(is_frozen_)
