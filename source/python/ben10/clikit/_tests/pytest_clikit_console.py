from ben10.clikit.console import BufferedConsole, Console
import os
import sys



#===================================================================================================
# TESTS
#===================================================================================================

class Test:

    def testConsole(self):
        from StringIO import StringIO
        import pytest

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

        oss = StringIO()
        console = Console(verbosity=2, stdout=oss)
        console.Progress('Doing...')
        assert oss.getvalue() == '''Doing...'''
        console.ProgressWarning('Skiped!')
        assert oss.getvalue() == '''Doing...Skiped!\n'''

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

