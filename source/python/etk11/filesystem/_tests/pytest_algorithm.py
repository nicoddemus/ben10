import os
import sys

import pytest

from etk11.filesystem import CreateFile, CreateDirectory, GetFileContents
from etk11.filesystem.algorithms import FindFiles, Filenames, FindFilename, ReplaceInFile, MakeDirs, SplitAll, \
    RelativePath, NormPath, IsValidFilename, MakeValidFilename, GetInvalidCharsInFilename, CheckInvalidCharsInFilename, \
    GetUnusedFilenameInDirectory
from etk11.fixtures import embed_data


#=======================================================================================================================
# Test
#=======================================================================================================================
class Test:

    def testFindFiles(self, embed_data):
        '''coilib50.path:
            _tmp  -> this folder has these files:  testRoot.bmp / mytestRoot.txt
              | 
           ___A____________________________ -> testA.bmp / mytestA.txt
           |                              |
           B -> testB.bmp mytestB.txt     C -> testC.bmp / mytestC.txt
        '''

        def PATH(p_path):
            return os.path.normpath(p_path)

        def Compare(p_obtained, p_expected):
            obtained = set(map(PATH, p_obtained))
            expected = set(map(PATH, p_expected))
            assert obtained == expected

        CreateDirectory(embed_data.GetDataFilename('A/B'))
        CreateDirectory(embed_data.GetDataFilename('A/C'))
        CreateFile(embed_data.GetDataFilename('testRoot.bmp'), '')
        CreateFile(embed_data.GetDataFilename('mytestRoot.txt'), '')
        CreateFile(embed_data.GetDataFilename('A/testA.bmp'), '')
        CreateFile(embed_data.GetDataFilename('A/mytestA.txt'), '')
        CreateFile(embed_data.GetDataFilename('A/B/testB.bmp'), '')
        CreateFile(embed_data.GetDataFilename('A/B/mytestB.txt'), '')
        CreateFile(embed_data.GetDataFilename('A/C/testC.bmp'), '')
        CreateFile(embed_data.GetDataFilename('A/C/mytestC.txt'), '')

        # no recursion, must return only .bmp files
        in_filter = ['*.bmp']
        out_filter = []
        found_files = list(FindFiles(embed_data.GetDataDirectory(), in_filter, out_filter, False))
        Compare(found_files, [embed_data.GetDataFilename('testRoot.bmp')])

        # no recursion, must return all files
        in_filter = ['*']
        out_filter = []
        found_files = list(FindFiles(embed_data.GetDataDirectory(), in_filter, out_filter, False))
        assert_found_files = ['A', 'mytestRoot.txt', 'testRoot.bmp', ]
        assert_found_files = map(embed_data.GetDataFilename, assert_found_files)
        Compare(found_files, assert_found_files)

        # no recursion, return all files, except *.bmp
        in_filter = ['*']
        out_filter = ['*.bmp']
        found_files = list(FindFiles(embed_data.GetDataDirectory(), in_filter, out_filter, False))
        assert_found_files = ['A', 'mytestRoot.txt', ]
        assert_found_files = map(embed_data.GetDataFilename, assert_found_files)
        Compare(found_files, assert_found_files)

        # recursion, to get just directories
        in_filter = ['*']
        out_filter = ['*.bmp', '*.txt']
        found_files = list(FindFiles(embed_data.GetDataDirectory(), in_filter, out_filter))
        assert_found_files = ['A', 'A/B', 'A/C', ]
        assert_found_files = map(embed_data.GetDataFilename, assert_found_files)
        Compare(found_files, assert_found_files)

        # recursion with no out_filters, must return all files
        in_filter = ['*']
        out_filter = []
        found_files = list(FindFiles(embed_data.GetDataDirectory()))
        assert_found_files = [
            'A',
            'mytestRoot.txt',
            'testRoot.bmp',
            'A/B',
            'A/C',
            'A/mytestA.txt',
            'A/testA.bmp',
            'A/B/mytestB.txt',
            'A/B/testB.bmp',
            'A/C/mytestC.txt',
            'A/C/testC.bmp',
        ]
        assert_found_files = map(PATH, assert_found_files)
        assert_found_files = map(embed_data.GetDataFilename, assert_found_files)
        Compare(found_files, assert_found_files)

        # recursion with no out_filters, must return all files
        # include_root_dir is False, it will be omitted from the found files
        in_filter = ['*']
        out_filter = []
        found_files = list(FindFiles(embed_data.GetDataDirectory(), include_root_dir=False))
        assert_found_files = [
            'A',
            'mytestRoot.txt',
            'testRoot.bmp',
            'A/B',
            'A/C',
            'A/mytestA.txt',
            'A/testA.bmp',
            'A/B/mytestB.txt',
            'A/B/testB.bmp',
            'A/C/mytestC.txt',
            'A/C/testC.bmp',
        ]
        assert_found_files = map(PATH, assert_found_files)
        Compare(found_files, assert_found_files)

        # recursion must return just .txt files
        in_filter = ['*.txt']
        out_filter = []
        found_files = list(FindFiles(embed_data.GetDataFilename('A'), in_filter, out_filter))
        assert_found_files = [
            'A/mytestA.txt',
            'A/B/mytestB.txt',
            'A/C/mytestC.txt',
        ]
        assert_found_files = map(PATH, assert_found_files)
        assert_found_files = map(embed_data.GetDataFilename, assert_found_files)
        Compare(found_files, assert_found_files)

        # recursion must return just .txt files
        in_filter = ['*.txt']
        out_filter = ['*A*']
        found_files = list(FindFiles(embed_data.GetDataDirectory(), in_filter, out_filter))
        assert_found_files = ['mytestRoot.txt', ]
        assert_found_files = map(PATH, assert_found_files)
        assert_found_files = map(embed_data.GetDataFilename, assert_found_files)
        Compare(found_files, assert_found_files)

        # recursion must ignore everyting below a directory that match the out_filter
        in_filter = ['*']
        out_filter = ['B', 'C']
        found_files = list(FindFiles(embed_data.GetDataDirectory(), in_filter, out_filter))
        assert_found_files = [
            'A',
            'A/mytestA.txt',
            'A/testA.bmp',
            'mytestRoot.txt',
            'testRoot.bmp',
        ]
        assert_found_files = map(embed_data.GetDataFilename, assert_found_files)
        Compare(found_files, assert_found_files)


    def testFilenames(self):
        environment_dict = dict(
            ESSS_HOME='d:/ama',
            ESSS_BUILDS='c:/bin/Builds2',
        )

        filenames = Filenames(
            'user',
            [
                '%(abs_path)s',
                '%(abs_path)s.builds2',
                '%(ESSS_HOME)s/.builds/%(filename)s',
                '%(ESSS_HOME)s/.builds/%(filename)s.builds2',
                '%(ESSS_BUILDS)s/projects/%(filename)s',
                '%(ESSS_BUILDS)s/projects/%(filename)s.builds2',
                '%(ESSS_BUILDS)s/projects/%(basename)s/%(filename)s',
                '%(ESSS_BUILDS)s/projects/%(basename)s/%(filename)s.builds2',
            ],
            environment_dict
        )
        cwd = os.getcwd()

        assert filenames[0] == os.path.join(cwd, 'user')
        assert filenames[1] == os.path.join(cwd, 'user.builds2')
        assert filenames[2] == os.path.normpath('d:/ama/.builds/user')
        assert filenames[3] == os.path.normpath('d:/ama/.builds/user.builds2')
        assert filenames[4] == os.path.normpath('c:/bin/Builds2/projects/user')
        assert filenames[5] == os.path.normpath('c:/bin/Builds2/projects/user.builds2')
        assert filenames[6] == os.path.normpath('c:/bin/Builds2/projects/user/user')
        assert filenames[7] == os.path.normpath('c:/bin/Builds2/projects/user/user.builds2')


    def testFindFilesWithStandardPath(self, embed_data):
        CreateDirectory(embed_data.GetDataFilename('A/B'))
        CreateDirectory(embed_data.GetDataFilename('A/C'))
        CreateFile(embed_data.GetDataFilename('A/B/b.file'), '')
        CreateFile(embed_data.GetDataFilename('A/C/c.file'), '')

        # Check all files
        in_filter = ['*.*']
        out_filter = []
        found_files = list(FindFiles(
            embed_data.GetDataDirectory(),
            in_filter,
            out_filter,
            recursive=True,
            standard_paths=True
        ))

        # Since we use standard paths, the result should use unix slashes (in theory this test can
        # only fail in windows)
        expected = map(embed_data.GetDataFilename, ['A/B/b.file', 'A/C/c.file'])
        assert set(found_files) == set(expected)


    def testFindFilename(self, embed_data):
        CreateDirectory(embed_data.GetDataFilename('A/B'))

        filenames = Filenames(
            'testA.bmp',
            [
                '%(abs_path)s',
                embed_data.GetDataFilename('%(filename)s'),
                embed_data.GetDataFilename('A/%(filename)s'),
                embed_data.GetDataFilename('A/B/%(filename)s'),
            ]
        )

        CreateFile(embed_data.GetDataFilename('A/B/testA.bmp'), '')
        filename = FindFilename(filenames)
        assert filename == os.path.normpath(embed_data.GetDataFilename('A/B/testA.bmp'))

        CreateFile(embed_data.GetDataFilename('A/testA.bmp'), '')
        filename = FindFilename(filenames)
        assert filename == os.path.normpath(embed_data.GetDataFilename('A/testA.bmp'))

        CreateFile(embed_data.GetDataFilename('testA.bmp'), '')
        filename = FindFilename(filenames)
        assert filename == os.path.normpath(embed_data.GetDataFilename('testA.bmp'))


    def testReplaceInFile(self, embed_data):
        # create test file
        filename = embed_data.GetDataFilename('test.txt')
        contents = "You're a slave, born in a prison"
        CreateFile(filename, contents)

        ReplaceInFile(filename, 'slave', 'stupid')
        assert GetFileContents(filename) == "You're a stupid, born in a prison"


    def testMakeDirs(self, embed_data):
        dir = embed_data.GetDataFilename('_testing_makedirs')
        MakeDirs(dir)
        assert os.path.isdir(dir)
        MakeDirs(dir)  # no error


    def testSplitAll(self):
        path = '/temp/foo/bar.txt'
        assert SplitAll(path) == ['/', 'temp', 'foo', 'bar.txt']

        path = 'temp/foo/bar.txt'
        assert SplitAll(path) == ['', 'temp', 'foo', 'bar.txt']

        path = './temp/foo/bar.txt'
        assert SplitAll(path) == ['.', 'temp', 'foo', 'bar.txt']

        path = '../temp/foo/bar.txt'
        assert SplitAll(path) == ['..', 'temp', 'foo', 'bar.txt']


    def testRelativePath(self):
        path = RelativePath('/temp/foo', '/temp/foo/bar')
        assert path == 'bar'

        path = RelativePath('temp/foo', 'temp/foo/bar/bar.txt')
        assert path == os.path.join('bar', 'bar.txt')


    def testNormPath(self):
        alpha = 'svn:\/\/10.0.0.60'
        assert NormPath(alpha) == 'svn://10.0.0.60'


    def testValidFilename(self):
        original = sys.platform
        try:
            sys.platform = 'win32'
            assert not IsValidFilename('test*')
            assert not IsValidFilename('tes:t')
            assert IsValidFilename('c:\\test')
            assert not IsValidFilename('c:\\test:')
            assert not IsValidFilename('\\t', False)
            assert not IsValidFilename('/t', False)
            assert not IsValidFilename(':t', False)

            assert MakeValidFilename('c:\\te?st:') == 'c:\\te_st_'
            assert set(GetInvalidCharsInFilename('c:\\tes*/t[:|<>?"')) == set(['*', ':', '|', '<', '>', '?', '"'])

            sys.platform = 'linux'
            assert MakeValidFilename('c:\\te?st:') == 'c:\\te_st:'  # : is ok in linux
            assert IsValidFilename('c:\\test')
            assert not IsValidFilename('c<test>')

            with pytest.raises(ValueError):
                CheckInvalidCharsInFilename('c<?foo')

            assert not IsValidFilename('\\test', False)
            assert not IsValidFilename('/test', False)
            assert IsValidFilename(':test', False)
        finally:
            sys.platform = original


    def testObtainUnusedFilenameInDirectory(self, embed_data):

        def PerformTestOnFilename(test_name, expected_base, create_file=False):
            # If a used filena is passed, then a new filename is returned
            expected_filename = os.path.join(embed_data.GetDataDirectory(), expected_base)
            full_test_name = embed_data.GetDataFilename(test_name)
            base_dir, base_filename = os.path.split(full_test_name)

            new_file_name = GetUnusedFilenameInDirectory(base_dir, base_filename)
            assert new_file_name == expected_filename

            if create_file:
                new_file = open(new_file_name, 'w')
                new_file.close()

        # Creating some files in the test directory
        existing_file_names = ['existing_file.txt', 'existing_file_01.txt', 'existing_file_03.txt']

        for name in existing_file_names:
            filename = embed_data.GetDataFilename(name)
            new_file = open(filename, 'w')
            new_file.close()

        base_prefix = 'existing_file.txt'
        # If a used filena is passed, then a new filename is returned
        PerformTestOnFilename(base_prefix, 'existing_file_002.txt')

        # If a not used filename is passed, then the same filename is returned
        new_filename_prefix = 'new_filename.txt'
        PerformTestOnFilename(new_filename_prefix, new_filename_prefix, True)

        expected_base = 'new_filename_002.txt'
        # But ask once again for the same file from the same base should result ina different file
        PerformTestOnFilename(new_filename_prefix, expected_base, True)

        expected_base = 'new_filename_003.txt'
        PerformTestOnFilename(new_filename_prefix, expected_base, True)

        # If the received base ends with '_' then an index will be added event if the base file
        # does not exist
        new_filename_prefix = 'new_prefix_with_underscore_.txt'
        expected_base = 'new_prefix_with_underscore_001.txt'
        PerformTestOnFilename(new_filename_prefix, expected_base, True)
