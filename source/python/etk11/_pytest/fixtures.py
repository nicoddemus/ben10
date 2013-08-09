import pytest



#===================================================================================================
# MultipleFilesNotFound
#===================================================================================================
class MultipleFilesNotFound(RuntimeError):

    def __init__(self, filenames):
        self._filenames = filenames

    def __str__(self):
        return 'Files not found: %s' % ','.join(self._filenames)



#===================================================================================================
# embed_data
#===================================================================================================

class _EmbedDataFixture(object):
    '''
    This fixture create a temporary data directory for the test.
    The contents of the directory is a copy of a 'data-directory' with the same name of the module
    (without the .py extension).
    
    :ivar boolean delete_dir:
        Determines if the data-directory is deleted at finalization. Default to True.
        This may be used for debugging purposes to examine the data-directory as left by the test.
        Remember that each test recreates the entire data directory.
    '''

    def __init__(self, request):

        # @ivar _module_dir: str
        # The module name.
        self._module_name = request.module.__name__.split('.')[-1]
        self._function_name = request.function.__name__

        # @ivar _source_dir: str
        # The source directory name.
        # The contents of this directories populates the data-directory
        # This name is create based on the module_name
        self._source_dir = request.fspath.dirname + '/' + self._module_name

        # @ivar _data_dir: str
        # The data directory name
        # This name is created based on the module_name
        # Adding the function name to enable parallel run of tests in the same module (pytest_xdist)
        self._data_dir = self._module_name.replace('pytest_', 'data_')
        self._data_dir += '__' + self._function_name

        # @ivar _created: boolean
        # Internal flag that controls whether we created the data-directory or not.
        # - False: Initial state. The data-directory was not created yet
        # - True: The directory was created. The directory is created lazily, that is, when needed.
        self._created = False

        # @ivar _finalize: boolean
        # Whether we have finalized.
        self._finalized = False

        self.delete_dir = True


    def CreateDataDir(self):
        '''
        Creates the data-directory as a copy of the source directory.
        
        :rtype: str
        :returns:
            Path to created data dir
        '''
        from etk11.filesystem import DeleteDirectory, CopyDirectory, IsDir, CreateDirectory
        from etk11.is_frozen import IsFrozen
        import os

        assert not self._finalized, "Oops. Finalizer has been called in the middle. Something is wrong."
        if self._created:
            return self._data_dir

        if os.path.isdir(self._data_dir):
            DeleteDirectory(self._data_dir)

        if IsFrozen():
            raise RuntimeError("_EmbedDataFixture is not ready for execution inside an executable.")


        if IsDir(self._source_dir):
            CopyDirectory(self._source_dir, self._data_dir)
        else:
            CreateDirectory(self._data_dir)

        self._created = True
        return self._data_dir


    def GetDataDirectory(self, absolute=False, create_dir=True):
        '''
        :param bool absolute:
            If True, returns the path as an abspath

        :param bool create_dir:
            If True (default) creates the data directory.
            
        :rtype: str
        :returns:
            Returns the data-directory name.

        @remarks:
            This method triggers the data-directory creation. 
        '''
        if create_dir:
            self.CreateDataDir()

        if absolute:
            import os
            from etk11.filesystem import StandardizePath
            return StandardizePath(os.path.abspath(self._data_dir))

        return self._data_dir


    def GetDataFilename(self, *parts, **kwargs):
        '''
        Returns a full filename in the data-directory.
        
        @params parts: list(str)
            Path parts. Each part is joined to form a path.
            
        :keyword bool absolute:
            If True, returns the filename as an abspath
            
        :rtype: str
        :returns:
            The full path prefixed with the data-directory.

        @remarks:
            This method triggers the data-directory creation. 
        '''
        # Make sure the data-dir exists.
        self.CreateDataDir()

        result = [self._data_dir] + list(parts)
        result = '/'.join(result)

        if 'absolute' in kwargs and kwargs['absolute']:
            import os
            from etk11.filesystem import StandardizePath
            result = StandardizePath(os.path.abspath(result))

        return result


    def Finalizer(self):
        '''
        Deletes the data-directory upon finalizing (see FixtureRequest.addfinalizer)
        '''
        from etk11.filesystem import DeleteDirectory

        if self.delete_dir:
            DeleteDirectory(self._data_dir, skip_on_error=True)
        self._finalized = True


    def AssertEqualFiles(self, filename1, filename2):
        '''
        Compare two files contents, showing a nice diff view if the files differs.
        
        Searches for the filenames both outside or inside the data directory.
        
        @filename1: str

        @filename2: str
        '''
        from etk11.filesystem import GetFileLines
        import os

        def FindFile(filename):
            r_filename = filename
            if not os.path.isfile(r_filename):
                r_filename = self.GetDataFilename(r_filename)
            if not os.path.isfile(r_filename):
                raise MultipleFilesNotFound([filename, r_filename])
            return r_filename

        filename1 = FindFile(filename1)
        filename2 = FindFile(filename2)

        obtained = GetFileLines(filename1)
        expected = GetFileLines(filename2)

        if obtained != expected:
            import difflib
            diff = ['*** FILENAME: ' + filename1]
            diff += [i for i in difflib.context_diff(obtained, expected)]
            diff = '\n'.join(diff)
            raise AssertionError(diff)


@pytest.fixture
def embed_data(request):
    '''
    Create a temporary directory with input data for the test.
    The directory contents is copied from a directory with the same name as the module located in
    the same directory of the test module.
    '''
    result = _EmbedDataFixture(request)
    request.addfinalizer(result.Finalizer)
    return result
