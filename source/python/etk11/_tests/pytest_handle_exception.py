import sys

import pytest

from etk11 import handle_exception


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

    def testHandleException(self, exception_handler, capfd):
        try:
            raise RuntimeError()
        except:
            handle_exception.HandleException('Test')
        assert len(exception_handler.exceptions) == 1

        assert capfd.readouterr() == [
            u'',
            u'''Traceback (most recent call last):
  File "x:\\etk11\\source\\python\\etk11\\_tests\\pytest_handle_exception.py", line 46, in testHandleException
    raise RuntimeError()
RuntimeError
''',
        ]


    def testIgnoreHandleException(self, exception_handler, capfd):
        handle_exception.StartIgnoreHandleException()
        try:
            try:
                raise RuntimeError()
            except:
                handle_exception.HandleException('Test')
            assert len(exception_handler.exceptions) == 1
        finally:
            handle_exception.EndIgnoreHandleException()

        assert capfd.readouterr() == [u'', u'', ]
