
from StringIO import StringIO

from etk11.txtout import TextOutput


#=======================================================================================================================
# Test
#=======================================================================================================================
class Test:

    def testIndentContextManager(self):
        stream = StringIO()
        output = TextOutput(stream)

        output.P()  # Empty line
        output.P('Simple line')
        output.P('Indented line', indent=1)

        # We simulate the with_statement, since coilib50 cannot depend on it
        with_stmt = output.P('Now using with!', top_margin=1)
        with_stmt.__enter__()
        output.I('Item inside context')
        with_stmt.__exit__()

        output.I('Item outside context', top_margin=1)

        expected_output = '''
Simple line
    Indented line

Now using with!
    - Item inside context

- Item outside context
'''
        assert stream.getvalue() == expected_output


    def testPageWidthParameter(self):
        stream = StringIO()
        oss = TextOutput(stream)

        oss.P('alpha bravo charlie delta echo foxtrot')
        oss.P('alpha bravo charlie delta echo foxtrot', page_width=12)

        expected_output = '''alpha bravo charlie delta echo foxtrot
alpha bravo
charlie
delta echo
foxtrot
'''
        assert stream.getvalue() == expected_output


    def testPrintEmptyString(self):
        stream = StringIO()

        oss = TextOutput(stream)
        oss.P('')
        expected_output = '\n'
        assert stream.getvalue() == expected_output


    def testPrintEmptyStringIndent(self):
        stream = StringIO()

        oss = TextOutput(stream)
        oss.P('', indent=1)
        expected_output = '    \n'
        assert stream.getvalue() == expected_output


    def testDefaultVerbose(self):
        stream = StringIO()
        oss = TextOutput(stream, verbose_level=1)
        oss.P('Alpha')
        oss.P('Bravo')
        assert stream.getvalue() == 'Alpha\nBravo\n'

        stream = StringIO()
        oss = TextOutput(stream, verbose_level=1)
        oss.default_verbose = 2
        oss.P('Alpha')
        oss.P('Bravo')
        assert stream.getvalue() == ''
