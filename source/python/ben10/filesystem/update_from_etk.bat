copy /qes x:\etk\coilib50\source\python\coilib50\filesystem\*.py
echo from _duplicates import CheckForUpdate, ExtendedPathMask, FindFiles, MatchMasks >> __init__.py
call aa.bat .fix_format . --refactor=update_from_etk.ini


