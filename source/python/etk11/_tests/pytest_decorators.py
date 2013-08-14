import pytest

from etk11.decorators import Implements, Override


#=======================================================================================================================
# Test
#=======================================================================================================================
class Test():

    def testImplements(self):
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


    def testOverride(self):

        def TestOK():

            class A(object):

                def Method(self):
                    '''
                    docstring
                    '''


            class B(A):

                @Override(A.Method)
                def Method(self):
                    return 2

            b = B()
            assert b.Method() == 2
            assert A.Method.__doc__ == B.Method.__doc__


        def TestERROR():

            class A(object):

                def MyMethod(self):
                    ''


            class B(A):

                @Override(A.Method)  # it will raise an error at this point
                def Method(self):
                    ''

        def TestNoMatch():

            class A(object):

                def Method(self):
                    ''


            class B(A):

                @Override(A.Method)
                def MethodNoMatch(self):
                    ''


        TestOK()
        with pytest.raises(AttributeError):
            TestERROR()

        with pytest.raises(AssertionError):
            TestNoMatch()
