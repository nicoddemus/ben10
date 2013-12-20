from ben10.foundation.odict import _GetSymbol
from ben10.foundation.pushpop import PushPopItem
import _ordereddict
import collections
import sys



#===================================================================================================
# Test
#===================================================================================================
class Test(object):

    def testOdict(self):
        assert _GetSymbol() == _ordereddict.ordereddict

        with PushPopItem(sys.modules, '_ordereddict', None):
            assert _GetSymbol() == collections.OrderedDict
