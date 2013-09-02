'''
The Console is a class that makes it easier to generate colored output.
'''
import os
import re
import sys



#===============================================================================
# CreateColorMap
#===============================================================================
def _CreateColorMap():
    '''
    Creates a map from color to ESC color codes.
    '''

    codes = {}

    _attrs = {
        'reset':     '39;49;00m',
        'bold':      '01m',
        'faint':     '02m',
        'standout':  '03m',
        'underline': '04m',
        'blink':     '05m',
    }

    for _name, _value in _attrs.items():
        codes[_name] = '\x1b[' + _value

    _colors = [
        ('black', 'darkgray'),
        ('darkred', 'red'),
        ('darkgreen', 'green'),
        ('brown', 'yellow'),
        ('darkblue', 'blue'),
        ('purple', 'fuchsia'),
        ('turqoise', 'teal'),
        ('lightgray', 'white'),
    ]

    for i, (dark, light) in enumerate(_colors):
        codes[dark] = '\x1b[%im' % (i + 30)
        codes[light] = '\x1b[%i;01m' % (i + 30)

    return codes



#===================================================================================================
# Console
#===================================================================================================
class Console(object):
    '''
    Verbosity
    ---------
    
    Controls how much output is generated. It accepts three values:
        0: Quiet: Messages in this level are printed even if verbosity is quiet.
        1: Normal: Messages in this level are printed only of verbosity is normal or higher.
        2: Verbose: Messages in this level are only printed when asked, that is, setting verbosity
                    to the max level.
    
    Print calls with vebosity parameter equal or inferior to the console verbosity value will print
    their messages, otherwise the message is skipped.
    
    The shortcut methods PrintVerbose and PrintQuiet defaults verbosity to the appropriate level. 

    Color
    -----
    
    If true prints using colors on the stdout and stderr. On Windows we convert all ANSI color codes
    to appropriate calls using @colorama@ library. 
    '''

    def __init__(self, verbosity=1, color=None, colorama=True, stdout=sys.stdout, stdin=sys.stdin):
        '''
        :param bool|None color:
            Define whether to generate colored output or not.
            If None try to guess whether to use color based on the output capabilities.
            
        :param bool colorama:
            Enables/disbales the use of colorama.
            This is necessary because colorama is incompatible with pytest. 
        '''
        self.verbosity = verbosity
        self.color = color
        self.colorama = colorama
        self.__stdin = stdin
        self.__stdout = stdout
        self.__stderr = stdout


    def SetStdOut(self, stdout):
        '''
        Configure output streams, both for normal (stdout) and PrintError (stderr) outputs.
        
        :param stdout: A file-like object.
        '''
        self.__stdout = stdout
        self.__stderr = stdout


    def _CreateMarkupRe(self):
        '''
        Creates markup regular-expression.
        Defined in a function because it uses COLOR_CODES constants.
        '''
        markup_re = re.compile(r'<(%s|/)>' % ('|'.join(self.COLOR_CODES)))
        self.__class__.MARKUP_RE = markup_re
        return markup_re


    def _SetVerbosity(self, value):
        '''
        Verbosity property set method.
        '''
        if value not in (0, 1, 2):
            raise ValueError('console.verbosity must be 0, 1 or 2')
        self._verbosity = value


    def _GetVerbosity(self):
        '''
        Verbosity property get method.
        '''
        return self._verbosity


    @classmethod
    def _AutoColor(cls):
        '''
        Try to guess color value (bool) from the environment:
            * sys.stdout.isatty
            * $COLORTERM
            * $TERM
        '''
        # From Sphinx's console.py
        if not hasattr(sys.stdout, 'isatty') or not sys.stdout.isatty():
            return False
        if 'COLORTERM' in os.environ:
            return True
        term = os.environ.get('TERM', 'dumb').lower()
        if term in ('xterm', 'linux') or 'color' in term:
            return True
        return False


    def _SetColor(self, value):
        '''
        Color property set method.
        '''
        if value is None:
            self._color = self._AutoColor()
        else:
            self._color = bool(value)

    def _GetColor(self):
        '''
        Color property get method.
        '''
        return self._color

    verbosity = property(_GetVerbosity, _SetVerbosity)
    color = property(_GetColor, _SetColor)

    MARKUP_RE = property(_CreateMarkupRe)
    COLOR_CODES = _CreateColorMap()


    def Print(self, message='', verbosity=1, newlines=1, indent=0, stderr=False):
        '''
        Prints a message to the output.
        
        :param int verbosity:
        :param int newlines:
        :param int indent:
        :paran bool stderr:
        '''
        if self.verbosity < verbosity:
            return

        if stderr:
            stream = self.__stderr
        else:
            stream = self.__stdout

        message = str(message)
        if self.color:
            # `out` holds the stream of text we'll eventually output
            # `stack` is the currently applied color codes
            # `remaining` holds the still-unparsed part of message
            # `match` is any <colorcode> or </> construct
            out = ''
            stack = []
            remaining = message
            match = self.MARKUP_RE.search(remaining)
            while match:
                # `token` is either 'colorcode' or '/'.
                token = match.groups()[0]
                out += remaining[:match.start()]
                remaining = remaining[match.end():]

                if token == '/':
                    if stack:
                        # Pull the last style off the stack.
                        # Emit a reset then reapply the remaining styles.
                        stack.pop()
                        out += self.COLOR_CODES['reset']
                        for name in stack:
                            out += self.COLOR_CODES[name]
                else:
                    out += self.COLOR_CODES[token]
                    stack.append(token)

                match = self.MARKUP_RE.search(remaining)

            # Get any remaining text that doesn't have markup and
            # reset the terminal if there are any unclosed color tags.
            out += remaining
            if stack:
                out += self.COLOR_CODES['reset']
        else:
            # No color, just strip that information from the message
            out = self.MARKUP_RE.sub('', message)

        # Support for colors on Windows
        assert isinstance(indent, int)
        assert isinstance(newlines, int)
        text = '    ' * indent + out + ('\n' * newlines)
        if self.color and self.colorama:
            from colorama import AnsiToWin32
            AnsiToWin32(stream).write(text)
        else:
            stream.write(text)
            stream.flush()

    def PrintError(self, message, newlines=1, indent=0):
        '''
        Shortcut to Print using stderr.
        '''
        message = str(message)
        return self.Print(message, verbosity=0, newlines=newlines, indent=indent, stderr=True)

    def PrintQuiet(self, message='', newlines=1, indent=0):
        '''
        Shortcut to Print using 'quiet' verbosity.
        '''
        return self.Print(message, verbosity=0, newlines=newlines, indent=indent)

    def PrintVerbose(self, message='', newlines=1, indent=0):
        '''
        Shortcut to Print using 'verbose' verbosity.
        '''
        return self.Print(message, verbosity=2, newlines=newlines, indent=indent)


    def Ask(self, message):
        '''
        Ask the users for a value.
        
        :param str message: Message to print before asking for the value
        :return str: A value entered by the user.
        '''
        self.PrintQuiet(message + ' ', newlines=0)
        return self.__stdin.readline().strip()


    def Progress(self, message):
        '''
        Starts a progree message, without the eol.
        Use one of the "finishers" methods to finish the progress:
        * ProgressOk
        * ProgressError
        '''
        self.Print(message, newlines=0)


    def ProgressOk(self, message='OK'):
        '''
        Ends a progress "successfully" with a message
        
        :param str message: Message to finish the progress. Default to "OK"
        '''
        self.Print(message)


    def ProgressError(self, message):
        '''
        Ends a progress "with failure" with a message
        
        :param str message: (Error) message to finish the progress.
        '''
        self.Print(message)



#===================================================================================================
# BufferedConsole
#===================================================================================================
class BufferedConsole(Console):
    '''
    The same as console, but defaults output to a buffer.
    '''

    def __init__(self, verbosity=1, color=None, stdin=None):
        '''
        :param (1|2|3) verbosity:
        :param bool color:
        '''
        from StringIO import StringIO
        self.__buffer = StringIO()
        Console.__init__(self, verbosity=1, color=color, colorama=False, stdout=self.__buffer, stdin=stdin)


    def GetOutput(self):
        '''
        Returns the current value of the output buffer and resets it.
        '''
        from StringIO import StringIO

        result = self.__buffer.getvalue()

        self.__buffer = StringIO()
        self.SetStdOut(self.__buffer)

        return result



#===================================================================================================
# TESTS
#===================================================================================================

class Test:

    def testConsole(self):
        import pytest
        from StringIO import StringIO

        # Test verbosity control
        with pytest.raises(ValueError):
            Console(verbosity=9)

        oss = StringIO()
        console = Console(verbosity=1, stdout=oss)
        console.PrintQuiet('Alpha.q')
        console.Print('Alpha.n')
        console.PrintVerbose('Alpha.v')
        assert oss.getvalue() == '''Alpha.q\nAlpha.n\n'''

        oss = StringIO()
        console = Console(verbosity=0)
        console.SetStdOut(oss)
        console.PrintQuiet('Alpha.q')
        console.Print('Alpha.n')
        console.PrintVerbose('Alpha.v')
        console.PrintError('Alpha.PrintError')  # For now, stdout and stoerr are the same!
        assert oss.getvalue() == '''Alpha.q\nAlpha.PrintError\n'''

        # Test color control
        console = Console(color=None)

        color_codes = dict(
            red='\x1b[31;01m',
            blue='\x1b[34;01m',
            reset='\x1b[39;49;00m',
        )

        # Stacking colors (only the last one will prevail)
        oss = StringIO()
        console = Console(color=True, colorama=False, stdout=oss)
        console.Print('<red>alpha<blue>bravo</></>charlie')
        assert oss.getvalue() == '%(red)salpha%(blue)sbravo%(reset)s%(red)s%(reset)scharlie\n' % color_codes

        # Automatically resets colors when reaching the eol
        oss = StringIO()
        console = Console(color=True, colorama=False, stdout=oss)
        console.Print('<red>alpha')
        assert oss.getvalue() == '%(red)salpha%(reset)s\n' % color_codes

        # Test Progress methods
        oss = StringIO()
        console = Console(verbosity=2, stdout=oss)
        console.Progress('Doing...')
        assert oss.getvalue() == '''Doing...'''
        console.ProgressOk()
        assert oss.getvalue() == '''Doing...OK\n'''

        oss = StringIO()
        console = Console(verbosity=2, stdout=oss)
        console.Progress('Doing...')
        assert oss.getvalue() == '''Doing...'''
        console.ProgressError('Failed!')
        assert oss.getvalue() == '''Doing...Failed!\n'''

        # Test Ask methods
        iss = StringIO()
        iss.write('alpha\n')
        iss.seek(0)
        console = BufferedConsole(verbosity=2, stdin=iss)
        assert console.Ask('Ask:') == 'alpha'


    def testBufferedConsole(self):
        console = BufferedConsole()

        console.Print('alpha')
        assert console.GetOutput() == '''alpha\n'''

        console.Print('bravo')
        assert console.GetOutput() == '''bravo\n'''


    def testAutoColor(self):
        console = Console()
        assert console.color == False

        class FakeStdout:
            '''
            Mocks the sys.stdout.isatty function behavior.
            '''
            def __init__(self):
                self._isatty = False
            def isatty(self):
                return self._isatty

        sys_stdout = sys.stdout
        sys.stdout = FakeStdout()
        try:
            # Tests sys.stdout.isatty attribute
            console.color = None
            assert console.color == False

            # Tests COLORTERM environment variable
            sys.stdout._isatty = True
            assert console.color == False

            os_environ = os.environ
            os.environ = dict(os.environ)
            os.environ['COLORTERM'] = '1'
            try:
                console.color = None
                assert console.color == True
            finally:
                os.environ = os_environ

            # Tests TERM environment variable
            console.color = None
            assert console.color == False

            os_environ = os.environ
            os.environ = dict(os.environ)
            os.environ['TERM'] = 'color'
            try:
                console.color = None
                assert console.color == True
            finally:
                os.environ = os_environ
        finally:
            sys.stdout = sys_stdout

