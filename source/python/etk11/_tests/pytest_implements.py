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
                pass

        assert IFoo.Foo.__doc__ == Impl.Foo.__doc__


    def CreateClass(self):

        class IFoo(object):

            def DoIt(self):
                pass

        class Implementation(object):

            @Implements(IFoo.DoIt)
            def DoNotDoIt(self):
                pass
