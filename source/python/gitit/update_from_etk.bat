copy /qe x:\etk\sharedscripts10\source\python\sharedscripts10\_git_impl.py git.py

mkdir _tests
copy /qe x:\etk\sharedscripts10\source\python\sharedscripts10\_tests\pytest_git.py _tests
copy /qes x:\etk\sharedscripts10\source\python\sharedscripts10\_tests\pytest_git _tests\pytest_git

sfk replace git.py /System().// -yes

call aa.bat .fix_format . --refactor=update_from_etk.ini


