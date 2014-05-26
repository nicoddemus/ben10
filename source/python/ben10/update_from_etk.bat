copy /qe x:\etk\sharedscripts10\source\python\sharedscripts10\_execute_impl.py execute.py

copy /qe x:\etk\sharedscripts10\source\python\sharedscripts10\_tests\pytest_execute.py _tests
copy /qes x:\etk\sharedscripts10\source\python\sharedscripts10\_tests\pytest_execute _tests\pytest_execute

call aa.bat .fix_format _tests\pytest_execute.py --refactor=x:\ben10\terraforming.ini
call aa.bat .fix_format execute.py --refactor=x:\ben10\terraforming.ini
