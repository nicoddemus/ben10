from ben10.fixtures import SkipIfImportError
from ben10.foundation.odict import _GetSymbol, _OrderedDict
from ben10.foundation.pushpop import PushPopItem
import sys



#===================================================================================================
# Test
#===================================================================================================
class Test(object):

    @SkipIfImportError('_ordereddict')
    def testOdict(self):
        import _ordereddict
        assert _GetSymbol() == _ordereddict.ordereddict

        with PushPopItem(sys.modules, '_ordereddict', None):
            assert _GetSymbol() == _OrderedDict


    @SkipIfImportError('_ordereddict')
    def testInsertOnC(self):
        import _ordereddict
        d = _ordereddict.ordereddict()
        d[1] = 'alpha'
        d[3] = 'charlie'

        assert d.items() == [(1, 'alpha'), (3, 'charlie')]

        d.insert(0, 0, 'ZERO')
        assert d.items() == [(0, 'ZERO'), (1, 'alpha'), (3, 'charlie')]

        d.insert(2, 2, 'bravo')
        assert d.items() == [(0, 'ZERO'), (1, 'alpha'), (2, 'bravo'), (3, 'charlie')]

        d.insert(99, 4, 'echo')
        assert d.items() == [(0, 'ZERO'), (1, 'alpha'), (2, 'bravo'), (3, 'charlie'), (4, 'echo')]


    def testInsertOnPython(self):
        d = _OrderedDict()
        d[1] = 'alpha'
        d[3] = 'charlie'

        assert d.items() == [(1, 'alpha'), (3, 'charlie')]

        d.insert(0, 0, 'ZERO')
        assert d.items() == [(0, 'ZERO'), (1, 'alpha'), (3, 'charlie')]

        d.insert(2, 2, 'bravo')
        assert d.items() == [(0, 'ZERO'), (1, 'alpha'), (2, 'bravo'), (3, 'charlie')]

        d.insert(99, 4, 'echo')
        assert d.items() == [(0, 'ZERO'), (1, 'alpha'), (2, 'bravo'), (3, 'charlie'), (4, 'echo')]
