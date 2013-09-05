set COVERAGE_MODULE=etk11.log
set COVERAGE_PATH=source\python\etk11\_tests\pytest_log.py
set COVERAGE_MODULE=etk11
set COVERAGE_PATH=source\python\etk11
pytest -n5 --cov-report term-missing --cov %COVERAGE_MODULE% %COVERAGE_PATH%

