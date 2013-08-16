from etk11 import handle_exception
from etk11.pushpop import PushPop
import pytest
import sys




#=======================================================================================================================
# exception_handler
#=======================================================================================================================
@pytest.fixture
def exception_handler(request):
    '''
    Captures the exceptions using handle_exception module.
    
    This code was in coilib50's base TestCase.
    '''

    class Handler():

        def __init__(self):
            self.exceptions = []
            handle_exception.on_exception_handled.Register(self._OnHandledException)

        def Finalizer(self):
            self.exceptions = []
            handle_exception.on_exception_handled.Unregister(self._OnHandledException)

        def _OnHandledException(self):
            info = sys.exc_info()
            self.exceptions.append(info)

    result = Handler()
    request.addfinalizer(result.Finalizer)
    return result



#=======================================================================================================================
# Test
#=======================================================================================================================
class Test():

    def testHandleException(self, exception_handler):
        from StringIO import StringIO

        with PushPop(sys, 'stderr', StringIO()) as output:
            try:
                raise RuntimeError()
            except:
                handle_exception.HandleException('Test')
            assert len(exception_handler.exceptions) == 1

#         assert output.getvalue() == '''Traceback (most recent call last):
#   File "x:\etk11\source\python\etk11\debug\_tests\pytest_handle_exception.py", line 64, in testHandleException
#     raise RuntimeError()
# RuntimeError'''
