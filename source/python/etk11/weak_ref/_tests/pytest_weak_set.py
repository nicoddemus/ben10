from etk11.weak_ref import WeakSet
import pytest



#===================================================================================================
# _Stub
#===================================================================================================
class _Stub(object):
    def Method(self):
        pass



#===================================================================================================
# Test
#===================================================================================================
class Test():

    def testWeakSet(self):
        weak_set = WeakSet()
        s1 = _Stub()
        s2 = _Stub()

        weak_set.add(s1)
        assert isinstance(iter(weak_set).next(), _Stub)

        assert s1 in weak_set
        assert len(weak_set) == 1
        del s1
        assert len(weak_set) == 0

        weak_set.add(s2)
        assert len(weak_set) == 1
        weak_set.remove(s2)
        assert len(weak_set) == 0

        weak_set.add(s2)
        weak_set.clear()
        assert len(weak_set) == 0

        weak_set.add(s2)
        weak_set.add(s2)
        weak_set.add(s2)
        assert len(weak_set) == 1
        del s2
        assert len(weak_set) == 0

        def method():
            pass
        weak_set.add(method)
        weak_set.add(method)
        assert len(weak_set) == 1

        s1 = _Stub()
        s2 = _Stub()
        with pytest.raises(KeyError):
            weak_set.remove(s1)
        weak_set.discard(s1)

        weak_set.remove(method)
        assert len(weak_set) == 0

        weak_set.add(s1.Method)
        assert len(weak_set) == 1
        del s1
        assert len(weak_set) == 0

        weak_set.add(s2.Method)
        assert len(weak_set) == 1
        weak_set.remove(s2.Method)
        assert len(weak_set) == 0
