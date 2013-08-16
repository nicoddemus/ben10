import copy

from etk11.null import Null


pytest_plugins = ["etk11.fixtures"]


#=======================================================================================================================
# Test
#=======================================================================================================================
class Test():

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


    def testCopy(self):
        n = Null()
        n1 = copy.copy(n)
        assert str(n) == str(n1)
