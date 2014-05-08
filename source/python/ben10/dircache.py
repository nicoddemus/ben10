from archivist import Archivist
from ben10.filesystem import (CopyDirectory, CopyFile, CreateLink, CreateTemporaryDirectory,
    DeleteDirectory, DeleteLink, Exists, IsLink)
import os



#===================================================================================================
# CacheDisabled
#===================================================================================================
class CacheDisabled(RuntimeError):
    '''
    Exception raised when any cache operation is performed in a DirCache instance that have no cache
    enabled.
    '''



#===================================================================================================
# DirCache
#===================================================================================================
class DirCache(object):

    '''
    DirCache is an utility that make a remote directory/archive available locally using a local
    cache.

    Use case:
    You want to have some remote resource, say 'http://.../remote.zip' contents available in a local
    directory (local):

        dir_cache = DirCache(
            'http://.../remote.zip',
            'local',
            'c:/dircache',
        )
        dir_cache.MakeLocallyAvailable()
        os.path.isdir('local')

    This will make the contents of remote.zip available inside the "local" directory. Behind the
    scenes we have an indirection, where the contents are stored in the cache directory
    c:/dircache/remote and "local" is actually a link to c:/dircache/remote.

        c:/dircache/remote.zip
        c:/dircache/remote

        ./local [c:/dircache/remote]

    The local cache directory (c:/dircache) is handy when you have many local directories from the
    same remote resource. This is the case of a Continuous Integration slave machine, that can
    execute many jobs that requires the same resources.
    '''

    def __init__(self, remote, local_dir, cache_dir=None):
        '''
        :param str remote:
            A remote directory or archive.
            This can be a local directory, ftp or http url.

        :param str local_dir:
            The local directory to place the remote contents into.
            If cache is enabled, DirCache will actually create a link with this name pointing to the
            real contents available on cache_dir.
            If cache is disabled, the remote contents are copied to the local directory.

        :param str|None cache_dir:
            A base directory to store the actual remote content.
            If None disables the cache for this instance of DirCache.
        '''
        self.__remote = remote
        self.__local_dir = local_dir

        self.__filename = os.path.basename(self.__remote)
        self.__name = os.path.splitext(self.__filename)[0]

        if cache_dir is None:
            self.__cache_base_dir = None
            self.__cache_dir = None
        else:
            self.__cache_base_dir = os.path.abspath(cache_dir)
            self.__cache_dir = self.__cache_base_dir + '/' + self.__name


    def CreateCache(self, force=False):
        '''
        Downloads the remote resource into the local cache.
        This method does not touch the local_dir.

        :param bool force:
            Forces the download, even if the local cache already exists.
        '''
        if self.CacheExists() and not force:
            return
        if Exists(self.__cache_dir):
            DeleteDirectory(self.__cache_dir)

        self._DownloadRemote(self.__cache_base_dir, self.__cache_dir)


    def _DownloadRemote(self, extract_dir, target_dir):
        '''
        Internal method that actually downloads the remote resource. Handles archive remotes.

        :param str extract_dir:
            A temporary directory where to extract archive remote resources.
            Only used if the remote resource is an archive.
        :param str target_dir:
            The final destination of the remote resource.
        '''
        if os.path.splitext(self.__filename)[1] in ('.zip', '.tbz2'):
            local_archive_filename = extract_dir + '/' + self.__filename
            CopyFile(self.__remote, local_archive_filename)
            archivist = Archivist()
            archivist.ExtractArchive(local_archive_filename, target_dir)
        else:
            CopyDirectory(self.__remote, target_dir)


    def CreateLocal(self):
        '''
        Makes a remote resource locally available, downloading it if necessary.
        '''
        self.DeleteLocal()
        if self.IsCacheEnabled():
            self.CreateCache()
            self._CreateLocal()
        else:
            with CreateTemporaryDirectory() as tmp_dir:
                self._DownloadRemote(tmp_dir, self.__local_dir)


    def _CreateLocal(self):
        CreateLink(self.__cache_dir, self.__local_dir)


    def DeleteLocal(self):
        '''
        Deletes the local resource.

        The remote and cache content are not touched.
        '''
        if Exists(self.__local_dir):
            if self.IsCacheEnabled():
                assert IsLink(self.__local_dir), "%s: The local directory is expected to be a link." % self.__local
                DeleteLink(self.__local_dir)
            else:
                assert not IsLink(self.__local_dir), "%s: The local directory is expected to be a directory." % self.__local
                DeleteDirectory(self.__local_dir)


    def GetFilename(self):
        '''
        Returns the filename, as defined by the remote resource.

        This may differ from the resource local directory.

        :returns str:
        '''
        return self.__filename


    def GetName(self):
        '''
        Returns the name, as defined by the remote resource.

        :returns str:
        '''
        return self.__name


    def Remote(self):
        '''
        Returns the local directory.

        :returns str:
        '''
        return self.__remote


    def LocalDir(self):
        '''
        Returns the local directory.

        :returns str:
        '''
        return self.__local_dir


    def RemoteExists(self):
        '''
        Checks if the remote resource exists.

        :returns bool:
        '''
        return Exists(self.__remote)


    def LocalExists(self):
        '''
        Checks if the local resource exists.

        :returns bool:
        '''
        return Exists(self.__local_dir)


    def IsCacheEnabled(self):
        return self.__cache_dir is not None


    def CacheBaseDir(self):
        '''
        Returns the cache base directory.

        :returns str:
        '''
        if not self.IsCacheEnabled():
            raise CacheDisabled()
        return self.__cache_base_dir


    def CacheDir(self):
        '''
        Returns this resource actual cache directory.
        '''
        if not self.IsCacheEnabled():
            raise CacheDisabled()
        return self.__cache_dir


    def CacheExists(self):
        '''
        Checks if the local cache exists.

        :returns bool:
        '''
        if not self.IsCacheEnabled():
            raise CacheDisabled()
        return Exists(self.__cache_dir)
