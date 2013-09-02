from etk11.clikit.app import App
from etk11.clikit.console import BufferedConsole, Console
import inspect
import pytest
import sys



#===================================================================================================
# TESTS
#===================================================================================================

class Test:
    '''
    Tests for App class using py.test
    '''

    def _TestMain(self, app, args, output, retcode=App.RETCODE_OK):
        assert app.Main(args.split()) == retcode
        assert app.console.GetOutput() == output


    def _TestScript(self, app, script):

        def Execute(cmd, output):
            retcode = app.Main(cmd.split())
            assert retcode == App.RETCODE_OK
            assert app.console.GetOutput() == output

        cmd = None
        output = ''
        for i_line in script.splitlines():
            if i_line.startswith('>'):
                if cmd is not None:
                    Execute(cmd, output)
                    cmd = None
                    output = ''
                cmd = i_line[1:]
            else:
                output += i_line + '\n'

        if cmd is not None:
            Execute(cmd, output)


    def testSysArgv(self):
        # False on tests because of colorama incompatibility with py.test
        app = App('test', color=False, buffered_console=True)

        @app
        def Case(console_, argv_, first, second):
            console_.Print('%s..%s' % (first, second))
            console_.Print(argv_)

        old_sys_argv = sys.argv
        sys.argv = [sys.argv[0], 'Case', 'alpha', 'bravo']
        try:
            app.Main()
            assert app.console.GetOutput() == "alpha..bravo\n['Case', 'alpha', 'bravo']\n"
        finally:
            sys.argv = old_sys_argv


    def testBufferedConsole(self):
        app = App('test', color=False, buffered_console=True)
        assert type(app.console) == BufferedConsole

        app = App('test', color=False)
        assert type(app.console) == Console


    def testHelp(self):
        app = App('test', color=False, buffered_console=True)

        @app
        def TestCmd(console_, first, second, option=1, option_yes=True, option_no=False):
            '''
            This is a test.
            
            :param first: This is the first parameter.
            :param second: This is the second and last parameter.
            :param option: This must be a number.
            :param option_yes: If set, says yes.
            :param option_no: If set, says nop.
            '''

        self._TestMain(app, '', '''
Usage:
    test <subcommand> [options]

Commands:
    TestCmd   This is a test.
''')

        self._TestMain(app, '--help', '''
Usage:
    test <subcommand> [options]

Commands:
    TestCmd   This is a test.
''')

        self._TestMain(app, 'TestCmd --help', '''This is a test.

Usage:
    ['TestCmd']

Parameters:
    first   This is the first parameter.
    second   This is the second and last parameter.

Options:
    --option   This must be a number. [default: 1]
    --option_yes   If set, says yes.
    --option_no   If set, says nop.
''')

        self._TestMain(app, 'TestCmd', '''ERROR: Too few arguments.

This is a test.

Usage:
    ['TestCmd']

Parameters:
    first   This is the first parameter.
    second   This is the second and last parameter.

Options:
    --option   This must be a number. [default: 1]
    --option_yes   If set, says yes.
    --option_no   If set, says nop.
''', app.RETCODE_ERROR)


    def testApp(self):
        '''
        Tests App usage and features.
        '''
        import pytest

        # NOTE: Must use color=False on tests because of colorama incompatibility with py.test
        app = App('test', color=False, buffered_console=True)

        @app(alias='cs')
        def Case1(console_):
            '''
            A "hello" message from case 1
            '''
            console_.Print('Hello from case 1')

        @app
        def Case2(console_):
            '''
            A "hello" message from case 2
            
            Additional help for this function is available.
            '''
            console_.Print('Hello from case 2')

        @app(alias=('c3', 'cs3'))
        def Case3(console_):
            console_.Print('Hello from case 3')

        # Test duplicate name
        with pytest.raises(ValueError):
            app.Add(Case3, alias='cs')

        # Test commands listing
        assert app.ListAllCommandNames() == ['Case1', 'cs', 'Case2', 'Case3', 'c3', 'cs3']

        # Tests all commands output
        self._TestMain(app, 'Case1', 'Hello from case 1\n')
        self._TestMain(app, 'cs', 'Hello from case 1\n')
        self._TestMain(app, 'Case2', 'Hello from case 2\n')
        self._TestMain(app, 'Case3', 'Hello from case 3\n')
        self._TestMain(app, 'c3', 'Hello from case 3\n')
        self._TestMain(app, 'cs3', 'Hello from case 3\n')

        # Tests output when an invalid command is requested
        self._TestMain(app, 'INVALID', '''ERROR: Unknown command 'INVALID'

Usage:
    test <subcommand> [options]

Commands:
    Case1, cs        A "hello" message from case 1
    Case2            A "hello" message from case 2
    Case3, c3, cs3   (no description)
''', app.RETCODE_ERROR)


    def testConf(self, tmpdir):
        '''
        Tests the configuration plugin (ConfPlugin)
        '''
        conf_filename = tmpdir.join('ConfigurationCmd.conf')

        app = App(
            'test',
            color=False,
            conf_defaults={
                'group' : {
                    'value' : 'ALPHA',
                }
            },
            conf_filename=str(conf_filename),
            buffered_console=True
        )

        @app
        def ConfigurationCmd(console_, conf_):
            '''
            Test Set/Get methods from configuration object.
            '''
            console_.Print('conf_.filename: %s' % conf_.filename)
            console_.Print('group.value: %s' % conf_.Get('group', 'value'))

            conf_.Set('group', 'value', 'BRAVO')
            console_.Print('group.value: %s' % conf_.Get('group', 'value'))

            assert not conf_filename.check(file=1)
            conf_.Save()
            assert conf_filename.check(file=1)

        self._TestMain(
            app,
            'ConfigurationCmd',
            'conf_.filename: %s\ngroup.value: ALPHA\ngroup.value: BRAVO\n' % conf_filename
        )

        # Creating an application with an existing configuration file.
        assert conf_filename.check(file=1)
        app = App(
            'test',
            color=False,
            conf_defaults={
                'group' : {
                    'value' : 'ALPHA',
                }
            },
            conf_filename=str(conf_filename),
            buffered_console=True
        )

        @app
        def Cmd(console_, conf_):
            console_.Print(conf_.filename)
            console_.Print(conf_.Get('group', 'value'))

        self._TestMain(
            app,
            'Cmd',
            '%s\nBRAVO\n' % conf_filename
        )


    def testPositionalArgs(self):
        '''
        >Command alpha bravo
        alpha..bravo
        '''
        app = App('test', color=False, buffered_console=True)

        @app
        def Command(console_, first, second):
            console_.Print('%s..%s' % (first, second))

        self._TestScript(app, inspect.getdoc(self.testPositionalArgs))


    def testOptionArgs(self):
        '''
        >Command
        1..2
        >Command --first=alpha --second=bravo
        alpha..bravo
        '''
        app = App('test', color=False, buffered_console=True)

        @app
        def Command(console_, first='1', second='2'):
            console_.Print('%s..%s' % (first, second))

        self._TestScript(app, inspect.getdoc(self.testOptionArgs))


    def testColor(self):
        app = App('test', color=True, buffered_console=True)

        assert app.console.color == True

        @app
        def Case():
            '''
            This is Case.
            '''

        self._TestMain(
            app,
            '',
            '''
Usage:
    test <subcommand> [options]

Commands:
    %(teal)sCase%(reset)s   This is Case.
''' % Console.COLOR_CODES
        )


    def testColorama(self, monkeypatch):
        '''
        TODO: Importing colorama from inside pytest raises an exception:

            File "D:\Kaniabi\EDEn\dist\12.0-all\colorama-0.2.5\lib\site-packages\colorama\win32.py", line 64
            in GetConsoleScreenBufferInfo
            >           handle, byref(csbi))
            E       ArgumentError: argument 2: <type 'exceptions.TypeError'>: expected LP_CONSOLE_SCREEN_BUFFER_INFO
                                   instance instead of pointer to CONSOLE_SCREEN_BUFFER_INFO
        '''
#        import colorama



    def testFixture1(self):
        app = App('test', color=True, buffered_console=True)

        @app.Fixture
        def my_fix_():
            return 'This is a custom fixture'

        @app
        def Cmd(console_, my_fix_):
            console_.Print(my_fix_)

        self._TestMain(
            app,
            'Cmd',
            'This is a custom fixture\n'
        )


    def testFixture2(self):
        app = App('test', color=True, buffered_console=True)

        @app.Fixture(name='rubles')
        def my_fix_():
            return 'This is rubles.'

        @app
        def Cmd(console_, rubles_):
            console_.Print(rubles_)

        self._TestMain(
            app,
            'Cmd',
            'This is rubles.\n'
        )

