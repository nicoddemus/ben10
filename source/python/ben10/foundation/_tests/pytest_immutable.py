from copy import copy, deepcopy
from ben10.foundation.immutable import AsImmutable
import pytest



#=======================================================================================================================
# Test
#=======================================================================================================================
class Test:

    def testImmutable(self):
        assert AsImmutable(1) == 1

        d = AsImmutable(dict(a=1, b=dict(b=2)))
        assert d == {'a': 1, 'b': {'b': 2}}
        with pytest.raises(NotImplementedError):
            d.__setitem__('a', 2)

        assert d['b'].AsMutable() == dict(b=2)
        AsImmutable(d, return_str_if_not_expected=False)
        d = d.AsMutable()
        d['a'] = 2

        c = deepcopy(d)
        assert c == d

        c = copy(d)
        assert c == d

        assert AsImmutable(([1, 2], [2, 3])) == ((1, 2), (2, 3))
        assert AsImmutable(None) is None
        assert isinstance(AsImmutable(set([1, 2, 4])), frozenset)
        assert isinstance(AsImmutable(frozenset([1, 2, 4])), frozenset)
        assert isinstance(AsImmutable([1, 2, 4]), tuple)
        assert isinstance(AsImmutable((1, 2, 4)), tuple)

