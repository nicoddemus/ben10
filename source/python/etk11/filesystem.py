'''
This module contains a selection of file related functions that can be used anywhere.

Some sort of wrapper for common builtin 'os' operations with a nicer interface.

These functions abstract file location, most of them work for either local, ftp or http protocols

FTP LIMITATIONS:
================

Right now, all functions that require a FTP connection are ALWAYS creating and closing a FTP Host.
    
Keep in mind that this process can be slow if you perform many of such operations in sequence. 
'''
import os
import re
import sys

from ftputil.ftp_error import FTPIOError  # @UnusedImport
from ftputil.ftp_error import PermanentError  # @UnresolvedImport @UnusedImport @Reimport

from etk11.reraise import Reraise


#=======================================================================================================================
# Exceptions
#=======================================================================================================================
#-----------------------------------------------------------------------------------------------------------------------
# UnknownPlatformError
#-----------------------------------------------------------------------------------------------------------------------
class UnknownPlatformError(RuntimeError):

    def __init__(self, platform):
        self.platform = platform
        RuntimeError.__init__(self, 'Unknown platform "%s".' % platform)


#-----------------------------------------------------------------------------------------------------------------------
# NotImplementedProtocol
#-----------------------------------------------------------------------------------------------------------------------
class NotImplementedProtocol(RuntimeError):
    def __init__(self, protocol):
        RuntimeError.__init__(self, "Function can't handle protocol '%s'." % protocol)
        self.protocol = protocol


#-----------------------------------------------------------------------------------------------------------------------
# NotImplementedForRemotePathError
#-----------------------------------------------------------------------------------------------------------------------
class NotImplementedForRemotePathError(NotImplementedError):
    def __init__(self):
        NotImplementedError.__init__(self, 'Function not implemented remote paths.')


#-----------------------------------------------------------------------------------------------------------------------
# FileError
#-----------------------------------------------------------------------------------------------------------------------
class FileError(RuntimeError):
    def __init__(self, filename):
        self.filename = filename
        RuntimeError.__init__(self, self.GetMessage(filename))

    def GetMessage(self, filename):
        raise NotImplementedError()


#-----------------------------------------------------------------------------------------------------------------------
# FileNotFoundError
#-----------------------------------------------------------------------------------------------------------------------
class FileNotFoundError(FileError):
    def GetMessage(self, filename):
        return 'File "%s" not found.' % filename


#-----------------------------------------------------------------------------------------------------------------------
# CantOpenFileThroughProxyError
#-----------------------------------------------------------------------------------------------------------------------
class CantOpenFileThroughProxyError(FileError):
    def GetMessage(self, filename):
        return 'Can\'t open file "%s" through a proxy.' % filename


#-----------------------------------------------------------------------------------------------------------------------
# DirectoryNotFoundError
#-----------------------------------------------------------------------------------------------------------------------
class DirectoryNotFoundError(FileError):
    def GetMessage(self, directory):
        return 'Directory "%s" not found.' % directory


#-----------------------------------------------------------------------------------------------------------------------
# DirectoryAlreadyExistsError
#-----------------------------------------------------------------------------------------------------------------------
class DirectoryAlreadyExistsError(FileError):
    def GetMessage(self, directory):
        return 'Directory "%s" already exists.' % directory


#-----------------------------------------------------------------------------------------------------------------------
# ServerTimeoutError
#-----------------------------------------------------------------------------------------------------------------------
class ServerTimeoutError(FileError):
    def GetMessage(self, filename):
        return 'Server timeout while accessing file "%s"' % filename


#-----------------------------------------------------------------------------------------------------------------------
# FileAlreadyExistsError
#-----------------------------------------------------------------------------------------------------------------------
class FileAlreadyExistsError(FileError):
    def GetMessage(self, filename):
        return 'File "%s" already exists.' % filename


#-----------------------------------------------------------------------------------------------------------------------
# FileOnlyActionError
#-----------------------------------------------------------------------------------------------------------------------
class FileOnlyActionError(FileError):
    def GetMessage(self, filename):
        return 'Action performed over "%s" only possible with a file.' % filename



#=======================================================================================================================
# Constants
#=======================================================================================================================
SEPARATOR_UNIX = '/'
SEPARATOR_WINDOWS = '\\'
EOL_STYLE_NONE = None  # Binary files
EOL_STYLE_UNIX = '\n'
EOL_STYLE_WINDOWS = '\r\n'
EOL_STYLE_MAC = '\r'

def _GetNativeEolStyle(platform=sys.platform):
    _NATIVE_EOL_STYLE_MAP = {
        'win32' : EOL_STYLE_WINDOWS,
        'linux2' : EOL_STYLE_UNIX,
        'darwin' : EOL_STYLE_MAC,
    }
    result = _NATIVE_EOL_STYLE_MAP.get(platform)

    if result is None:
        raise UnknownPlatformError(platform)

    return result

EOL_STYLE_NATIVE = _GetNativeEolStyle()



#=======================================================================================================================
# NormalizePath
#=======================================================================================================================
def NormalizePath(path):
    '''
    Normalizes a path maintaining the final slashes.
    
    Some environment variables need the final slash in order to work.
    
    Ex. The SOURCES_DIR set by subversion must end with a slash because of the way it is used
    in the Visual Studio projects.
     
    :param str path:
        The path to normalize.
        
    :rtype: str
    :returns:
        Normalized path
    '''
    if path.endswith('/') or path.endswith('\\'):
        slash = os.path.sep
    else:
        slash = ''
    return os.path.normpath(path) + slash


#=======================================================================================================================
# CanonicalPath
#=======================================================================================================================
def CanonicalPath(path):
    '''
    Returns a version of a path that is unique.

    Given two paths path1 and path2:
        CanonicalPath(path1) == CanonicalPath(path2) if and only if they represent the same file on the host OS. 
        Takes account of case, slashes and relative paths.

    :param str path:
        The original path.

    :rtype: str
    :returns:
        The unique path.
    '''
    path = os.path.normpath(path)
    path = os.path.abspath(path)
    path = os.path.normcase(path)

    return path


#===================================================================================================
# StandardizePath
#===================================================================================================
def StandardizePath(path, strip=False):
    '''
    Replaces all slashes and backslashes with the target separator
    
    StandardPath:
        We are defining that the standard-path is the one with only back-slashes in it, either
        on Windows or any other platform.
        
    :param bool strip:
        If True, removes additional slashes from the end of the path.
    '''
    path = path.replace(SEPARATOR_WINDOWS, SEPARATOR_UNIX)
    if strip:
        path = path.rstrip(SEPARATOR_UNIX)
    return path



#===================================================================================================
# NormStandardPath
#===================================================================================================
def NormStandardPath(path):
    '''
    Normalizes a standard path (posixpath.normpath) maintaining any slashes at the end of the path. 

    Normalize:
        Removes any local references in the path "/../"

    StandardPath:
        We are defining that the standard-path is the one with only back-slashes in it, either
        on Windows or any other platform. 
    '''
    import posixpath
    if path.endswith('/'):
        slash = '/'
    else:
        slash = ''
    return posixpath.normpath(path) + slash



#===================================================================================================
# CreateMD5
#===================================================================================================
def CreateMD5(source_filename, target_filename=None):
    '''
    Creates a md5 file from a source file (contents are the md5 hash of source file)
    
    :param str source_filename:
        Path to source file
        
    :type target_filename: str or None
    :param target_filename:
        Name of the target file with the md5 contents
        
        If None, defaults to source_filename + '.md5'
    '''
    if target_filename is None:
        target_filename = source_filename + '.md5'

    # Obtain MD5 hex
    from etk11.hash import Md5Hex
    md5_contents = Md5Hex(filename=source_filename)

    # Write MD5 hash to a file
    CreateFile(target_filename, md5_contents)



MD5_SKIP = 'md5_skip'  # Returned to show that a file copy was skipped because it hasn't changed.
#===================================================================================================
# CopyFile
#===================================================================================================
def CopyFile(source_filename, target_filename, override=True, md5_check=False, copy_symlink=True):
    '''
    Copy a file from source to target.

    :param  source_filename:
        @see _DoCopyFile

    :param  target_filename:
        @see _DoCopyFile
        
    :param bool md5_check:
        If True, checks md5 files (of both source and target files), if they match, skip this copy
        and return MD5_SKIP
        
        Md5 files are assumed to be {source, target} + '.md5'
        
        If any file is missing (source, target or md5), the copy will always be made. 

    :param  copy_symlink:
        @see _DoCopyFile

    :raises FileAlreadyExistsError:
        If target_filename already exists, and override is False
        
    :raises NotImplementedProtocol:
        If file protocol is not accepted
        
        Protocols allowed are:
            source_filename: local, ftp, http
            target_filename: local, ftp
            
    :rtype: None | MD5_SKIP
    :returns:
        MD5_SKIP if the file was not copied because there was a matching .md5 file
        
    .. see:: FTP LIMITATIONS at this module's doc for performance issues information
    '''
    # Check override
    if not override and Exists(target_filename):
        raise FileAlreadyExistsError(target_filename)


    # If we enabled md5 checks, ignore copy of files that haven't changed their md5 contents.
    if md5_check:
        source_md5_filename = source_filename + '.md5'
        target_md5_filename = target_filename + '.md5'

        # If all files already exist, and md5's are the same, skip this copy
        files = [source_filename, source_md5_filename, target_filename, target_md5_filename]
        if all(map(Exists, files)):
            if GetFileContents(source_md5_filename) == GetFileContents(target_md5_filename):
                return MD5_SKIP

    # Copy source file
    _DoCopyFile(source_filename, target_filename, copy_symlink=copy_symlink)

    # Copy md5 file after the file itself was copied, for safety
    if md5_check:
        try:
            _DoCopyFile(source_md5_filename, target_md5_filename)
        except FileNotFoundError:
            pass  # Md5 does not exist, ignore it


def _DoCopyFile(source_filename, target_filename, copy_symlink=True):
    '''
    :param str source_filename:
        The source filename.
        Schemas: local, ftp, http

    :param str target_filename:
        Target filename.
        Schemas: local, ftp

    :param  copy_symlink:
        @see _CopyFileLocal
        
    :raises FileNotFoundError:
        If source_filename does not exist
    '''
    from urlparse import urlparse

    source_url = urlparse(source_filename)
    target_url = urlparse(target_filename)

    if _UrlIsLocal(source_url):
        if not Exists(source_filename):
            raise FileNotFoundError(source_filename)

        if _UrlIsLocal(target_url):
            # local to local
            _CopyFileLocal(source_filename, target_filename, copy_symlink=copy_symlink)
        elif target_url.scheme in ['ftp']:
            # local to remote
            RemoteImpl.FTPUploadFileToUrl(source_filename, target_url)
        else:
            raise NotImplementedProtocol(target_url.scheme)

    elif source_url.scheme in ['http', 'ftp']:
        if _UrlIsLocal(target_url):
            # HTTP/FTP to local
            RemoteImpl.DownloadUrlToFile(source_url, target_filename)
        else:
            # HTTP/FTP to other ==> NotImplemented
            raise NotImplementedProtocol(target_url.scheme)
    else:
        raise NotImplementedProtocol(source_url.scheme)


def _CopyFileLocal(source_filename, target_filename, copy_symlink=True):
    '''
    Copy a file locally to a directory.

    :param str source_filename:
        The filename to copy from.

    :param str target_filename:
        The filename to copy to.

    :param bool copy_symlink:
        If True and source_filename is a symlink, target_filename will also be created as
        a symlink.

        If False, the file being linked will be copied instead.
    '''
    import shutil
    try:
        # >>> Create the target_filename directory if necessary
        dir_name = os.path.dirname(target_filename)
        if dir_name and not os.path.isdir(dir_name):
            os.makedirs(dir_name)

        if copy_symlink and os.path.islink(source_filename):
            # >>> Delete the target_filename if it already exists
            if os.path.isfile(target_filename) or os.path.islink(target_filename):
                DeleteFile(target_filename)

            # >>> Obtain the relative path from link to source_filename (linkto)
            from path import path
            source_filename = path(source_filename)
            linkto = source_filename.readlink()

            # >>> Create the target_filename as a sym-link
            linkto.symlink(target_filename)
        else:
            shutil.copyfile(source_filename, target_filename)
            shutil.copymode(source_filename, target_filename)
    except Exception, e:
        Reraise(e, 'While executiong _filesystem._CopyFileLocal(%s, %s)' % (source_filename, target_filename))



#=======================================================================================================================
# CopyFiles
#=======================================================================================================================
def CopyFiles(source_dir, target_dir, create_target_dir=False):
    '''
    Copy files from the given source to the target.

    :param str source_dir:
        A filename, URL or a file mask.
        Ex.
            x:\etk11
            x:\etk11\*
            http://server/directory/file
            ftp://server/directory/file


    :param str target_dir:
        A directory or an URL
        Ex.
            d:\Temp
            ftp://server/directory

    :param bool create_target_dir:
        If True, creates the target path if it doesn't exists.
        
        
    :raises DirectoryNotFoundError:
        If target_dir does not exist, and create_target_dir is False

    .. see:: CopyFile for documentation on accepted protocols
    
    .. see:: FTP LIMITATIONS at this module's doc for performance issues information
    '''
    import fnmatch

    # Check if we were given a directory or a directory with mask
    if IsDir(source_dir):
        # Yes, it's a directory, copy everything from it
        source_mask = '*'
    else:
        # Split directory and mask
        source_dir, source_mask = os.path.split(source_dir)

    # Create directory if necessary
    if not IsDir(target_dir):
        if create_target_dir:
            CreateDirectory(target_dir)
        else:
            raise DirectoryNotFoundError(target_dir)

    # List and match files
    filenames = ListFiles(source_dir)

    # Check if we have a source directory
    if filenames is None:
        return

    # Copy files
    for i_filename in filenames:
        if fnmatch.fnmatch(i_filename, source_mask):
            source_path = source_dir + '/' + i_filename
            target_path = target_dir + '/' + i_filename

            if IsDir(source_path):
                # If we found a directory, copy it recursively
                CopyFiles(source_path, target_path, create_target_dir=True)
            else:
                CopyFile(source_path, target_path)



#===================================================================================================
# CopyFilesX
#===================================================================================================
def CopyFilesX(file_mapping):
    '''
    Copies files into directories, according to a file mapping
    
    :param list(tuple(str,str)) file_mapping:
        A list of mappings between the directory in the target and the source.
        For syntax, @see: ExtendedPathMask
        
    :rtype: list(tuple(str,str))
    :returns:
        List of files copied. (source_filename, target_filename)
        
    .. see:: FTP LIMITATIONS at this module's doc for performance issues information
    '''
    from .algorithms import FindFiles
    from etk11.extended_path_mask import ExtendedPathMask

    # List files that match the mapping
    files = []
    for i_target_path, i_source_path_mask in file_mapping:
        tree_recurse, flat_recurse, dirname, in_filters, out_filters = ExtendedPathMask.Split(i_source_path_mask)

        filenames = FindFiles(dirname, in_filters, out_filters, tree_recurse)
        for i_source_filename in filenames:
            if os.path.isdir(i_source_filename):
                continue  # Do not copy dirs

            i_target_filename = i_source_filename[len(dirname) + 1:]
            if flat_recurse:
                i_target_filename = os.path.basename(i_target_filename)
            i_target_filename = os.path.join(i_target_path, i_target_filename)

            files.append((
                StandardizePath(i_source_filename),
                StandardizePath(i_target_filename)
            ))

    # Copy files
    for i_source_filename, i_target_filename in files:
        # Create target dir if necessary
        target_dir = os.path.dirname(i_target_filename)
        CreateDirectory(target_dir)

        CopyFile(i_source_filename, i_target_filename)

    return files



#===================================================================================================
# IsFile
#===================================================================================================
def IsFile(path):
    '''
    :param str path:
        Path to a file (local or ftp)
        
    :raises NotImplementedProtocol:
        If checking for a non-local, non-ftp file
    
    :rtype: bool
    :returns:
        True if the file exists
        
    .. see:: FTP LIMITATIONS at this module's doc for performance issues information
    '''
    from urlparse import urlparse
    url = urlparse(path)

    if _UrlIsLocal(url):
        return os.path.isfile(path)

    elif url.scheme == 'ftp':
        return RemoteImpl.FTPIsFile(url)
    else:
        raise NotImplementedProtocol(url.scheme)



#===================================================================================================
# IsDir
#===================================================================================================
def IsDir(directory):
    '''
    :param str directory:
        A path

    :rtype: bool
    :returns:
        Returns whether the given path points to an existent directory.
        
    :raises NotImplementedProtocol:
        If the path protocol is not local or ftp
        
    .. see:: FTP LIMITATIONS at this module's doc for performance issues information
    '''
    from urlparse import urlparse
    directory_url = urlparse(directory)

    if _UrlIsLocal(directory_url):
        return os.path.isdir(directory)
    elif directory_url.scheme == 'ftp':
        return RemoteImpl.FTPIsDir(directory_url)
    else:
        raise NotImplementedProtocol(directory_url.scheme)



#=======================================================================================================================
# Exists
#=======================================================================================================================
def Exists(path):
    '''
    :rtype: bool
    :returns:
        True if the path already exists (either a file or a directory)
    
    .. see:: FTP LIMITATIONS at this module's doc for performance issues information
    '''
    return IsFile(path) or IsDir(path)



#=======================================================================================================================
# CopyDirectory
#=======================================================================================================================
def CopyDirectory(source_dir, target_dir, override=False):
    '''
    Recursively copy a directory tree.
    
    :param str source_dir:
        Where files will come from
    
    :param str target_dir:
        Where files will go to
    
    :param bool override:
        If True and target_dir already exists, it will be deleted before copying.

    :raises NotImplementedForRemotePathError:
        If trying to copy to/from remote directories
    '''
    _AssertIsLocal(source_dir)
    _AssertIsLocal(target_dir)

    if override and IsDir(target_dir):
        DeleteDirectory(target_dir, skip_on_error=False)

    import shutil
    shutil.copytree(source_dir, target_dir)



#===================================================================================================
# DeleteFile
#===================================================================================================
def DeleteFile(target_filename):
    '''
    Deletes the given local filename. 
    
    .. note:: If file doesn't exist this method has no effect.

    :param str target_filename:
        A local filename
        
    :raises NotImplementedForRemotePathError:
        If trying to delete a non-local path
        
    :raises FileOnlyActionError:
        Raised when filename refers to a directory.
    '''
    _AssertIsLocal(target_filename)

    try:
        if os.path.isfile(target_filename):
            os.remove(target_filename)
        elif IsDir(target_filename):
            raise FileOnlyActionError(target_filename)
    except Exception, e:
        Reraise(e, 'While executing filesystem.DeleteFile(%s)' % (target_filename))



#===================================================================================================
# AppendToFile
#===================================================================================================
def AppendToFile(filename, contents, eol_style=EOL_STYLE_NATIVE):
    '''
    Appends content to a local file.
    
    :param str filename:
    
    :param str contents:
    
    :type eol_style: EOL_STYLE_XXX constant
    :param eol_style:
        Replaces the EOL by the appropriate EOL depending on the eol_style value.
        Considers that all content is using only "\n" as EOL.
        
    :raises NotImplementedForRemotePathError:
        If trying to modify a non-local path
    '''
    _AssertIsLocal(filename)

    oss = open(filename, 'ab')
    try:
        contents = _HandleContentsEol(contents, eol_style)
        oss.write(contents)
    finally:
        oss.close()



#===================================================================================================
# MoveFile
#===================================================================================================
def MoveFile(source_filename, target_filename):
    '''
    Moves a file.
    
    :param str source_filename:
    
    :param str target_filename:
    
    :raises NotImplementedForRemotePathError:
        If trying to operate with non-local files.
    '''
    _AssertIsLocal(source_filename)
    _AssertIsLocal(target_filename)

    import shutil
    shutil.move(source_filename, target_filename)



#===================================================================================================
# MoveDirectory
#===================================================================================================
def MoveDirectory(source_dir, target_dir):
    '''
    Moves a directory.
    
    :param str source_dir:
    
    :param str target_dir:
    
    :raises NotImplementedError:
        If trying to move anything other than:
            Local dir -> local dir
            FTP dir -> FTP dir (same host)
    '''
    if not IsDir(source_dir):
        raise DirectoryNotFoundError(source_dir)

    if Exists(target_dir):
        raise DirectoryAlreadyExistsError(target_dir)

    from urlparse import urlparse
    source_url = urlparse(source_dir)
    target_url = urlparse(target_dir)

    # Local to local
    if _UrlIsLocal(source_url) and _UrlIsLocal(target_url):
        import shutil
        shutil.move(source_dir, target_dir)

    # FTP to FTP
    elif source_url.scheme == 'ftp' and target_url.scheme == 'ftp':
        if source_url.hostname != target_url.hostname:
            raise NotImplementedError('Can only move FTP directories in the same host')
        return RemoteImpl.FTPMoveDirectory(source_url, target_url)
    else:
        raise NotImplementedError('Can only move directories local->local or ftp->ftp')


#===================================================================================================
# GetFileContents
#===================================================================================================
def GetFileContents(filename, binary=False):
    '''
    Reads a file and returns its contents. Works for both local and remote files.
    
    :param str filename:
    
    :param bool binary:
        If True returns the file as is, ignore any EOL conversion.
    
    :rtype: str
    :returns:
        The file's contents
        
    .. see:: FTP LIMITATIONS at this module's doc for performance issues information
    '''
    source_file = OpenFile(filename, binary=binary)
    try:
        return source_file.read()
    finally:
        source_file.close()


#===================================================================================================
# GetFileLines
#===================================================================================================
def GetFileLines(filename):
    '''
    Reads a file and returns its contents as a list of lines. Works for both local and remote files.
    
    :param str filename:
    
    :rtype: list(str)
    :returns:
        The file's lines
        
    .. see:: FTP LIMITATIONS at this module's doc for performance issues information
    '''
    return GetFileContents(filename, binary=False).split('\n')


def OpenFile(filename, binary=False):
    '''
    Open a file and returns it.
    Consider the possibility of a remote file (HTTP, HTTPS, FTP)
    
    :param str filename:
        Local or remote filename.
    
    :param bool binary:
        If True returns the file as is, ignore any EOL conversion.
    
    :rtype: file
    :returns:
        The open file, it must be closed by the caller
        
    @raise: FileNotFoundError
        When the given filename cannot be found
        
    .. see:: FTP LIMITATIONS at this module's doc for performance issues information
    '''
    from urlparse import urlparse
    filename_url = urlparse(filename)

    # Check if file is local
    if _UrlIsLocal(filename_url):
        if not os.path.isfile(filename):
            raise FileNotFoundError(filename)
        mode = 'r'
        if binary:
            mode += 'b'
        else:
            mode += 'U'
        return file(filename, mode)

    # Not local
    return RemoteImpl.OpenFile(filename_url)



#=======================================================================================================================
# ListFiles
#=======================================================================================================================
def ListFiles(directory):
    '''
    Lists the files in the given directory

    :param str directory:
        A directory or URL

    :rtype: list(str)
    :returns:
        List of filenames/directories found in the given directory.
        Returns None if the given directory does not exists.

    :raises NotImplementedProtocol:
        If file protocol is not local or FTP
        
    .. see:: FTP LIMITATIONS at this module's doc for performance issues information
    '''
    from urlparse import urlparse
    directory_url = urlparse(directory)

    # Handle local
    if _UrlIsLocal(directory_url):
        if not os.path.isdir(directory):
            return None
        return os.listdir(directory)

    # Handle FTP
    elif directory_url.scheme == 'ftp':
        return RemoteImpl.FTPListFiles(directory_url)
    else:
        raise NotImplementedProtocol(directory_url.scheme)



#=======================================================================================================================
# CheckIsFile
#=======================================================================================================================
def CheckIsFile(filename):
    '''
    Check if the given file exists.
    
    @filename: str
        The filename to check for existence.
        
    @raise: FileNotFoundError
        Raises if the file does not exist. 
    '''
    if not IsFile(filename):
        raise FileNotFoundError(filename)



#===================================================================================================
# CheckIsDir
#===================================================================================================
def CheckIsDir(directory):
    '''
    Check if the given directory exists.
    
    @filename: str
        Path to a directory being checked for existence.
        
    @raise: DirectoryNotFoundError
        Raises if the directory does not exist. 
    '''
    if not IsDir(directory):
        raise DirectoryNotFoundError(directory)



#===================================================================================================
# CreateFile
#===================================================================================================
def CreateFile(filename, contents, eol_style=EOL_STYLE_NATIVE, create_dir=True):
    '''
    Create a file with the given contents.

    :param str filename:
        Filename and path to be created.

    :param str contents:
        The file contents as a string.

    :type eol_style: EOL_STYLE_XXX constant
    :param eol_style:
        Replaces the EOL by the appropriate EOL depending on the eol_style value.
        Considers that all content is using only "\n" as EOL.
        
    :param bool create_dir:
        If True, also creates directories needed in filename's path
        
    :raises NotImplementedProtocol:
        If file protocol is not local or FTP
    
    .. see:: FTP LIMITATIONS at this module's doc for performance issues information
    '''
    # If asked, creates directory containing file
    if create_dir:
        dirname = os.path.dirname(filename)
        if dirname:
            CreateDirectory(dirname)

    # Replaces eol on each line by the given eol_style.
    contents = _HandleContentsEol(contents, eol_style)

    from urlparse import urlparse
    filename_url = urlparse(filename)

    # Handle local
    if _UrlIsLocal(filename_url):
        _LocalCreateFile(filename, contents)

    # Handle FTP
    elif filename_url.scheme == 'ftp':
        RemoteImpl.FTPCreateFile(filename_url, contents)

    else:
        raise NotImplementedProtocol(filename_url.scheme)


def _LocalCreateFile(filename, contents):
    '''
    Create a file locally
    
    :param str filename:
        File to be created

    :param str contents:
        Initial contents in file
    '''
    # Check if encoding is necessary
    BOM = ''  # Byte order mark is a Unicode character used to signal the endianness of a text file or stream.
    if isinstance(contents, unicode):
        import codecs
        BOM = codecs.BOM_UTF8
        contents = contents.encode('utf-8')

    # Write file
    oss = file(filename, 'wb')
    try:
        oss.write(BOM)
        oss.write(contents)
    finally:
        oss.close()


#===================================================================================================
# CreateDirectory
#===================================================================================================
def CreateDirectory(directory):
    '''
    Create directory including any missing intermediate directory.

    :param str directory:
    
    :raises NotImplementedProtocol:
        If protocol is not local or FTP.
        
    .. see:: FTP LIMITATIONS at this module's doc for performance issues information
    '''
    from urlparse import urlparse

    directory_url = urlparse(directory)

    # Handle local
    if _UrlIsLocal(directory_url):
        from path import path
        target = path(directory)
        if not target.exists():
            target.makedirs()

    # Handle FTP
    elif directory_url.scheme == 'ftp':
        RemoteImpl.FTPCreateDirectory(directory_url)

    else:
        raise NotImplementedProtocol(directory_url.scheme)



#===================================================================================================
# DeleteDirectory
#===================================================================================================
def DeleteDirectory(directory, skip_on_error=False):
    '''
    Deletes a directory.
    
    :param str directory:
    
    :param bool skip_on_error:
        If True, ignore any errors when trying to delete directory (for example, directory not
        found)

    :raises NotImplementedForRemotePathError:
        If trying to delete a remote directory.
    '''
    _AssertIsLocal(directory)

    import shutil
    def OnError(fn, path, excinfo):
        '''
        Remove the read-only flag and try to remove again.
        On Windows, rmtree fails when trying to remove a read-only file. This fix it!
        Another case: Read-only directories return True in os.access test. It seems that read-only
        directories has it own flag (looking at the property windows on Explorer).
        '''
        if fn is os.remove and os.access(path, os.W_OK):
            raise

        # Make the file WRITEBLE and executes the original delete funcion (osfunc)
        import stat
        os.chmod(path, stat.S_IWRITE)
        fn(path)

    try:
        shutil.rmtree(directory, onerror=OnError)
    except:
        if not skip_on_error:
            raise  # Raise only if we are not skipping on error



#===================================================================================================
# GetMTime
#===================================================================================================
def GetMTime(path):
    '''
    :param str path:
        Path to file or directory
    
    :rtype: float
    :returns:
        Modification time for path.
        
        If this is a directory, the highest mtime from files inside it will be returned.
        
    @note:
        In some Linux distros (such as CentOs, or anything with ext3), mtime will not return a value
        with resolutions higher than a second.
        
        http://stackoverflow.com/questions/2428556/os-path-getmtime-doesnt-return-fraction-of-a-second
    '''
    if os.path.isdir(path):
        from etk11.algorithms import FindFiles
        files = FindFiles(path)

        if len(files) > 0:
            return max(map(os.path.getmtime, files))

    return os.path.getmtime(path)



#===================================================================================================
# Internal functions
#===================================================================================================
def _UrlIsLocal(directory_url):
    '''
    :param ParseResult directory_url:
        A parsed url as returned by urlparse.urlparse.

    :rtype: bool
    :returns:
        Returns whether the given url refers to a local path.

    .. note:: The "directory_url.scheme" is the drive letter for a local path on Windows and an empty string
    for a local path on Linux. The other possible values are "http", "ftp", etc. So, checking if
    the length is less than 2 characters long checks that the url is local.
    '''
    return len(directory_url.scheme) < 2


def _AssertIsLocal(path):
    '''
    Checks if a given path is local, raise an exception if not.
    
    This is used in filesystem functions that do not support remote operations yet.
    
    :param str path:
    
    :raises NotImplementedForRemotePathError:
        If the given path is not local
    '''
    from urlparse import urlparse
    if not _UrlIsLocal(urlparse(path)):
        raise NotImplementedForRemotePathError


def _HandleContentsEol(contents, eol_style):
    '''
    Replaces eol on each line by the given eol_style.
    
    :param str contents:
    :type eol_style: EOL_STYLE_XXX constant
    :param eol_style:
    '''
    if eol_style == EOL_STYLE_NONE:
        return contents

    if eol_style == EOL_STYLE_UNIX:
        return contents.replace('\r\n', eol_style).replace('\r', eol_style)

    if eol_style == EOL_STYLE_MAC:
        return contents.replace('\r\n', eol_style).replace('\n', eol_style)

    if eol_style == EOL_STYLE_WINDOWS:
        return contents.replace('\r\n', '\n').replace('\r', '\n').replace('\n', EOL_STYLE_WINDOWS)

    raise ValueError('Unexpected eol style: %r' % (eol_style,))


def ListMappedNetworkDrives():
    '''
    On Windows, returns a list of mapped network drives
    
    :return: tuple(string, string, bool)
        For each mapped netword drive, return 3 values tuple:
            - the local drive
            - the remote path-
            - True if the mapping is enabled (warning: not reliable)
    '''
    if sys.platform != 'win32':
        raise NotImplementedError
    drives_list = []
    netuse = _CallWindowsNetCommand(['use'])
    for line in netuse.split(EOL_STYLE_WINDOWS):
        match = re.match("(\w*)\s+(\w:)\s+(.+)", line.rstrip())
        if match:
            drives_list.append((match.group(2), match.group(3), match.group(1) == 'OK'))
    return drives_list


def _CallWindowsNetCommand(parameters):
    '''
    Call Windows NET command, used to acquire/configure network services settings.
    
    :param parameters: list of command line parameters
    
    :return: command output
    '''
    import subprocess
    popen = subprocess.Popen(["net"] + parameters, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdoutdata, stderrdata = popen.communicate()
    if stderrdata:
        raise OSError("Failed on call net.exe: %s" % stderrdata)
    return stdoutdata



#=======================================================================================================================
# RemoteImpl
#=======================================================================================================================
class RemoteImpl:

    @classmethod
    def FTPHost(cls, url):
        '''
        Create an ftputil.FTPHost instance at the target url. Configure the host to correctly use the
        url's port.
    
        :param ParseResult url:
            As returned by urlparse.urlparse
    
        :rtype: ftputil.FTPHost
        '''
        from ftputil.ftputil import FTPHost as ftputil_host
        import ftplib

        class DefaultFTP(ftplib.FTP):
            def __init__(self, host='', user='', passwd='', acct='', port=ftplib.FTP.port):
                # Must call parent constructor without any parameter so it don't try to perform
                # the connect without the port parameter (it have the same "if host" code in there)
                ftplib.FTP.__init__(self)

                if host:
                    self.connect(host, port)

                    if user:
                        self.login(user, passwd, acct)
                    else:
                        self.login()

            def __enter__(self):
                return self

            def __exit__(self):
                self.close()


        class ActiveFTP(DefaultFTP):
            def __init__(self, *args, **kwargs):
                DefaultFTP.__init__(self, *args, **kwargs)
                self.set_pasv(False)


        from functools import partial
        create_host = partial(ftputil_host, url.hostname, url.username, url.password, port=url.port)

        # Try to create active ftp host
        host = create_host(session_factory=ActiveFTP)

        # Check if a simple operation fails in active ftp, if it does, switch to default (passive) ftp
        try:
            host.stat('~')
        except Exception, e:
            if e.errno == 425:  # Errno raised when trying to a server without active ftp
                host = create_host(session_factory=DefaultFTP)

        return host


    @classmethod
    def FTPUploadFileToUrl(cls, source_filename, target_url):
        '''
        Uploads the given LOCAL file to the given ftp url.
    
        :param str source_filename:
            The local filename to copy from.
    
        :param ParseResult target_url:
            The target directory.
            
            A parsed url as returned by urlparse.urlparse
        '''
        with cls.FTPHost(target_url) as ftp_host:
            ftp_host.upload(source_filename, target_url.path, 'b')


    @classmethod
    def DownloadUrlToFile(cls, source_url, target_filename):
        '''
        Downloads file in source_url to target_filename
        
        :param ParseResult source_url:
            A parsed url as returned by urlparse.urlparse
        
        :param str target_filename:
            A target filename
        
        '''
        if source_url.scheme == 'ftp':
            return cls._FTPDownload(source_url, target_filename)

        # Use shutil for other schemes
        iss = cls.OpenFile(source_url)
        with file(target_filename, 'wb') as oss:
            import shutil
            shutil.copyfileobj(iss, oss)


    @classmethod
    def OpenFile(cls, filename_url):
        '''
        :param ParseResult filename_url:
            Target file to be opened
        
            A parsed url as returned by urlparse.urlparse
            
        :rtype: file
        :returns:
            The open file
            
        @raise: FileNotFoundError
            When the given filename cannot be found
            
        @raise: CantOpenFileThroughProxyError
            When trying to access a file through a proxy, using a protocol not supported by urllib
            
        @raise: DirectoryNotFoundError
            When trying to access a remote directory that does not exist
            
        @raise: ServerTimeoutError
            When failing to connect to a remote server
        '''

        if filename_url.scheme == 'ftp':
            try:
                return cls._FTPOpenFile(filename_url)
            except FTPIOError, e:
                if e.errno == 550:
                    raise FileNotFoundError(filename_url.path)
                raise

        try:
            import urllib
            return urllib.urlopen(filename_url.geturl(), None)
        except IOError, e:
            # Raise better errors than the ones given by urllib
            import errno
            filename = filename_url.path
            if e.errno == errno.ENOENT:  # File does not exist
                raise FileNotFoundError(filename)

            if 'proxy' in str(e.strerror):
                raise CantOpenFileThroughProxyError(filename)

            if '550' in str(e.strerror):
                raise DirectoryNotFoundError(filename)

            if '11001' in str(e.strerror):
                raise ServerTimeoutError(filename)

            # If it's another error, just raise it again.
            raise e


    @classmethod
    def _FTPDownload(cls, source_url, target_filename):
        '''
        Downloads a file through FTP
        
        :param source_url:
            .. see:: DownloadUrlToFile
        :param target_filename:
            .. see:: DownloadUrlToFile
        '''
        with cls.FTPHost(source_url) as ftp_host:
            ftp_host.download(source=source_url.path, target=target_filename, mode='b')


    @classmethod
    def _FTPOpenFile(cls, filename_url):
        '''
        Opens a file (FTP only) and sets things up to close ftp connection when the file is closed.
        
        :param filename_url:
            .. see:: OpenFile
        '''
        ftp_host = cls.FTPHost(filename_url)
        try:
            open_file = ftp_host.open(filename_url.path)

            # Set it up so when open_file is closed, ftp_host closes too
            def FTPClose():
                # Before closing, remove callback to avoid recursion, since ftputil closes all files
                # it has
                from etk11.callback import Remove
                Remove(open_file.close, FTPClose)

                ftp_host.close()

            from etk11.callback import After
            After(open_file.close, FTPClose)

            return open_file
        except:
            ftp_host.close()
            raise


    @classmethod
    def FTPCreateFile(cls, url, contents):
        '''
        Creates a file in a ftp server.
    
        :param ParseResult url:
            File to be created.
        
            A parsed url as returned by urlparse.urlparse
    
        :param text contents:
            The file contents.
        '''
        with cls.FTPHost(url) as ftp_host:
            with ftp_host.file(url.path, 'w') as oss:
                oss.write(contents)


    @classmethod
    def FTPIsFile(cls, url):
        '''
        :param ParseResult url:
            URL for file we want to check
        
        :rtype: bool
        :returns:
            True if file exists.
        '''
        with cls.FTPHost(url) as ftp_host:
            return ftp_host.path.isfile(url.path)


    @classmethod
    def FTPCreateDirectory(cls, url):
        '''
        :param ParseResult url:
            Target url to be created
            
            A parsed url as returned by urlparse.urlparse
        '''
        with cls.FTPHost(url) as ftp_host:
            ftp_host.makedirs(url.path)


    @classmethod
    def FTPMoveDirectory(cls, source_url, target_url):
        '''
        :param ParseResult url:
            Target url to be created
            
            A parsed url as returned by urlparse.urlparse
        '''
        with cls.FTPHost(source_url) as ftp_host:
            ftp_host.rename(source_url.path, target_url.path)


    @classmethod
    def FTPIsDir(cls, url):
        '''
        List files in a url
        
        :param ParseResult url:
            Directory url we are checking
            
            A parsed url as returned by urlparse.urlparse
            
        :rtype: bool
        :returns:
            True if url is an existing dir
        '''
        with cls.FTPHost(url) as ftp_host:
            return ftp_host.path.isdir(url.path)


    @classmethod
    def FTPListFiles(cls, url):
        '''
        List files in a url
        
        :param ParseResult url:
            Target url being searched for files
            
            A parsed url as returned by urlparse.urlparse
            
        :rtype: list(str) or None
        :returns:
            List of files, or None if directory does not exist (error 550 CWD)
        '''
        with cls.FTPHost(url) as ftp_host:
            try:
                return ftp_host.listdir(url.path)
            except PermanentError, e:
                if e.errno == 550:
                    # "No such file or directory"
                    return None
                else:
                    raise
