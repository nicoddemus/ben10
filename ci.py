import os
import sys

def Pytest(params):
    import pytest
    return pytest.main(params.split())

def Pylint(params, output_filename):
    from pylint.lint import Run

    os.chdir('source/python')

    sys_stdout = sys.stdout
    sys.stdout = file(output_filename, 'w')
    try:
        Run(params.split())
    except SystemExit:
        # TODO: handle exit code from pylint
        pass
    finally:
        sys.stdout.close()
        sys.stdout = sys_stdout


old_cwd = os.getcwd()
os.chdir(os.path.dirname(__file__))
try:
    pytest_retcode = Pytest('--junitxml=pytest.xml --cov-report xml --cov ben10 source/python/')
    # TODO: Disabled until we can configure job's done to use pylint.
    #Pylint('-f parseable -d I0011,R0801 ben10', 'pylint.out')
finally:
    os.chdir(old_cwd)

if pytest_retcode:
    sys.exit(999)  # Indicate that build failed
sys.exit(0)

