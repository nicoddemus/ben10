from etk11.weak_ref import WeakList
import pytest
import weakref



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

    def testWeakList(self):
        weak_list = WeakList()
        s1 = _Stub()
        s2 = _Stub()

        weak_list.append(s1)
        assert isinstance(weak_list[0], _Stub)

        assert s1 in weak_list
        assert 1 == len(weak_list)
        del s1
        assert 0 == len(weak_list)

        weak_list.append(s2)
        assert 1 == len(weak_list)
        weak_list.remove(s2)
        assert 0 == len(weak_list)

        weak_list.append(s2)
        del weak_list[:]
        assert 0 == len(weak_list)

        weak_list.append(s2)
        del s2
        del weak_list[:]
        assert 0 == len(weak_list)

        s1 = _Stub()
        weak_list.append(s1)
        assert 1 == len(weak_list[:])

        del s1

        assert 0 == len(weak_list[:])

        def m1():
            pass

        weak_list.append(m1)
        assert 1 == len(weak_list[:])
        del m1
        assert 0 == len(weak_list[:])

        s = _Stub()
        weak_list.append(s.Method)
        assert 1 == len(weak_list[:])
        s = weakref.ref(s)
        assert 0 == len(weak_list[:])
        assert s() is None

        s0 = _Stub()
        s1 = _Stub()
        weak_list.extend([s0, s1])
        assert len(weak_list) == 2


    def testSetItem(self):
        weak_list = WeakList()
        s1 = _Stub()
        s2 = _Stub()
        weak_list.append(s1)
        weak_list.append(s1)
        assert s1 == weak_list[0]
        weak_list[0] = s2
        assert s2 == weak_list[0]
