'''
COVERAGE:
  > ii load pytest_cov .
  > pytest --cov-report term-missing --cov sharedscripts10._pytest.fixtures source\python\sharedscripts10\_pytest\_tests\pytest_fixtures.py
  ====================================== test session starts =======================================
  platform win32 -- Python 2.7.3 -- pytest-2.3.4
  collected 5 items

  source/python/sharedscripts10/_pytest/_tests/pytest_fixtures.py .....
  ------------------------- coverage: platform win32, python 2.7.3-final-0 -------------------------
  Name                                             Stmts   Miss  Cover   Missing
  ------------------------------------------------------------------------------
  source\python\sharedscripts10\_pytest\fixtures     126      4    97%   83, 89, 181, 318

  ==================================== 5 passed in 0.40 seconds ====================================
'''
from __future__ import with_statement
from etk11._pytest.fixtures import MultipleFilesNotFound
from etk11.filesystem import CreateFile
import os
import pytest


pytest_plugins = ["etk11._pytest.fixtures"]



#=======================================================================================================================
# Test
#=======================================================================================================================
class Test(object):

    def test_embed_data(self, embed_data):
        assert not os.path.isdir('data_fixtures__test_embed_data')

        embed_data.CreateDataDir()

        assert os.path.isdir('data_fixtures__test_embed_data')

        # Checking if all contents of pytest_fixtures is present
        assert os.path.isfile(embed_data.GetDataFilename('alpha.txt'))
        assert os.path.isfile(embed_data.GetDataFilename('alpha.dist-12.0-win32.txt'))
        assert os.path.isfile(embed_data.GetDataFilename('alpha.dist-12.0.txt'))

        # Checking auxiliary functions
        assert embed_data.GetDataDirectory() == 'data_fixtures__test_embed_data'
        assert embed_data.GetDataFilename('alpha.txt') == 'data_fixtures__test_embed_data/alpha.txt'


    def test_embed_data_ExistingDataDir(self, embed_data):
        # Create the directory manually (we must not use any embed_data functions or else the
        # directory is created)
        extra_txt = 'data_fixtures__test_embed_data_ExistingDataDir/extra.txt'
        CreateFile(extra_txt, 'This file will perish')
        assert os.path.isfile(extra_txt)

        # Calling CreateDataDir again will recreate the directory, deleting the old file
        embed_data.CreateDataDir()
        assert not os.path.isfile(extra_txt)


    def test_embed_data_AssertEqualFiles(self, embed_data):
        CreateFile(embed_data.GetDataFilename('equal.txt'), 'This is alpha.txt')
        embed_data.AssertEqualFiles(
            'alpha.txt',
            'equal.txt'
        )

        CreateFile(embed_data.GetDataFilename('different.txt'), 'This is different.txt')
        with pytest.raises(AssertionError) as e:
            embed_data.AssertEqualFiles(
                'alpha.txt',
                'different.txt'
            )
        assert str(e.value) == '''*** FILENAME: data_fixtures__test_embed_data_AssertEqualFiles/alpha.txt
*** 

--- 

***************

*** 1 ****

! This is alpha.txt
--- 1 ----

! This is different.txt'''


        with pytest.raises(MultipleFilesNotFound) as e:
            embed_data.AssertEqualFiles(
                'alpha.txt',
                'missing.txt'
            )

        assert str(e.value) == 'Files not found: missing.txt,data_fixtures__test_embed_data_AssertEqualFiles/missing.txt'

