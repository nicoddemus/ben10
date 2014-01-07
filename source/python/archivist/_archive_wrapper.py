from __future__ import with_statement
from ben10.filesystem import StandardizePath
from ben10.foundation.decorators import Implements
from ben10.interface import Interface, ImplementsInterface
import os



#===================================================================================================
# IArchiveWrapper
#===================================================================================================
class IArchiveWrapper(Interface):
    def __init__(self, filename):
        '''
        Creates the wrapper opening the given archive.

        :param str filename:
            The name of the archive file.
        '''

    def ListFilenames(self):
        '''
        List archive filenames.

        :rtype: list(str)
        '''

    def ListDirs(self):
        '''
        List archive directories.

        :rtype: list(str)
        '''

    def ReadFile(self, filename):
        '''
        Read the contents of the given filename stored inside the archive.

        :param str filename:
            A filename found inside the archive.

        :rtype: str
        :returns:
            The contents of the file.
        '''



#===================================================================================================
# ZipWrapper
#===================================================================================================
class ZipWrapper(object):
    '''
    ArchiveWrapper for zipfiles
    '''

    ImplementsInterface(IArchiveWrapper)

    def __init__(self, filename):
        import zipfile
        self.wrapped = zipfile.ZipFile(filename)


    @Implements(IArchiveWrapper.ListFilenames)
    def ListFilenames(self):
        return self.wrapped.namelist()


    @Implements(IArchiveWrapper.ListDirs)
    def ListDirs(self):
        result = []
        for i in self.ListFilenames():
            assert not i.endswith('/'), "Filenames ending with '/' couldn't be reproduced on tests."
            result.append(os.path.dirname(i))
        return sorted(result)


    @Implements(IArchiveWrapper.ReadFile)
    def ReadFile(self, filename):
        return self.wrapped.read(filename)



#===================================================================================================
# RarWrapper
#===================================================================================================
class RarWrapper(object):
    '''
    ArchiveWrapper for rarfiles
    '''

    ImplementsInterface(IArchiveWrapper)

    def __init__(self, filename):
        from ._rarfile import Rarfile
        self.wrapped = Rarfile().CreateRarFile(filename)


    def ListFilenames(self):
        result = self.wrapped.namelist()
        result = [StandardizePath(i) for i in result]
        return result


    def ListDirs(self):
        result = []
        for i in self.ListFilenames():
            if self.wrapped.getinfo(i).isdir():
                result.append(i)
            else:
                result.append(os.path.dirname(i))
        return sorted(result)


    def ReadFile(self, filename):
        return self.wrapped.read(filename)



#===================================================================================================
# CreateArchiveWrapper
#===================================================================================================
def CreateArchiveWrapper(filename):
    '''
    :param str filename:
        An archive file. Its type will be determined from its extension (.rar, .zip)

    :rtype: IArchiveWrapper
    :returns:
        An archive wrapper appropiate for the given file type
    '''
    extension = os.path.splitext(filename)[1]
    if extension == '.zip':
        return ZipWrapper(filename)
    if extension == '.rar':
        return RarWrapper(filename)
    else:
        raise NotImplementedError(extension)
