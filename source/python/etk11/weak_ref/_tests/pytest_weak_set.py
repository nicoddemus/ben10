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

    def AssertEqual(self, a, b):
        '''
        Avoiding using "assert a == b" because it adds another reference to the ref-count.
        '''
        if a == b:
            pass
        else:
            assert False, "%s != %s" % (a, b)

    def testWeakSet(self):
        weak_set = WeakSet()
        s1 = _Stub()
        s2 = _Stub()

        weak_set.add(s1)
        assert isinstance(iter(weak_set).next(), _Stub)

        assert s1 in weak_set
        self.AssertEqual(len(weak_set), 1)
        del s1
        self.AssertEqual(len(weak_set), 0)

#         weak_set.add(s2)
#         self.AssertEqual(len(weak_set), 1)
#         weak_set.remove(s2)
#         self.AssertEqual(len(weak_set), 0)
#
#         weak_set.add(s2)
#         weak_set.clear()
#         self.AssertEqual(len(weak_set), 0)
#
#         weak_set.add(s2)
#         weak_set.add(s2)
#         weak_set.add(s2)
#         self.AssertEqual(len(weak_set), 1)
#         del s2
#         self.AssertEqual(len(weak_set), 0)
#
#         # >>> Testing with FUNCTION
#
#         # Adding twice, having one
#         def function():
#             pass
#         weak_set.add(function)
#         weak_set.add(function)
#         self.AssertEqual(len(weak_set), 1)


    def testRemove(self):
        weak_set = WeakSet()

        s1 = _Stub()

        self.AssertEqual(len(weak_set), 0)

        # Trying remove, raises KeyError
        with pytest.raises(KeyError):
            weak_set.remove(s1)
        self.AssertEqual(len(weak_set), 0)

        # Trying discard, no exception raised
        weak_set.discard(s1)
        self.AssertEqual(len(weak_set), 0)


    def testWeakSet2(self):
        weak_set = WeakSet()

        # >>> Removing with DEL
        s1 = _Stub()
        weak_set.add(s1.Method)
        self.AssertEqual(len(weak_set), 1)
        del s1
        self.AssertEqual(len(weak_set), 0)

        # >>> Removing with REMOVE
        s2 = _Stub()
        weak_set.add(s2.Method)
        self.AssertEqual(len(weak_set), 1)
        weak_set.remove(s2.Method)
        self.AssertEqual(len(weak_set), 0)


    def testWithError(self):
        weak_set = WeakSet()

        # Not WITH, everything ok
        s1 = _Stub()
        weak_set.add(s1.Method)
        self.AssertEqual(len(weak_set), 1)
        del s1
        self.AssertEqual(len(weak_set), 0)

        # Using WITH, s2 is not deleted from weak_set
        s2 = _Stub()
        with pytest.raises(KeyError):
            raise KeyError('key')
        self.AssertEqual(len(weak_set), 0)

        weak_set.add(s2.Method)
        self.AssertEqual(len(weak_set), 1)
        del s2
        self.AssertEqual(len(weak_set), 1)  # <-- This should be ZERO!


    def testFunction(self):
        weak_set = WeakSet()

        def function():
            pass

        # Adding twice, having one.
        weak_set.add(function)
        weak_set.add(function)
        self.AssertEqual(len(weak_set), 1)

        # Removing function
        weak_set.remove(function)
        assert len(weak_set) == 0
