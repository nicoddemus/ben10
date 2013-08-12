import pytest

from etk11.implements import Implements


#=======================================================================================================================
# Test
#=======================================================================================================================
class Test:

    def testErrorDifferentFunction(self):
        with pytest.raises(AssertionError):
            self.CreateClass()

        class IFoo(object):
            def Foo(self):
                '''
                docstring
                '''

        class Impl(object):

            @Implements(IFoo.Foo)
            def Foo(self):
                return self.__class__.__name__

        assert IFoo.Foo.__doc__ == Impl.Foo.__doc__

        # Just for 100% coverage.
        assert Impl().Foo() == 'Impl'


    def CreateClass(self):

        class IFoo(object):

            def DoIt(self):
                ''

        class Implementation(object):

            @Implements(IFoo.DoIt)
            def DoNotDoIt(self):
                ''
