set COVERAGE_MODULE=etk11
set COVERAGE_PATH=source\python\etk11

pytest --cov-report term-missing --cov %COVERAGE_MODULE% %COVERAGE_PATH%

