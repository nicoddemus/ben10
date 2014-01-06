import sys
import os
import pytest
from pylint.lint import Run

pytest_retcode = pytest.main(
    '-n5 --junitxml=pytest.xml --cov-report xml --cov ben10 source/python/'.split()
)

sys_stdout = sys.stdout
sys.stdout = file('pylint.out', 'w')
old_cwd = os.getcwd()
os.chdir('source/python')
try:
    pass  # Run('-f parseable -d I0011,R0801 ben10'.split())
except SystemExit:
    pass
finally:
    os.chdir(old_cwd)
    sys.stdout.close()
    sys.stdout = sys_stdout

if pytest_retcode:
    sys.exit(999)  # Indicate that build failed
sys.exit(0)
