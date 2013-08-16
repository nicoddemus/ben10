import pytest

from etk11.lru import LRU, LRUWithRemovalMemo, _Node


#=======================================================================================================================
# Test
#=======================================================================================================================
class Test:

    def testLRU(self):

        with pytest.raises(ValueError):
            lru = LRU(-1)

        lru = LRU(2)

        def CheckLru():
            lru[1] = 1
            lru[2] = 2
            lru[3] = 3

            assert 1 not in lru
            assert 2 in lru
            assert 3 in lru

            assert 2 == len(lru)
            assert lru.keys() == [2, 3]
            assert lru.values() == [2, 3]

            lru[2] = 2
            lru[1] = 1
            assert lru.values() == [2, 1]

            # Iterates from the used in the last access to others based on access time.
            assert [(2, 2), (1, 1)] == list(lru.iteritems())
            lru[2] = 2
            assert [(1, 1), (2, 2)] == list(lru.iteritems())

            del lru[2]
            assert [(1, 1), ] == list(lru.iteritems())

            lru[2] = 2
            assert [(1, 1), (2, 2)] == list(lru.iteritems())

            _a = lru[1]
            assert [(2, 2), (1, 1)] == list(lru.iteritems())

            _a = lru[2]
            assert [(1, 1), (2, 2)] == list(lru.iteritems())

            assert lru.get(2) == 2
            assert lru.get(3) == None
            assert [(1, 1), (2, 2)] == list(lru.iteritems())

            lru.clear()
            assert [] == list(lru.iteritems())

        CheckLru()

        # Check it twice (because the last thing we do is clearing it, so, did it work?)
        CheckLru()


    def testLRUWithRemovalMemo(self):
        lru = LRUWithRemovalMemo(2)
        lru[1] = 1
        assert lru.GetAndClearRemovedItems() == []
        lru[2] = 2
        assert lru.GetAndClearRemovedItems() == []
        lru[2] = 3  # Just replace the item (it was not removed)
        assert lru.GetAndClearRemovedItems() == []
        lru[4] = 4
        assert lru.GetAndClearRemovedItems() == [1]
        assert lru.GetAndClearRemovedItems() == []

        del lru[4]
        assert lru.GetAndClearRemovedItems() == [4]
        assert lru.GetAndClearRemovedItems() == []

        assert len(lru) == 1
        lru.clear()
        assert lru.GetAndClearRemovedItems() == []


    def testNode(self):
        a = _Node(1, 'one', 1)
        b = _Node(2, 'two', 2)
        assert a < b
        assert b > a

        c = _Node(3, 'three', 2)
        assert b == c

        assert repr(a) == '_Node(time=1)'


#     def profile(self):
#         @ProfileMethod('test.prof')
#         def Check():
#             lru = LRU(50)
#             for i in xrange(300000):
#                 lru[i % 50] = i
#
#             for i in xrange(300000):
#                 _a = lru[i % 50]
#
#
#             for i in xrange(5000):
#                 for _key in lru.iterkeys():
#                     pass
#
#         Check()
#         PrintProfile('test.prof')


