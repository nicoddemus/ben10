import contextlib



#===================================================================================================
# CaptureStd
#===================================================================================================
@contextlib.contextmanager
def CaptureStd():
    '''
    Context manager used to capture stdout and stderr.
    
    e.g.
        with CaptureStd() as output:
            print 'hey'
            
        repr(output.stdout) == 'hey\n'
        repr(output.stderr) == ''
        
    @note:
        This replaces some older code that fiddled around with file descriptions, using os.dup2
    '''
    class CapturedOutput(object):
        def __init__(self):
            from cStringIO import StringIO
            self._stdout = StringIO()
            self._stderr = StringIO()

        @property
        def stdout(self):
            return self._stdout.getvalue()

        @property
        def stderr(self):
            return self._stderr.getvalue()


    import sys
    oldout, olderr = sys.stdout, sys.stderr
    try:
        output = CapturedOutput()

        sys.stdout = output._stdout
        sys.stderr = output._stderr

        yield output
    finally:
        sys.stdout, sys.stderr = oldout, olderr



#===================================================================================================
# StandardRedirect
#===================================================================================================
class StandardRedirect(object):
    '''
    To use:
    
    s = StandardRedirect()
    ...
    out, err = s.reset()
    '''

    def __init__(self, stream_class=None):
        '''
        Initializes and starts capturing stderr and stdout.
        '''
        import sys
        if stream_class is None:
            from cStringIO import StringIO
            stream_class = StringIO

        self._original_stderr = sys.stderr
        self._original_stdout = sys.stdout
        sys.stderr = stream_class()
        sys.stdout = stream_class()


    def reset(self):
        '''
        Stops capturing stderr and stdout. Note that the coding standard is different to be a
        drop in replacement for py.io.StdCapture.
        
        :rtype: tuple(str, str)
        :returns:
            Returns a tuple with (out, err) captured.
        '''
        import sys
        ret = sys.stdout.getvalue(), sys.stderr.getvalue()
        sys.stderr = self._original_stderr
        sys.stdout = self._original_stdout
        return ret



#===================================================================================================
# StandardRedirectAll
#===================================================================================================
class StandardRedirectAll(object):

    def __init__(self, stream_class=None):
        '''
        Initializes and starts capturing stderr and stdout from the Python and C api.
        
        :param <stream> stream_class:
            A StringIO compatible class.
        '''
        self.redirections = [
            StandardRedirect(stream_class),
        ]


    def reset(self):
        '''
        Stops capturing stderr and stdout. 
        
        :rtype: tuple(str, str)
        :returns:
            Returns a tuple with (out, err) captured from the Python and C api (note that
            both are concatenated, so, they won't be correct timewise).
        '''
        out, err = '' , ''
        for r in self.redirections:
            o, e = r.reset()
            out += o
            err += e
        return out, err

