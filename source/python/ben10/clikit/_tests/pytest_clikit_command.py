from ben10.clikit.command import Command, InvalidFixture
from ben10.clikit.console import BufferedConsole
import pytest



#===================================================================================================
# TESTS
#===================================================================================================

class Test:

    def testConstructor(self):
        def Hello():
            '''
            Hello function.
            '''

        cmd = Command(Hello)
        assert cmd.names == ['Hello']
        assert cmd.description == 'Hello function.'

        cmd = Command(Hello, names='h')
        assert cmd.names == ['h']

        cmd = Command(Hello, names=['h1', 'h2'])
        assert cmd.names == ['h1', 'h2']


        def no_doc():
            ''

        cmd = Command(no_doc)
        assert cmd.description == '(no description)'


    def testArguments(self):

        def Hello(console_, filename, option='yes', dependency=True, no_setup=False):
            '''
            Hello function.

            :param filename: The name of the file.
            :param dependency: True if set
            :param no_setup: False if set
            '''
            console_.Print('%s - %s' % (filename, option))

        cmd = Command(Hello)
        assert cmd.names == ['Hello']
        assert cmd.description == 'Hello function.'

        assert cmd.fixtures == ['console_']
        assert cmd.args.keys() == ['filename', 'option', 'dependency', 'no_setup']
        assert map(str, cmd.args.values()) == ['filename', 'option=yes', 'dependency', 'no_setup']
        assert cmd.trail is None
        assert cmd.kwargs is None

        console = BufferedConsole()
        cmd.Call({'console_' : console}, {'filename' : 'alpha.txt'})
        assert console.GetOutput() == 'alpha.txt - yes\n'

        # Ignores all invalid arguments passed to Call.
        console = BufferedConsole()
        cmd.Call({'console_' : console}, {'filename' : 'bravo.txt', 'INVALID' : 'INVALID'})
        assert console.GetOutput() == 'bravo.txt - yes\n'

        with pytest.raises(InvalidFixture):
            cmd.Call({}, {'filename' : 'alpha.txt'})

        with pytest.raises(TypeError):
            cmd.Call({'console_' : console}, {})

        assert cmd.FormatHelp() == '''Usage:
    Hello <filename> [--option=yes],[--dependency],[--no_setup]

Parameters:
    filename   The name of the file.

Options:
    --option   (no description) [default: yes]
    --dependency   True if set
    --no_setup   False if set
'''

        import argparse
        parser = argparse.ArgumentParser('TEST')
        cmd.ConfigureArgumentParser(parser)
        assert parser.format_help() == '''usage: TEST [-h] [--option OPTION] [--dependency] [--no_setup] filename

positional arguments:
  filename

optional arguments:
  -h, --help       show this help message and exit
  --option OPTION
  --dependency
  --no_setup
'''
