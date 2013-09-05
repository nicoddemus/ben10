set COVERAGE_MODULE=ben10.log
set COVERAGE_PATH=source\python\ben10\_tests\pytest_log.py
set COVERAGE_MODULE=ben10
set COVERAGE_PATH=source\python\ben10
pytest -n8 --cov-report term-missing --cov %COVERAGE_MODULE% %COVERAGE_PATH%

