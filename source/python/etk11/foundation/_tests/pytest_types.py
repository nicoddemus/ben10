import pytest

import copy
from etk11.foundation.types_ import CheckType, CheckFormatString, IsBasicType, CheckBasicType, CheckEnum, _IsNumber, \
    IsNumber, Null


#=======================================================================================================================
# Test
#=======================================================================================================================
class Test:

    def testPassing(self):
        # self.failIfRaises TypeError
        CheckType('hellou', str)

        # self.failIfRaises TypeError,
        CheckType('hellou', (int, str))

        # self.failIfRaises TypeError,
        CheckType(99, (int, str))


    def testRaising(self):
        with pytest.raises(TypeError):
            CheckType('hellou', int)

        with pytest.raises(TypeError):
            CheckType('hellou', (int, float))

        with pytest.raises(TypeError):
            CheckType(99, (str, float))


    def testCheckFormatString(self):
        CheckFormatString('%s', 1)
        CheckFormatString('%s m', 1)

        with pytest.raises(ValueError):
            CheckFormatString('%s m %s', 1)

        with pytest.raises(ValueError):
            CheckFormatString('%s m %s', 1, 3, 3)


    def testBasicType(self):
        assert IsBasicType(1)
        assert IsBasicType(1L)
        assert not IsBasicType([1])
        assert IsBasicType([1], accept_compound=True)
        assert IsBasicType({1: [1]}, accept_compound=True)
        assert IsBasicType({1: set([1])}, accept_compound=True)
        assert IsBasicType(frozenset([1L, 2]), accept_compound=True)
        with pytest.raises(TypeError):
            CheckBasicType([0])


    def testCheckEnum(self):
        for i in xrange(10):
            # self.assertNotRaises(ValueError,
            CheckEnum(i, range(10))

        with pytest.raises(ValueError):
            CheckEnum(-1, range(10))
        with pytest.raises(ValueError):
            CheckEnum(11, range(10))
        with pytest.raises(ValueError):
            CheckEnum('foo', range(10))


    def testCheckNumber(self):
        import numpy as np

        for number_class in [int, float, long]:
            converted = number_class(1)

            assert IsNumber(converted)

        # Checking numpy numbers
        collection = np.zeros(1, np.float32)
        assert IsNumber(collection[0])


    def testIsNumberRebinded(self):
        IsNumber(2)
        assert _IsNumber.func_code == IsNumber.func_code  # @UndefinedVariable


    def testNull(self):
        # constructing and calling

        dummy = Null()
        dummy = Null('value')
        n = Null('value', param='value')

        n()
        n('value')
        n('value', param='value')

        # attribute handling
        n.attr1
        n.attr1.attr2
        n.method1()
        n.method1().method2()
        n.method('value')
        n.method(param='value')
        n.method('value', param='value')
        n.attr1.method1()
        n.method1().attr1

        n.attr1 = 'value'
        n.attr1.attr2 = 'value'

        del n.attr1
        del n.attr1.attr2.attr3

        # Iteration
        for i in n:
            'Not executed'

        # representation and conversion to a string
        assert repr(n) == '<Null>'
        assert str(n) == 'Null'

        # truth value
        assert bool(n) == False
        assert bool(n.foo()) == False

        dummy = Null()
        assert dummy.__name__ == 'Null'  # Name should return a string.

        # Null objects are always equal to other null object
        assert n != 1
        assert n == dummy


    def testNullCopy(self):
        n = Null()
        n1 = copy.copy(n)
        assert str(n) == str(n1)
