from etk11.weak_ref import GetRealObj, GetWeakProxy, GetWeakRef, IsSame, IsWeakProxy, IsWeakRef
import pytest
import weakref



#===================================================================================================
# _Stub
#===================================================================================================
class _Stub(object):

    def __eq__(self, o):
        return True  # always equal

    def __ne__(self, o):
        return not self == o



#===================================================================================================
# Test
#===================================================================================================
class Test():

    def testIsSame(self):
        s1 = _Stub()
        s2 = _Stub()

        r1 = weakref.ref(s1)
        r2 = weakref.ref(s2)

        p1 = weakref.proxy(s1)
        p2 = weakref.proxy(s2)

        assert IsSame(s1, s1)
        assert not IsSame(s1, s2)

        assert IsSame(s1, r1)
        assert IsSame(s1, p1)

        assert not IsSame(s1, r2)
        assert not IsSame(s1, p2)


        assert IsSame(p2, r2)
        assert IsSame(r1, p1)
        assert not IsSame(r1, p2)

        with pytest.raises(ReferenceError):
            IsSame(p1, p2)


    def testGetWeakRef(self):
        b = GetWeakRef(None)
        assert b() is None


    def testGeneral(self):
        class Bar(object):

            def m1(self):
                pass

            def __hash__(self):
                return 1

            def __eq__(self, o):
                return True

            def __ne__(self):
                return False

        b = Bar()
        r = GetWeakRef(b.m1)
        assert r() is not None  # should not be a regular weak ref here (but a weak method ref)

        assert IsWeakRef(r)
        assert not IsWeakProxy(r)

        r = GetWeakProxy(b.m1)
        r()
        assert IsWeakProxy(r)
        assert not IsWeakRef(r)

        r = weakref.ref(b)
        b2 = Bar()
        r2 = weakref.ref(b2)
        assert r == r2
        assert hash(r) == hash(r2)

        r = GetWeakRef(b.m1)
        r2 = GetWeakRef(b.m1)
        assert r == r2
        assert hash(r) == hash(r2)



    def testGetRealObj(self):
        class Bar(object):
            pass

        b = Bar()
        r = GetWeakRef(b)
        assert GetRealObj(r) is b

        r = GetWeakRef(None)
        assert GetRealObj(r) is None


    def testGetWeakProxyFromWeakRef(self):
        class Bar(object):
            pass

        b = Bar()
        r = GetWeakRef(b)
        proxy = GetWeakProxy(r)
        assert IsWeakProxy(proxy)
