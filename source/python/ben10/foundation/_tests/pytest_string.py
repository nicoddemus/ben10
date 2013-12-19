from ben10.foundation.string import Dedent
import pytest
import sys



#===================================================================================================
# Test
#===================================================================================================
class Test:

    def testDedent1(self):
        string = Dedent(
            '''
            oneline
            '''
        )
        assert string == 'oneline'


    def testDedent2(self):
        string = Dedent(
            '''
            oneline
            twoline
            '''
        )
        assert string == 'oneline\ntwoline'


    def testDedent3(self):
        string = Dedent(
            '''
            oneline
                tabbed
            '''
        )
        assert string == 'oneline\n    tabbed'


    def testDedent4(self):
        string = Dedent(
            '''
            oneline
                tabbed
            detabbed
            '''
        )
        assert string == 'oneline\n    tabbed\ndetabbed'


    def testDedent5(self):
        string = Dedent(
            '''
            oneline
            ''',
            ignore_first_linebreak=False
        )
        assert string == '\noneline'


    def testDedent6(self):
        string = Dedent(
            '''
            oneline
            ''',
            ignore_last_linebreak=False
        )
        assert string == 'oneline\n'


    def testDedent7(self):
        '''
        Test a string that has an 'empty line' with 4 spaces above indent level
        '''
        # Using a trick to avoid auto-format to remove the empty spaces.
        string = Dedent(
            '''
            line
            %s
            other_line
            ''' % '    '
        )
        assert string == 'line\n    \nother_line'


    def testDedent8(self):
        '''
        Test not the first line in the right indent.
        '''
        string = Dedent(
            '''
                alpha
              bravo
            charlie
            '''
        )
        assert string == '    alpha\n  bravo\ncharlie'


    def testDedent9(self):
        '''
        Coverage 100%

        TODO: Strange behavior when mixing tabs and spaces.
        '''
        string = Dedent(
            '''
                alpha
            \tbravo
            '''
        )
        assert string == '                alpha\n            \tbravo'
