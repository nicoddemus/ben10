'''
COVERAGE:
    Name                                                           Stmts   Miss  Cover   Missing
    --------------------------------------------------------------------------------------------
    source\python\etk11\_pytest\fixtures                              78      2    97%   87, 92    

PYLINK:
    ************* Module etk11.fixtures
    C:  1,0: Missing docstring
    C:  8,0:MultipleFilesNotFound: Missing docstring
    W: 10,4:MultipleFilesNotFound.__init__: __init__ method from base class 'RuntimeError' is not called
    C:179,8:_EmbedDataFixture.AssertEqualFiles.FindFile: Missing docstring
    C:202,0:embed_data: Invalid name "embed_data" for type function (should match [A-Z_][a-zA-Z0-9_]{2,30}$)
    E:201,1:embed_data: Module 'pytest' has no 'fixture' member
'''
from __future__ import with_statement

import os

import pytest

from etk11 import is_frozen
from etk11.fixtures import MultipleFilesNotFound
from etk11.filesystem import CreateFile, StandardizePath


pytest_plugins = ["etk11.fixtures"]



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

        assert embed_data.GetDataDirectory(absolute=True) \
            == StandardizePath(os.path.abspath('data_fixtures__test_embed_data'))
        assert embed_data.GetDataFilename('alpha.txt', absolute=True) \
            == StandardizePath(os.path.abspath('data_fixtures__test_embed_data/alpha.txt'))


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


    def testNotOnFrozen(self, monkeypatch, embed_data):
        monkeypatch.setattr(is_frozen, 'IsFrozen', lambda:True)

        with pytest.raises(RuntimeError) as exception:
            embed_data.CreateDataDir()

        filename = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'fixtures.py')
        assert str(exception) in (
            'File "%s", line 87\nRuntimeError: _EmbedDataFixture is not ready for execution inside an executable.' % filename,
            '%s:87: RuntimeError: _EmbedDataFixture is not ready for execution inside an executable.' % filename,
        )



