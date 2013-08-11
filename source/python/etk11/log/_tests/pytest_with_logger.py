


class Test:

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
