from etk11.foundation.is_frozen import SetIsFrozen
from etk11.foundation.types_ import CheckType, CheckFormatString, IsBasicType, CheckBasicType, \
    CheckEnum, _IsNumber, IsNumber, Null, Boolean, CreateDevelopmentCheckType, AsList, Flatten, \
    MergeDictsRecursively, Intersection, OrderedIntersection, CheckIsNumber
import copy
import pytest



#=======================================================================================================================
# Test
#=======================================================================================================================
class Test:

    def testBoolean(self):
        assert Boolean('TRUE') == True
        assert Boolean('true') == True
        assert Boolean('yes') == True
        assert Boolean('1') == True
        assert Boolean('false') == False
        assert Boolean('no') == False
        assert Boolean('0') == False

        with pytest.raises(ValueError):
            Boolean('INVALID')


    def testDevelopmentCheckType(self):
        was_frozen = SetIsFrozen(False)
        assert CreateDevelopmentCheckType() is CheckType

        SetIsFrozen(True)
        func = CreateDevelopmentCheckType()
        assert isinstance(func, type(lambda: None)) and func.__name__ == '<lambda>'

        SetIsFrozen(was_frozen)


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


    def testCheckIsNumber(self):
        assert CheckIsNumber(1)
        with pytest.raises(TypeError):
            CheckIsNumber('alpha')


    def testIsNumberRebinded(self):
        IsNumber(2)
        assert _IsNumber.func_code == IsNumber.func_code  # @UndefinedVariable


    class ListWithoutIter(object):
        def __init__(self, *args, **kwargs):
            self.contents = []
            for item in args:
                self.contents.append(item)
        def __len__(self):
            return len(self.contents)
        def __getitem__(self, index):
            return self.contents[index]


    def testAsList(self):
        a = [1, 2, 3]
        assert a is AsList(a)
        assert ['a'] == AsList('a')
        assert ['a'] == AsList(('a',))
        assert ['a'] == AsList(set('a'))


    def testFlatten(self):
        a = [[[1], [2]], [3]]
        assert Flatten(a) == [1, 2, 3]

        a = [1, 2, [3, 4], (5, 6)]
        assert Flatten(a) == [1, 2, 3, 4, 5, 6]


    def testFlattenOnClassWithoutIter(self):
        a = self.ListWithoutIter(self.ListWithoutIter(0, 1), 2, 3)
        assert Flatten(a) == [0, 1, 2, 3]


    def testFlattenOnClassWithoutIterForStrings(self):
        a = self.ListWithoutIter(self.ListWithoutIter("a", "bb"), "ccc")
        assert Flatten(a) == ["a", "bb", "ccc"]


    def testFlattenForStrings(self):
        a = [["a", "bb"], "ccc"]
        assert Flatten(a) == ["a", "bb", "ccc"]


    def testFlattenForUnicodeStrings(self):
        a = [[u"a", u"bb"], u"ccc"]
        assert Flatten(a) == [u"a", u"bb", u"ccc"]


    def testFlattenForTuples(self):
        a = [(0, "a"), (1, "b"), ((2, "c"), 42)]
        assert Flatten(a) == [0, "a", 1, "b", 2, "c", 42]


    def testFlattenSkipSpecificClass(self):
        obj = self.ListWithoutIter('a', 'b')
        a = [obj, 'c', ['d', 'e']]
        assert Flatten(a, skip_types=[self.ListWithoutIter]) == [obj, 'c', 'd', 'e']


    def testFlattenSkipTypeOfSubclass(self):
        class Foo(self.ListWithoutIter):
            def __init__(self, *args, **kwargs):
                super(Foo, self).__init__(*args, **kwargs)

        obj = Foo()
        a = [obj, 'c', 'd']
        assert Flatten(a, skip_types=[self.ListWithoutIter]) == [obj, 'c', 'd']


    def testMergeDictsRecursively(self):
        dict_1 = { 'a' : 1, 'b' : 2 }
        dict_2 = { 'c' : 3, 'd' : 4 }
        assert MergeDictsRecursively(dict_1, dict_2) == { 'a' : 1, 'b' : 2, 'c' : 3, 'd' : 4 }


    def testMergeDictsRecursivelyDictsOnTheRightHaveHigherPrecedence(self):
        dict_1 = { 'a' : 1, 'b' : 2 }
        dict_2 = { 'b' : 3, 'd' : 4 }
        assert MergeDictsRecursively(dict_1, dict_2) == { 'a' : 1, 'b' : 3, 'd' : 4 }


    def testMergeDictsRecursivelyManyLevelsOfRecursion(self):
        dict_1 = {
            'a' : 0,
            'b' : {
                'replaced_inner_b' : 0,
                'kept_inner_b' : 0,
            },
            'c' : {
                'inner_c' : {
                    'replaced_inner_c' : 0,
                    'kept_inner_c' : 0,
                },
            },
        }
        dict_2 = {
            'b' : {
                'replaced_inner_b' : 42,
                'added_inner_b' : 0,
            },
            'c' : {
                'inner_c' : {
                    'replaced_inner_c' : 42,
                    'added_inner_c' : 0,
                }
            }
        }
        assert (
            MergeDictsRecursively(dict_1, dict_2)
            == {
                'a' : 0,
                'b' : {
                    'kept_inner_b' : 0,
                    'replaced_inner_b' : 42,
                    'added_inner_b' : 0,
                },
                'c' : {
                    'inner_c' : {
                        'replaced_inner_c' : 42,
                        'added_inner_c' : 0,
                        'kept_inner_c' : 0,
                    }
                },
            }
        )


    def testMergeDictsRecursivelyWhenLeftHasDictKeyButRightDoesnt(self):
        dict_1 = {
            'a' : {
                'inner_a' : 0
            }
        }
        dict_2 = {
            'a' : 42
        }
        assert MergeDictsRecursively(dict_1, dict_2) == { 'a' : 42 }


    def testMergeDictsRecursivelyWhenRightHasDictKeyButLeftDoesnt(self):
        dict_1 = {
            'a' : 42
        }
        dict_2 = {
            'a' : {
                'inner_a' : 0
            }
        }
        assert (
            MergeDictsRecursively(dict_1, dict_2)
            == {
                'a' : {
                    'inner_a' : 0
                }
            }
        )


    def testMergeDictsWithWrongTypes(self):
        with pytest.raises(AttributeError):
            MergeDictsRecursively('Foo', {})

        with pytest.raises(TypeError):
            MergeDictsRecursively({}, 'Foo')

        with pytest.raises(TypeError) as excinfo:
            MergeDictsRecursively({}, 'Foo')

        assert (
            str(excinfo.value)
            == 'Wrong types passed. Expecting two dictionaries, got: "dict" and "str"'
        )


    def testIntersection(self):
        alpha = [3, 2, 1]
        bravo = [2, 3, 4]
        assert Intersection(alpha, bravo) == set([2, 3])


    def testOrderedIntersection(self):
        alpha = [1, 2, 3]
        bravo = [2, 3, 4]
        assert OrderedIntersection(alpha, bravo) == [2, 3]

        alpha = [3, 1, 2]
        bravo = [2, 3, 4]
        assert OrderedIntersection(alpha, bravo) == [3, 2]


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
