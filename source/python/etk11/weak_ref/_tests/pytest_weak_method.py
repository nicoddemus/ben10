from etk11.weak_ref import WeakMethodRef, WeakMethodProxy, ReferenceError
import pytest
import sys



#===================================================================================================
# Test
#===================================================================================================
class Test():

    def SetupTestAttributes(self):

        class C:
            def f(self, y=0):
                return self.x + y

        class D(object):
            def f(self):
                pass

        self.C = C
        self.c = C()
        self.c.x = 1
        self.d = D()


    def testRefcount(self):
        self.SetupTestAttributes()

        assert sys.getrefcount(self.c) == 2  # 2: one in self, and one as argument to getrefcount()
        cf = self.c.f
        assert sys.getrefcount(self.c) == 3  # 3: as above, plus cf
        rf = WeakMethodRef(self.c.f)
        pf = WeakMethodProxy(self.c.f)
        assert sys.getrefcount(self.c) == 3
        del cf
        assert sys.getrefcount(self.c) == 2
        rf2 = WeakMethodRef(self.c.f)
        assert sys.getrefcount(self.c) == 2
        del rf
        del rf2
        del pf
        assert sys.getrefcount(self.c) == 2


    def testDies(self):
        self.SetupTestAttributes()

        rf = WeakMethodRef(self.c.f)
        pf = WeakMethodProxy(self.c.f)
        assert not rf.is_dead()
        assert not pf.is_dead()
        assert rf()() == 1
        assert pf(2) == 3
        self.c = None
        assert rf.is_dead()
        assert pf.is_dead()
        assert rf() == None
        with pytest.raises(ReferenceError):
            pf()


    def testWorksWithFunctions(self):
        self.SetupTestAttributes()

        def foo(y):
            return y + 1
        rf = WeakMethodRef(foo)
        pf = WeakMethodProxy(foo)
        assert foo(1) == 2
        assert rf()(1) == 2
        assert pf(1) == 2
        assert not rf.is_dead()
        assert not pf.is_dead()


    def testWorksWithUnboundMethods(self):
        self.SetupTestAttributes()

        meth = self.C.f
        rf = WeakMethodRef(meth)
        pf = WeakMethodProxy(meth)
        assert meth(self.c) == 1
        assert rf()(self.c) == 1
        assert pf(self.c) == 1
        assert not rf.is_dead()
        assert not pf.is_dead()


    def testEq(self):
        self.SetupTestAttributes()

        rf1 = WeakMethodRef(self.c.f)
        rf2 = WeakMethodRef(self.c.f)
        assert rf1 == rf2
        rf3 = WeakMethodRef(self.d.f)
        assert rf1 != rf3
        del self.c
        assert rf1.is_dead()
        assert rf2.is_dead()
        assert rf1 == rf2


    def testProxyEq(self):
        self.SetupTestAttributes()

        pf1 = WeakMethodProxy(self.c.f)
        pf2 = WeakMethodProxy(self.c.f)
        pf3 = WeakMethodProxy(self.d.f)
        assert pf1 == pf2
        assert pf3 != pf2
        del self.c
        assert pf1 == pf2
        assert pf1.is_dead()
        assert pf2.is_dead()


    def testHash(self):
        self.SetupTestAttributes()

        r = WeakMethodRef(self.c.f)
        r2 = WeakMethodRef(self.c.f)
        assert r == r2
        h = hash(r)
        assert hash(r) == hash(r2)
        del self.c
        assert r() is None
        assert hash(r) == h


    def testRepr(self):
        self.SetupTestAttributes()

        r = WeakMethodRef(self.c.f)
        assert str(r)[:33] == '<WeakMethodRef to C.f for object '

        def Foo():
            pass

        r = WeakMethodRef(Foo)
        assert str(r) == '<WeakMethodRef to Foo>'
