from StringIO import StringIO
from etk11 import log
import sys


#=======================================================================================================================
# Test
#=======================================================================================================================
class Test():

    def testHandlers(self):
        stream = StringIO()
        original = sys.stderr
        null_handler = log.NullHandler()
        try:
            sys.stderr = stream

            logger = log.GetLogger('test_handler')
            logger.Error('Test')

            logger.AddHandler(null_handler)
            logger.Error('Test2')
        finally:
            logger.RemoveHandler(null_handler)
            sys.stderr = original

        # Change: No handlers could be found for logger "test_handler" is not logged
        # as we now add a NullHandler by default (in which case that warning won't appear
        # and a StreamHandler won't be automatically created!)
        assert stream.getvalue().strip() == ''


    def testWithLogger(self):
        contents = '''
from __future__ import with_statement
from etk11.log import StartLogging, GetLogger
with StartLogging() as logger:
    GetLogger('').Warn('something')
    assert 'something' in logger.GetRecordedLog()
    assert 'something' in logger.GetRecordedLog()
'''
        code = compile(contents, '<string>', 'exec')