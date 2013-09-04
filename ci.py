import sys
import os
import pytest
from pylint.lint import Run

pytest.main(
    '--junitxml=pytest.xml --cov-report xml --cov etk11 source/python/'.split()
  )

sys_stdout = sys.stdout
sys.stdout = file('pylint.out', 'w')
old_cwd = os.getcwd()
os.chdir('source/python')
try:
    Run('-f parseable -d I0011,R0801 etk11'.split())
except SystemExit:
    pass
finally:
    os.chdir(old_cwd)
    sys.stdout.close()
    sys.stdout = sys_stdout

