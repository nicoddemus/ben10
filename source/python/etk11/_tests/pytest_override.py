from etk11.override import Override
import pytest



#===================================================================================================
# Test
#===================================================================================================
class Test():

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
