from __future__ import with_statement
from etk11.filesystem import GetFileContents, CreateFile, EOL_STYLE_MAC, ListFiles, CreateDirectory, MoveFile, \
    DeleteDirectory, NotImplementedForRemotePathError, AppendToFile, DeleteFile, CopyDirectory, CopyFile, CopyFiles, \
    DirectoryNotFoundError, CopyFilesX, IsDir, IsFile, FileAlreadyExistsError, MoveDirectory, DirectoryAlreadyExistsError, \
    MD5_SKIP, CheckIsFile, FileNotFoundError, GetMTime, StandardizePath, NormStandardPath, NormalizePath, CanonicalPath, \
    EOL_STYLE_NONE, EOL_STYLE_WINDOWS, EOL_STYLE_UNIX, OpenFile, CreateMD5, GetFileLines, CheckIsDir
import os
import pytest
import sys



pytest_plugins = ["etk11.fixtures"]



# ==================================================================================================
# Test
# ==================================================================================================
class Test:

    def assertSetEqual(self, a, b):
        assert set(a) == set(b)


    def testCreateMD5(self, embed_data):
        source_filename = embed_data.GetDataFilename('files/source/alpha.txt')
        target_filename = embed_data.GetDataFilename('files/source/alpha.txt.md5')

        assert not os.path.isfile(target_filename)

        # By default, CreateMD5 should keep the filename, adding .md5
        CreateMD5(source_filename)
        assert os.path.isfile(target_filename)
        assert GetFileContents(target_filename) == 'd41d8cd98f00b204e9800998ecf8427e'

        # Filename can also be forced
        target_filename = embed_data.GetDataFilename('files/source/md5_file')
        assert not os.path.isfile(target_filename)

        CreateMD5(source_filename, target_filename=target_filename)
        assert os.path.isfile(target_filename)
        assert GetFileContents(target_filename) == 'd41d8cd98f00b204e9800998ecf8427e'


    def testCopyFileWithMd5(self, embed_data):
        source_filename = embed_data.GetDataFilename('md5/file')
        source_filename_md5 = embed_data.GetDataFilename('md5/file.md5')
        target_filename = embed_data.GetDataFilename('md5/copied_file')
        target_filename_md5 = embed_data.GetDataFilename('md5/copied_file.md5')

        # Make sure that files do not exist prior to copying
        assert not os.path.isfile(target_filename)
        assert not os.path.isfile(target_filename_md5)

        def CopyAndCheck(source, target, expecting_skip=False):
            # Copy files considering md5
            result = CopyFile(
                source_filename=source,
                target_filename=target,
                override=True,
                md5_check=True,
            )
            if expecting_skip:
                assert result == MD5_SKIP
            else:
                assert result is None

        CopyAndCheck(source_filename, target_filename, expecting_skip=False)
        assert os.path.isfile(target_filename)
        assert os.path.isfile(target_filename_md5)

        # Make sure that the contents of md5 file are as expected
        assert GetFileContents(target_filename_md5) == '65fa244213983bd017d7d447bb534248'

        # Copying again should be ignored, since the md5's match (mtime should not change)
        CopyAndCheck(source_filename, target_filename, expecting_skip=True)

        # If the local file (not md5) is missing, it must be copied (even though technically the
        # md5 is still there, and matches)
        DeleteFile(target_filename)
        CopyAndCheck(source_filename, target_filename, expecting_skip=False)

        # Delete local md5 and file should be copied again
        DeleteFile(target_filename_md5)
        CopyAndCheck(source_filename, target_filename, expecting_skip=False)

        # Same for a modified md5
        CreateFile(target_filename_md5, contents='00000000000000000000000000000000')
        CopyAndCheck(source_filename, target_filename, expecting_skip=False)

        # Sanity check
        CopyAndCheck(source_filename, target_filename, expecting_skip=True)

        # If the source md5 changed, we have to copy it again
        CreateFile(source_filename_md5, contents='00000000000000000000000000000000')
        CopyAndCheck(source_filename, target_filename, expecting_skip=False)

        # If the source md5 does not exist, we have to the file, and ignore the md5
        DeleteFile(source_filename_md5)
        DeleteFile(target_filename_md5)
        CopyAndCheck(source_filename, target_filename, expecting_skip=False)
        assert not os.path.isfile(source_filename_md5)
        assert not os.path.isfile(target_filename_md5)


    def testCopyFilesX(self, embed_data):
        base_dir = embed_data.GetDataFilename('complex_tree') + '/'

        def CheckFiles(files):
            for file_1, file_2 in files:
                embed_data.AssertEqualFiles(file_1, file_2)

        # Shallow copy in the base dir -------------------------------------------------------------
        copied_files = CopyFilesX([
            (embed_data.GetDataFilename('A'), base_dir + '*'),
        ])
        self.assertSetEqual(
            copied_files,
            [
                ('data_filesystem__testCopyFilesX/complex_tree/1', 'data_filesystem__testCopyFilesX/A/1'),
                ('data_filesystem__testCopyFilesX/complex_tree/2', 'data_filesystem__testCopyFilesX/A/2'),
            ]
        )
        CheckFiles(copied_files)

        # Recurisve copy in a subdir ---------------------------------------------------------------
        copied_files = CopyFilesX([
            (embed_data.GetDataFilename('B'), '+' + base_dir + '/subdir_1/*')
        ])

        self.assertSetEqual(
            copied_files,
            [
                ('data_filesystem__testCopyFilesX/complex_tree//subdir_1/subsubdir_1/1.1.1', 'data_filesystem__testCopyFilesX/B/subsubdir_1/1.1.1'),
                ('data_filesystem__testCopyFilesX/complex_tree//subdir_1/subsubdir_1/1.1.2', 'data_filesystem__testCopyFilesX/B/subsubdir_1/1.1.2')
            ]
        )
        CheckFiles(copied_files)

        # Shallow copy in the base dir, with filter ------------------------------------------------
        copied_files = CopyFilesX([
            (embed_data.GetDataFilename('shallow'), base_dir + '1'),
        ])

        self.assertSetEqual(
            copied_files,
            [
                ('data_filesystem__testCopyFilesX/complex_tree/1', 'data_filesystem__testCopyFilesX/shallow/1'),
            ]
        )
        CheckFiles(copied_files)

        # Shallow copy in the base dir, with multiple filter ---------------------------------------
        copied_files = CopyFilesX([
            (embed_data.GetDataFilename('shallow'), base_dir + '1;2'),
        ])

        self.assertSetEqual(
            copied_files,
            [
                ('data_filesystem__testCopyFilesX/complex_tree/1', 'data_filesystem__testCopyFilesX/shallow/1'),
                ('data_filesystem__testCopyFilesX/complex_tree/2', 'data_filesystem__testCopyFilesX/shallow/2'),
            ]
        )
        CheckFiles(copied_files)

        # Recursive copy of all files --------------------------------------------------------------
        copied_files = CopyFilesX([
            (embed_data.GetDataFilename('all'), '+' + base_dir + '*')
        ])

        self.assertSetEqual(
            copied_files,
            [
                ('data_filesystem__testCopyFilesX/complex_tree/1', 'data_filesystem__testCopyFilesX/all/1'),
                ('data_filesystem__testCopyFilesX/complex_tree/2', 'data_filesystem__testCopyFilesX/all/2'),
                ('data_filesystem__testCopyFilesX/complex_tree/subdir_1/subsubdir_1/1.1.1', 'data_filesystem__testCopyFilesX/all/subdir_1/subsubdir_1/1.1.1'),
                ('data_filesystem__testCopyFilesX/complex_tree/subdir_1/subsubdir_1/1.1.2', 'data_filesystem__testCopyFilesX/all/subdir_1/subsubdir_1/1.1.2'),
                ('data_filesystem__testCopyFilesX/complex_tree/subdir_2/2.1', 'data_filesystem__testCopyFilesX/all/subdir_2/2.1')
            ]
        )
        CheckFiles(copied_files)

        # Recursive copy of all files with filter --------------------------------------------------
        copied_files = CopyFilesX([
            (embed_data.GetDataFilename('all'), '+' + base_dir + '1.1*')
        ])

        self.assertSetEqual(
            copied_files,
            [
                ('data_filesystem__testCopyFilesX/complex_tree/subdir_1/subsubdir_1/1.1.1', 'data_filesystem__testCopyFilesX/all/subdir_1/subsubdir_1/1.1.1'),
                ('data_filesystem__testCopyFilesX/complex_tree/subdir_1/subsubdir_1/1.1.2', 'data_filesystem__testCopyFilesX/all/subdir_1/subsubdir_1/1.1.2'),
            ]
        )
        CheckFiles(copied_files)

        # Recursive copy of all files with negative filter -----------------------------------------
        copied_files = CopyFilesX([
            (embed_data.GetDataFilename('all'), '+' + base_dir + '*;!*2')
        ])

        self.assertSetEqual(
            copied_files,
            [
                ('data_filesystem__testCopyFilesX/complex_tree/1', 'data_filesystem__testCopyFilesX/all/1'),
                ('data_filesystem__testCopyFilesX/complex_tree/subdir_1/subsubdir_1/1.1.1', 'data_filesystem__testCopyFilesX/all/subdir_1/subsubdir_1/1.1.1'),
            ]
        )
        CheckFiles(copied_files)

        # Flat recursive ---------------------------------------------------------------------------
        copied_files = CopyFilesX([
            (embed_data.GetDataFilename('all'), '-' + base_dir + '1.1*')
        ])

        self.assertSetEqual(
            copied_files,
            [
                ('data_filesystem__testCopyFilesX/complex_tree/subdir_1/subsubdir_1/1.1.1', 'data_filesystem__testCopyFilesX/all/1.1.1'),
                ('data_filesystem__testCopyFilesX/complex_tree/subdir_1/subsubdir_1/1.1.2', 'data_filesystem__testCopyFilesX/all/1.1.2'),
            ]
        )
        CheckFiles(copied_files)


    def testCopyFiles(self, embed_data):
        source_dir = embed_data.GetDataFilename('files/source')
        target_dir = embed_data.GetDataFilename('target_dir')

        # Make sure that the target dir does not exist
        assert not os.path.isdir(target_dir)

        # We should get an error if trying to copy files into a missing dir
        with pytest.raises(DirectoryNotFoundError):
            CopyFiles(source_dir, target_dir)

        # Create dir and check files
        CopyFiles(source_dir, target_dir, create_target_dir=True)

        assert ListFiles(source_dir) == ListFiles(target_dir)

        # Inexistent source directory --------------------------------------------------------------
        inexistent_dir = embed_data.GetDataFilename('INEXISTENT_DIR')
        CopyFiles(inexistent_dir + '/*', target_dir)


    def testCopyFileSymlink(self, embed_data):
        if sys.platform.startswith('win'):
            return

        # Create a filei
        original = embed_data.GetDataFilename('original_file.txt')
        CreateFile(original, contents='original')

        # Create symlink to that file
        symlink = embed_data.GetDataFilename('symlink.txt')
        os.symlink(os.path.abspath(original), symlink)

        assert os.path.islink(symlink)

        # Copy link
        copied_symlink = embed_data.GetDataFilename('copied_symlink.txt')
        CopyFile(symlink, copied_symlink, copy_symlink=True)

        assert os.path.islink(copied_symlink)

        # Copy real file
        real_file = embed_data.GetDataFilename('real_file.txt')
        CopyFile(symlink, real_file, copy_symlink=False)

        assert not os.path.islink(real_file)


    def testOpenFile(self, embed_data):
        test_filename = embed_data.GetDataFilename('testOpenFile.data')

        # Create a file with a mixture of "\r" and "\n" characters
        oss = file(test_filename, 'wb')
        oss.write('Alpha\nBravo\r\nCharlie\rDelta')
        oss.close()

        # Use OpenFile to obtain the file contents, with binary=False and binary=True
        iss = OpenFile(test_filename, binary=False)

        expected = 'Alpha\nBravo\nCharlie\nDelta'
        assert iss.read() == expected

        iss = OpenFile(test_filename, binary=True)
        assert iss.read() == 'Alpha\nBravo\r\nCharlie\rDelta'


    def testFileContents(self, embed_data):
        test_filename = embed_data.GetDataFilename('testFileContents.data')

        # Create a file with a mixture of "\r" and "\n" characters
        oss = file(test_filename, 'wb')
        oss.write('Alpha\nBravo\r\nCharlie\rDelta')
        oss.close()

        expected = 'Alpha\nBravo\nCharlie\nDelta'

        # Use GetFileContents to obtain the file contents, with binary=False and binary=True
        assert GetFileContents(test_filename) == expected
        assert GetFileContents(test_filename, binary=True) == 'Alpha\nBravo\r\nCharlie\rDelta'


    def testFileLines(self, embed_data):
        test_filename = embed_data.GetDataFilename('testFileLines.data')

        # Create a file with a mixture of "\r" and "\n" characters
        oss = file(test_filename, 'wb')
        oss.write('Alpha\nBravo\r\nCharlie\rDelta')
        oss.close()

        expected = ['Alpha', 'Bravo', 'Charlie', 'Delta']

        # Use GetFileContents to obtain the file contents, with binary=False and binary=True
        assert GetFileLines(test_filename) == expected


    def testFTPFileContents(self, monkeypatch, embed_data):
        self._StartFtpServer(monkeypatch, embed_data.GetDataDirectory())
        try:
            obtained = GetFileContents(self._GetFTPUrl('file.txt'))
            expected = GetFileContents(embed_data.GetDataFilename('file.txt'))
            assert obtained == expected

            with pytest.raises(FileNotFoundError):
                GetFileContents(self._GetFTPUrl('missing_file.txt'))
        finally:
            self._StopFtpServer()


    def testCreateFile(self, embed_data):
        contents = 'First\nSecond\r\nThird\rFourth'
        contents_unix = 'First\nSecond\nThird\nFourth'
        contents_mac = 'First\rSecond\rThird\rFourth'
        contents_windows = 'First\r\nSecond\r\nThird\r\nFourth'

        target_file = embed_data.GetDataFilename('mac.txt')
        CreateFile(target_file, contents, eol_style=EOL_STYLE_MAC)
        assert GetFileContents(target_file, binary=True) == contents_mac

        target_file = embed_data.GetDataFilename('windows.txt')
        CreateFile(target_file, contents, eol_style=EOL_STYLE_WINDOWS)
        assert GetFileContents(target_file, binary=True) == contents_windows

        target_file = embed_data.GetDataFilename('linux.txt')
        CreateFile(target_file, contents, eol_style=EOL_STYLE_UNIX)
        assert GetFileContents(target_file, binary=True) == contents_unix

        contents_binary = 'First\nSecond\r\nThird\rFourth'
        target_file = embed_data.GetDataFilename('binary.txt')
        CreateFile(target_file, contents, eol_style=EOL_STYLE_NONE)
        assert GetFileContents(target_file, binary=True) == contents_binary


    def testCreateFileInMissingDirectory(self, monkeypatch, embed_data):
        from ftputil.ftp_error import FTPIOError

        # Trying to create a file in a directory that does not exist should raise an error
        target_file = embed_data.GetDataFilename('missing_dir/sub_dir/file.txt')

        with pytest.raises(IOError):
            CreateFile(target_file, contents='contents', create_dir=False)

        # Unless we pass the correct parameter
        CreateFile(target_file, contents='contents', create_dir=True)
        assert GetFileContents(target_file) == 'contents'

        # Also works if there is no subdirectory
        single_file = 'just_file.txt'
        try:
            CreateFile(single_file, contents='contents', create_dir=True)
        finally:
            DeleteFile(single_file)

        # Same goes for FTP
        self._StartFtpServer(monkeypatch, embed_data.GetDataDirectory())
        try:
            target_ftp_file = self._GetFTPUrl('missing_ftp_dir/sub_dir/file.txt')

            with pytest.raises(FTPIOError):
                CreateFile(target_ftp_file, contents='contents', create_dir=False)

            CreateFile(target_ftp_file, contents='contents', create_dir=True)
            assert GetFileContents(target_ftp_file) == 'contents'
        finally:
            self._StopFtpServer()


    def testAppendToFile(self, embed_data):
        # Check initial contents in file
        file_path = embed_data.GetDataFilename('files/source/alpha.txt')
        assert GetFileContents(file_path) == ''

        # Append some text
        contents = 'some phrase'
        AppendToFile(file_path, contents)

        assert GetFileContents(file_path) == contents


    def testMoveFile(self, embed_data):
        origin = embed_data.GetDataFilename('files/source/alpha.txt')
        target = embed_data.GetDataFilename('moved_alpha.txt')

        assert os.path.isfile(origin)
        assert not os.path.isfile(target)

        MoveFile(origin, target)

        assert not os.path.isfile(origin)
        assert os.path.isfile(target)


        # Move only works for local files
        with pytest.raises(NotImplementedForRemotePathError):
            MoveFile('ftp://user@server:origin_file', 'target_file')

        with pytest.raises(NotImplementedForRemotePathError):
            MoveFile('origin_file', 'ftp://user@server:target_file')


    def testMoveDirectory(self, embed_data):
        origin = embed_data.GetDataFilename('files', 'source')
        target = embed_data.GetDataFilename('files', 'source_renamed')

        assert os.path.isdir(origin)
        assert not os.path.isdir(target)

        MoveDirectory(origin, target)

        assert not os.path.isdir(origin)
        assert os.path.isdir(target)

        # Cannot rename a directory if the target dir already exists
        some_dir = embed_data.GetDataFilename('some_directory')
        CreateDirectory(some_dir)
        with pytest.raises(DirectoryAlreadyExistsError):
            MoveDirectory(some_dir, target)


    def testIsFile(self, embed_data):
        assert IsFile(embed_data.GetDataFilename('file.txt')) == True
        assert IsFile(embed_data.GetDataFilename('files/source/alpha.txt')) == True
        assert IsFile(embed_data.GetDataFilename('doesnt_exist')) == False
        assert IsFile(embed_data.GetDataFilename('files/doesnt_exist')) == False


    def testCopyDirectory(self, embed_data):
        source_dir = embed_data.GetDataFilename('complex_tree')
        target_dir = embed_data.GetDataFilename('complex_tree_copy')

        # Sanity check
        assert not os.path.isdir(target_dir)

        # Copy directory and check files files
        CopyDirectory(source_dir, target_dir)

        # Check directories for files
        assert ListFiles(source_dir) == ListFiles(target_dir)
        assert ListFiles(embed_data.GetDataFilename(source_dir, 'subdir_1')) \
            == ListFiles(embed_data.GetDataFilename(target_dir, 'subdir_1'))
        assert ListFiles(embed_data.GetDataFilename(source_dir, 'subdir_1', 'subsubdir_1')) \
            == ListFiles(embed_data.GetDataFilename(target_dir, 'subdir_1', 'subsubdir_1'))
        assert ListFiles(embed_data.GetDataFilename(source_dir, 'subdir_2')) \
            == ListFiles(embed_data.GetDataFilename(target_dir, 'subdir_2'))


    def testCopyDirectoryFailureToOverrideTarget(self, embed_data):
        '''
        CopyDirectory function must raise an error when fails trying to delete target directory if
        override option is set as True.

        It may fail to delete target directory when target directory has an internal file open or
        when user trying to perform doesn't have permissions necessary, for instance.
        '''
        # Only tested on Windows platform because we aren't sure how to properly reproduce behavior
        # on Linux, since open file handles are kept alive even after files are deleted and no error
        # is raised.
        #
        # Reference: http://stackoverflow.com/questions/2028874/what-happens-to-an-open-file-handler-on-linux-if-the-pointed-file-gets-moved-de
        if 'win' in sys.platform:
            foo_dir = os.path.join(embed_data.GetDataDirectory(), 'foo')
            os.mkdir(foo_dir)
            foo_file = os.path.join(foo_dir, 'foo.txt')

            bar_dir = os.path.join(embed_data.GetDataDirectory(), 'bar')
            os.mkdir(bar_dir)

            with open(foo_file, 'w'):
                with pytest.raises(OSError):
                    CopyDirectory(bar_dir, foo_dir, override=True)


    def testDeleteFile(self, embed_data):
        file_path = embed_data.GetDataFilename('files/source/alpha.txt')

        # Make sure file is there
        assert os.path.isfile(file_path)

        DeleteFile(file_path)

        # And now its gone
        assert not os.path.isfile(file_path)

        # Deleting a file that does not exist will not raise errors
        fake = 'fake_file'
        assert not os.path.isfile(fake)
        DeleteFile(fake)

        # Raises erorr if tries to delete a directory
        a_dir = os.path.join(embed_data.GetDataFilename('files/source'), 'a_dir')
        os.mkdir(a_dir)
        from etk11.filesystem import FileOnlyActionError
        with pytest.raises(FileOnlyActionError):
            DeleteFile(a_dir)


    def testDeleteDirectory(self, embed_data):
        dir_path = embed_data.GetDataFilename('files')

        assert os.path.isdir(dir_path)
        DeleteDirectory(dir_path)
        assert not os.path.isdir(dir_path)

        # DeleteDirectory only works for local files
        with pytest.raises(NotImplementedForRemotePathError):
            DeleteDirectory('ftp://user@server:dir')


    def testCreateDirectory(self, embed_data):
        # Dir not created yet
        assert os.path.isdir(embed_data.GetDataFilename('dir1')) == False

        # Dir created
        CreateDirectory(embed_data.GetDataFilename('dir1'))
        assert os.path.isdir(embed_data.GetDataFilename('dir1')) == True

        # Creating it again will not raise an error
        CreateDirectory(embed_data.GetDataFilename('dir1'))

        # Creating long sequence
        CreateDirectory(embed_data.GetDataFilename('dir1/dir2/dir3'))
        assert os.path.isdir(embed_data.GetDataFilename('dir1')) == True
        assert os.path.isdir(embed_data.GetDataFilename('dir1/dir2')) == True
        assert os.path.isdir(embed_data.GetDataFilename('dir1/dir2/dir3')) == True


    def testListFiles(self, embed_data):
        # List local files
        assert set(ListFiles(embed_data.GetDataFilename('files/source'))) == set(['alpha.txt', 'bravo.txt', 'subfolder'])

        # Try listing a dir that does not exist
        assert ListFiles(embed_data.GetDataFilename('files/non-existent')) is None


    def testCopyFile(self, embed_data):
        source_file = embed_data.GetDataFilename('files/source/alpha.txt')
        target_file = embed_data.GetDataFilename('alpha_copy.txt')

        # Sanity check
        assert not os.path.isfile(target_file)

        # Copy and check file
        CopyFile(source_file, target_file)
        embed_data.AssertEqualFiles(source_file, target_file)


    def testIsDir(self, embed_data):
        assert IsDir('.')
        assert not IsDir(embed_data.GetDataFilename('missing_dir'))


    def testFTPIsDir(self, monkeypatch, embed_data):
        self._StartFtpServer(monkeypatch, embed_data.GetDataDirectory())

        try:
            assert IsDir(self._GetFTPUrl('.'))
            assert not IsDir(self._GetFTPUrl('missing_dir'))
        finally:
            self._StopFtpServer()


    def testFTPCopyFiles(self, monkeypatch, embed_data):
        self._StartFtpServer(monkeypatch, embed_data.GetDataDirectory())

        try:
            source_dir = embed_data.GetDataFilename('files/source')
            target_dir = self._GetFTPUrl('ftp_target_dir')

            # Make sure that the target dir does not exist
            assert not os.path.isdir(target_dir)

            # We should get an error if trying to copy files into a missing dir
            with pytest.raises(DirectoryNotFoundError):
                CopyFiles(source_dir, target_dir)

            # Create dir and check files
            CopyFiles(source_dir, target_dir, create_target_dir=True)

            assert set(ListFiles(source_dir)) == set(ListFiles(target_dir))
        finally:
            self._StopFtpServer()


    def testMoveDirectoryFTP(self, monkeypatch, embed_data):
        self._StartFtpServer(monkeypatch, embed_data.GetDataDirectory())

        try:
            source_dir = self._GetFTPUrl('files/source')
            target_dir = self._GetFTPUrl('ftp_target_dir')

            # Make sure that the source exists, and target does not
            assert IsDir(source_dir)
            assert not IsDir(target_dir)

            # Keep a list of files in source_dir
            source_files = ListFiles(source_dir)

            # Move directory
            MoveDirectory(source_dir, target_dir)

            # Make sure that the target exists, and source does not
            assert IsDir(target_dir)
            assert not IsDir(source_dir)

            # list of files should be the same as before
            assert ListFiles(target_dir) == source_files

            # Cannot rename a directory if the target dir already exists
            source_dir = self._GetFTPUrl('some_directory')
            CreateDirectory(source_dir)
            with pytest.raises(DirectoryAlreadyExistsError):
                MoveDirectory(source_dir, target_dir)
        finally:
            self._StopFtpServer()


    def testFTPCopyFile(self, monkeypatch, embed_data):
        def CopyAndCheckFiles(source_file, target_file, override=True):
            CopyFile(
                source_file,
                target_file,
                override,
            )
            assert GetFileContents(source_file) == GetFileContents(target_file)

        self._StartFtpServer(monkeypatch, embed_data.GetDataDirectory())
        try:
            # Upload file form local to FTP
            source_file = embed_data.GetDataFilename('files/source/alpha.txt')
            target_file = self._GetFTPUrl('alpha.txt')
            CopyAndCheckFiles(source_file, target_file)

            # Upload file form local to FTP, testing override
            source_file = embed_data.GetDataFilename('files/source/alpha.txt')
            target_file = self._GetFTPUrl('alpha.txt')
            with pytest.raises(FileAlreadyExistsError):
                CopyAndCheckFiles(source_file, target_file, override=False,)

            # Download file to local
            source_file = self._GetFTPUrl('alpha.txt')
            target_file = embed_data.GetDataFilename('alpha_copied_from_ftp.txt')
            CopyAndCheckFiles(source_file, target_file)
        finally:
            self._StopFtpServer()


    def testFTPCreateFile(self, monkeypatch, embed_data):
        self._StartFtpServer(monkeypatch, embed_data.GetDataDirectory())
        try:
            target_file = self._GetFTPUrl('ftp.txt')
            contents = 'This is a new file.'
            CreateFile(
                target_file,
                contents
            )
            assert GetFileContents(target_file) == contents

        finally:
            self._StopFtpServer()


    def testFTPIsFile(self, monkeypatch, embed_data):
        self._StartFtpServer(monkeypatch, embed_data.GetDataDirectory())
        try:
            assert IsFile(self._GetFTPUrl('file.txt')) == True
            assert IsFile(self._GetFTPUrl('files/source/alpha.txt')) == True
            assert IsFile(self._GetFTPUrl('doesnt_exist')) == False
            assert IsFile(self._GetFTPUrl('files/doesnt_exist')) == False
        finally:
            self._StopFtpServer()


    def testFTPListFiles(self, monkeypatch, embed_data):
        self._StartFtpServer(monkeypatch, embed_data.GetDataDirectory())
        try:
            # List FTP files
            assert ListFiles(self._GetFTPUrl('files/source')) == ['alpha.txt', 'bravo.txt', 'subfolder']

            # Try listing a directory that does not exist
            assert ListFiles(self._GetFTPUrl('/files/non-existent')) is None
        finally:
            self._StopFtpServer()


    def testFTPMakeDirs(self, monkeypatch, embed_data):
        self._StartFtpServer(monkeypatch, embed_data.GetDataDirectory())

        try:
            CreateDirectory(self._GetFTPUrl('/ftp_dir1'))
            assert os.path.isdir(embed_data.GetDataFilename('ftp_dir1'))

        finally:
            self._StopFtpServer()


    def testStandardizePath(self):
        assert StandardizePath('c:/alpha\\bravo') == 'c:/alpha/bravo'

        assert StandardizePath('c:\\alpha\\bravo\\', strip=False) == 'c:/alpha/bravo/'
        assert StandardizePath('c:\\alpha\\bravo\\', strip=True) == 'c:/alpha/bravo'

        assert StandardizePath('c:\\alpha\\bravo') == 'c:/alpha/bravo'

        assert StandardizePath('c:/alpha/bravo') == 'c:/alpha/bravo'

        assert StandardizePath('') == ''


    def testNormalizePath(self):
        assert NormalizePath('c:/alpha/zulu/../bravo') == os.path.normpath('c:/alpha/bravo')
        assert NormalizePath('') == '.'


    def testNormStandardPath(self):
        assert NormStandardPath('c:/alpha/zulu/../bravo') == 'c:/alpha/bravo'
        assert NormStandardPath('c:/alpha/../../../bravo/charlie') == '../bravo/charlie'

        assert NormStandardPath('/alpha/bravo') == '/alpha/bravo'
        assert NormStandardPath('/alpha/zulu/../bravo') == '/alpha/bravo'

        assert NormStandardPath('') == '.'


    def testCanonicalPath(self):
        if sys.platform == 'win32':
            assert CanonicalPath('X:/One/Two/Three') == 'x:\\one\\two\\three'
            obtained = CanonicalPath('Alpha')
            expected = os.path.abspath('Alpha').lower()
            assert obtained == expected

            obtained = CanonicalPath('../other/../Bravo')
            expected = os.path.abspath('../Bravo').lower()
            assert obtained == expected
        else:
            assert CanonicalPath('/home/SuperUser/Directory/../Shared') == '/home/SuperUser/Shared'
            obtained = CanonicalPath('Alpha')
            expected = os.path.abspath('Alpha')
            assert obtained == expected

            obtained = CanonicalPath('../other/../Bravo')
            expected = os.path.abspath('../Bravo')
            assert obtained == expected


    def testCheckIsFile(self, monkeypatch, embed_data):
        # assert not raises Exception
        CheckIsFile(embed_data.GetDataFilename('file.txt'))

        with pytest.raises(FileNotFoundError):
            CheckIsFile(embed_data.GetDataFilename('MISSING_FILE'))

        with pytest.raises(FileNotFoundError):
            CheckIsFile(embed_data.GetDataDirectory())  # Not a file

        self._StartFtpServer(monkeypatch, embed_data.GetDataDirectory())
        try:
            # assert not raises Exception
            CheckIsFile(self._GetFTPUrl('file.txt'))
            with pytest.raises(FileNotFoundError):
                CheckIsFile(self._GetFTPUrl('MISSING_FILE'))
            with pytest.raises(FileNotFoundError):
                CheckIsFile(self._GetFTPUrl('.'))  # Not a file
        finally:
            self._StopFtpServer()


    def testCheckIsDir(self, monkeypatch, embed_data):
        # assert not raises Exception
        CheckIsDir(embed_data.GetDataDirectory())

        with pytest.raises(DirectoryNotFoundError):
            CheckIsDir(embed_data.GetDataFilename('MISSING_DIR'))

        with pytest.raises(DirectoryNotFoundError):
            CheckIsDir(embed_data.GetDataFilename('file.txt'))  # Not a directory

        self._StartFtpServer(monkeypatch, embed_data.GetDataDirectory())
        try:
            # assert not raises Exception
            CheckIsDir(self._GetFTPUrl('.'))

            with pytest.raises(DirectoryNotFoundError):
                CheckIsDir(self._GetFTPUrl('MISSING_DIR'))

            with pytest.raises(DirectoryNotFoundError):
                CheckIsDir(self._GetFTPUrl('file.txt'))  # Not a directory
        finally:
            self._StopFtpServer()



    def testGetMTime__slow(self, embed_data):
        '''
        Tests modification time for files and directories (mtime for a directory should be the
        greatest mtime of files within it)
        '''
        import time

        # Test needs some time to sleep between creation of files, so they have time to change
        if sys.platform.startswith('win'):
            sleep_time = 0.01
        else:
            # Some linux distros cannot differentiate mtimes within a 1 second resolution
            sleep_time = 1

        # Make sure our data dir doesn't have leftovers from previous tests
        assert not os.path.isdir(embed_data.GetDataDirectory(create_dir=False))

        # GetMTime works for files and directories
        # For files, it is basically the same as os.path.getmtime
        some_file = embed_data.GetDataFilename('file')
        CreateFile(some_file, contents='')

        assert GetMTime(some_file) == os.path.getmtime(some_file)

        # Empty directories work like files
        CreateDirectory(embed_data.GetDataFilename('base_dir'))
        mtime = GetMTime(embed_data.GetDataFilename('base_dir'))
        assert mtime == os.path.getmtime(embed_data.GetDataFilename('base_dir'))

        # Creating a file within that directory should increase the overall mtime
        time.sleep(sleep_time)
        CreateFile(embed_data.GetDataFilename('base_dir/1.txt'), contents='')
        old_mtime, mtime = mtime, GetMTime(embed_data.GetDataFilename('base_dir'))
        assert mtime > old_mtime

        # Same for sub directories
        time.sleep(sleep_time)
        CreateDirectory(embed_data.GetDataFilename('base_dir/sub_dir'))
        old_mtime, mtime = mtime, GetMTime(embed_data.GetDataFilename('base_dir'))
        assert mtime > old_mtime

        # Files in a sub directory
        time.sleep(sleep_time)
        CreateDirectory(embed_data.GetDataFilename('base_dir/sub_dir/2.txt'))
        old_mtime, mtime = mtime, GetMTime(embed_data.GetDataFilename('base_dir'))
        assert mtime > old_mtime

        # Or sub-sub directories
        time.sleep(sleep_time)
        CreateDirectory(embed_data.GetDataFilename('base_dir/sub_dir/sub_sub_dir'))
        old_mtime, mtime = mtime, GetMTime(embed_data.GetDataFilename('base_dir'))
        assert mtime > old_mtime


    def testHandleContents(self):
        from etk11.filesystem import _filesystem
        HandleContents = _filesystem._HandleContentsEol
        assert 'a\r\nb' == HandleContents('a\nb', _filesystem.EOL_STYLE_WINDOWS)
        assert 'a\r\nb' == HandleContents('a\r\nb', _filesystem.EOL_STYLE_WINDOWS)
        assert 'a\r\nb' == HandleContents('a\rb', _filesystem.EOL_STYLE_WINDOWS)

        assert 'a\rb' == HandleContents('a\rb', _filesystem.EOL_STYLE_MAC)
        assert 'a\rb' == HandleContents('a\r\nb', _filesystem.EOL_STYLE_MAC)
        assert 'a\rb' == HandleContents('a\nb', _filesystem.EOL_STYLE_MAC)
        assert 'a\rb\r' == HandleContents('a\nb\n', _filesystem.EOL_STYLE_MAC)

        assert 'a\nb' == HandleContents('a\rb', _filesystem.EOL_STYLE_UNIX)
        assert 'a\nb' == HandleContents('a\r\nb', _filesystem.EOL_STYLE_UNIX)
        assert 'a\nb' == HandleContents('a\nb', _filesystem.EOL_STYLE_UNIX)
        assert 'a\nb\n' == HandleContents('a\nb\n', _filesystem.EOL_STYLE_UNIX)



    #===============================================================================================
    # FTP server utility functions
    #===============================================================================================
    def _StartFtpServer(self, monkeypatch, directory):
        '''
        Starts a phony ftp-server for testing purpose.

        Usage:
            self._StartFtpServer()
            try:
                # ...
            finally:
                self._StopFtpServer()
        '''
        from pyftpdlib import ftpserver
        import logging

        # Redirect ftpserver messages to "logging"
        monkeypatch.setattr(ftpserver, 'log', logging.info)
        monkeypatch.setattr(ftpserver, 'logline', logging.info)
        monkeypatch.setattr(ftpserver, 'logerror', logging.info)

        from _phony_ftp_server import PhonyFtpServer
        self._ftpd = PhonyFtpServer(directory)
        self._ftp_port = self._ftpd.Start()


    def _GetAnonymousFTPDir(self, sub_dir):
        base_dir = 'ftp://127.0.0.1:%s' % self._ftp_port
        return '/'.join([base_dir, sub_dir])


    def _GetFTPUrl(self, sub_dir):
        base_dir = 'ftp://dev:123@127.0.0.1:%s' % self._ftp_port
        return '/'.join([base_dir, sub_dir])


    def _StopFtpServer(self):
        '''
        Stops the phony ftp-server previously started with "_StartFtpServer" method.
        '''
        self._ftpd.Stop()


    def testListMappedNetworkDrives(self, embed_data, monkeypatch):
        from etk11.filesystem import ListMappedNetworkDrives, _filesystem

        if sys.platform != 'win32':
            return

        def _MockWindowsNetCommand(*args):
            net_use_output = GetFileContents(embed_data.GetDataFilename('net_use.txt'))
            return net_use_output.replace("\n", EOL_STYLE_WINDOWS)

        monkeypatch.setattr(_filesystem, '_CallWindowsNetCommand', _MockWindowsNetCommand)
        mapped_drives = ListMappedNetworkDrives()
        assert mapped_drives[0][0] == 'H:'
        assert mapped_drives[0][1] == r'\\br\CXMR'
        assert mapped_drives[0][2] == True
        assert mapped_drives[1][0] == 'O:'
        assert mapped_drives[1][2] == False
        assert mapped_drives[2][0] == 'P:'
