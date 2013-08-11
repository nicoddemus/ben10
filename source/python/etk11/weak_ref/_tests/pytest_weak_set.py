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

        def AssertEqual(a, b):
            '''
            Avoiding using "assert a == b" because it adds another reference to the ref-count.
            '''
            if a == b:
                pass
            else:
                assert False, "%s != %s" % (a, b)

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

        # >>> Testing with FUNCTION

        # Adding twice, having one
        def function():
            pass
        weak_set.add(function)
        weak_set.add(function)
        assert len(weak_set) == 1

        s1 = _Stub()
        s2 = _Stub()
        # Trying remove, raises KeyError
        with pytest.raises(KeyError):
            weak_set.remove(s1)
        # Trying discard, no exception raised
        weak_set.discard(s1)

        # Removing function
        weak_set.remove(function)
        assert len(weak_set) == 0

        # >>> Testing with METHOD

        weak_set.add(s1.Method)
        assert len(weak_set) == 1
        del s1
        AssertEqual(len(weak_set), 0)

        weak_set.add(s2.Method)
        AssertEqual(len(weak_set), 1)
        weak_set.remove(s2.Method)
        AssertEqual(len(weak_set), 0)
