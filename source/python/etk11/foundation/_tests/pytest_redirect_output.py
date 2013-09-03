from __future__ import with_statement
from etk11.foundation.redirect_output import CaptureStd
import sys



#===================================================================================================
# Test
#===================================================================================================
class Test:

    def testCaptureStd(self):
        def Check(obtained_output, expected_stdout, expected_stderr):
            assert obtained_output.stdout == expected_stdout
            assert obtained_output.stderr == expected_stderr

        with CaptureStd() as output:
            Check(output, '', '')

            print >> sys.stdout, 'stdout'
            Check(output, 'stdout\n', '')

            print >> sys.stderr, 'stderr'
            Check(output, 'stdout\n', 'stderr\n')

        Check(output, 'stdout\n', 'stderr\n')
