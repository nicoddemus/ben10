'''
The Console is a class that makes it easier to generate colored output.
'''
import os
import re
import sys



#===================================================================================================
# CreateColorMap
#===================================================================================================
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

    def __init__(self, verbosity=1, color=False, colorama=None, stdout=sys.stdout, stdin=sys.stdin):
        '''
        :param bool|None color:
            Define whether to generate colored output or not.
            If None try to guess whether to use color based on the output capabilities.

        :param bool colorama:
            Enables/disbales the use of colorama.
                None: Tries to use it if available.
                True: Tries to use and fails if not available
                False: Do not use it.
            This is necessary because colorama is incompatible with pytest.
        '''
        self.__stderr = stdout
        self.__stdin = stdin
        self.__stdout = stdout
        if colorama is True:
            import colorama
            self.colorama = True
        elif colorama is None:
            try:
                import colorama
            except ImportError:
                self.colorama = False
            else:
                self.colorama = True
        else:
            self.colorama = False

        self._verbosity = None
        self._SetVerbosity(verbosity)

        self._color = None
        self._SetColor(color)


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
        return re.compile(r'<(%s|/)>' % ('|'.join(self.COLOR_CODES)))


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

    DEFAULT_VERBOSITY = 1
    DEFAULT_NEWLINES = 1
    DEFAULT_INDENT = 0

    def Print(self, message='', verbosity=DEFAULT_VERBOSITY, newlines=DEFAULT_NEWLINES, indent=DEFAULT_INDENT, stderr=False):
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


    def Progress(self, message, verbosity=DEFAULT_VERBOSITY, indent=DEFAULT_INDENT, format_='%s: '):
        '''
        Starts a progree message, without the eol.
        Use one of the "finishers" methods to finish the progress:
        * ProgressOk
        * ProgressError
        '''
        self.Print(format_ % message, verbosity=verbosity, newlines=0, indent=indent)


    def ProgressOk(self, message='OK', verbosity=DEFAULT_VERBOSITY, format_='<green>%s</>'):
        '''
        Ends a progress "successfully" with a message

        :param str message: Message to finish the progress. Default to "OK"
        '''
        self.Print(format_ % message, verbosity=verbosity)


    def ProgressError(self, message, verbosity=DEFAULT_VERBOSITY, format_='<red>%s</>'):
        '''
        Ends a progress "with failure" message

        :param str message: (Error) message to finish the progress.
        '''
        self.Print(format_ % message, verbosity=verbosity)


    def ProgressWarning(self, message, verbosity=DEFAULT_VERBOSITY, format_='<yellow>%s</>'):
        '''
        Ends a progress "with a warning" message

        :param str message: (Warning) message to finish the progress.
        '''
        self.Print(format_ % message, verbosity=verbosity)


    def Item(self, message, verbosity=DEFAULT_VERBOSITY, newlines=1, indent=0, stderr=False, format_='- %s'):
        '''
        Prints an item.

        :param str message:
        :param int verbosity:
        :param int newlines:
        :param int indent:
        :paran bool stderr:
        '''
        return self.Print(format_ % message, verbosity, newlines, indent, stderr)



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
        Console.__init__(self, verbosity=verbosity, color=color, colorama=False, stdout=self.__buffer, stdin=stdin)


    def GetOutput(self):
        '''
        Returns the current value of the output buffer and resets it.
        '''
        from StringIO import StringIO

        result = self.__buffer.getvalue()

        self.__buffer = StringIO()
        self.SetStdOut(self.__buffer)

        return result
