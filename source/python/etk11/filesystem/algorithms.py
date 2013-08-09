import os
import sys



#===================================================================================================
# FindFiles
#===================================================================================================
def FindFiles(dir, in_filters=None, out_filters=None, recursive=True, include_root_dir=True, standard_paths=False):
    '''
    Searches for files in a given directory that match with the given patterns.

    :type dir: the directory root, to search the files.
    :param dir:
    :type in_filters: a list with patterns to match (default = all). E.g.: ['*.py']
    :param in_filters:
    :type out_filters: a list with patterns to ignore (default = none). E.g.: ['*.py']
    :param out_filters:
    :type recursive: if True search in subdirectories, otherwise, just in the root.
    :param recursive:
    :type include_root_dir: if True, includes the directory being searched in the returned paths
    :param include_root_dir:
    :type standard_paths: if True, always uses unix path separators "/"
    :param standard_paths:
    :rtype: a list of strings with the files that matched (with the full path in the filesystem).
    '''
    # all files
    if in_filters is None:
        in_filters = ['*']

    if out_filters is None:
        out_filters = []

    result = []

    # maintain just files that don't have a pattern that match with out_filters
    # walk through all directories based on dir
    for dir_root, directories, filenames in os.walk(dir):

        for i_directory in directories[:]:
            if MatchMasks(i_directory, out_filters):
                directories.remove(i_directory)

        for filename in directories + filenames:
            if MatchMasks(filename, in_filters) and not MatchMasks(filename, out_filters):
                result.append(os.path.join(dir_root, filename))

        if not recursive:
            break

    if not include_root_dir:
        # Remove root dir from all paths
        dir_prefix = len(dir) + 1
        result = [file[dir_prefix:] for file in result]

    if standard_paths:
        from etk11.filesystem import StandardizePath
        result = map(StandardizePath, result)

    return result



#===================================================================================================
# MatchMasks
#===================================================================================================
def MatchMasks(filename, filters):
    '''
    Verifies if a filename match with given patterns.

    :type filename: the filename to match.
    :param filename:
    :type filters: the patterns to search in the filename.
    :param filters:
    :rtype: True if the filename has matched with one pattern, False otherwise.
    '''
    import fnmatch
    if not isinstance(filters, (list, tuple)):
        filters = [filters]

    for filter in filters:
        if fnmatch.fnmatch(filename, filter):
            return True
    return False


#===================================================================================================
# FilenamesExpandVars
#===================================================================================================
def FilenamesExpandVars(expression, filename, extra_vars={}, environ=os.environ):
    '''
        Expands the variables in the given expression:
            - Environmetn variables
            - Other varibles:
                - abs_path: The absolute patch of the given filename
                - platform: The current platform (sys.platform)
                - PLATFORM: The platform string (coilib50.system.Platform())
                - filename: The given filename
                - basename: The given filename base name (with out path)
                - exe_path: Path to the executable (either Python.exe or the application)
            - Extra variables: parameter extra_vars
    '''
    import coilib50.system

    abs_path = os.path.abspath(filename)
    basename = os.path.basename(filename)

    d = {}
    d.update(environ)
    d.update(extra_vars)
    d.update({
        'abs_path'  : abs_path,
        'platform'  : sys.platform,
        'PLATFORM'  : coilib50.system.Platform(),
        'filename'  : filename,
        'basename'  : basename,
        'app_dir'   : coilib50.system.GetApplicationDir(),
        'exe_path'  : os.path.dirname(sys.executable),
    })

    return expression % d


#===================================================================================================
# Filenames
#===================================================================================================
def Filenames(filename, masks, extra_vars={}, environ=os.environ):
    '''
        Returns a list of filenames, one for each mask, replacing 'dict' values using
        FilenamesExpandVars
    '''
    return [os.path.normpath(FilenamesExpandVars(i, filename, extra_vars, environ)) for i in masks]


#===================================================================================================
# FindFilename
#===================================================================================================
def FindFilename(filenames, is_dir=False):
    '''
        Returns the first filename in the given list that exists or raises an "IOError"
        exception
    '''
    if is_dir:
        Test = os.path.isdir
    else:
        Test = os.path.isfile

    result = None
    for i_filename in filenames:
        if Test(i_filename):
            result = i_filename
            break
    if (result is None):
        raise IOError, '\n - '.join([''] + filenames)
    return result


#===================================================================================================
# ReplaceInFile
#===================================================================================================
def ReplaceInFile(filename, string, replace):
    '''Replaces the string found in the given filename with the replace string.
    :type filename: the name of the file.
    :param filename:
    :type string: the string to search for.
    :param string:
    :type replace: replacement string.
    :param replace:
    :rtype: he new contents of the file
    '''
    f = file(filename)
    try:
        contents = f.read()
    finally:
        f.close()

    contents = contents.replace(string, replace)

    f = file(filename, 'w')
    try:
        f.write(contents)
    finally:
        f.close()

    return contents


#===================================================================================================
# GetProgramName
#===================================================================================================
def GetProgramName(filename):
    '''Returns the given filename appended with ".exe" on the windows platform,
    returning it unchanged in others.
    :type filename: the filename of the program.
    :param filename:
    '''
    if sys.platform == 'win32':
        filename += '.exe'
    return filename


#===================================================================================================
# MakeDirs
#===================================================================================================
def MakeDirs(directory):
    '''Creates all the intermediate directories. If the given directory already
    exists, do nothing.
    '''
    try:
        os.makedirs(directory)
    except OSError, e:
        import errno
        if e.errno != errno.EEXIST:
            raise e


#===================================================================================================
# NormPath
#===================================================================================================
def NormPath(path):
    '''
        An extension to os.path.normpath, accepting scaped slash "\/" which are not "normalized".
    '''
    def DoNormPath(path):
        result = path.replace('\/', '&slash;')
        result = os.path.normpath(result)
        result = result.replace('&slash;', '/')
        return result

    if isinstance(path, list):
        return map(DoNormPath, path)
    else:
        return DoNormPath(path)


#===================================================================================================
# SplitAll
#===================================================================================================
def SplitAll(path):
    """Return a list of the path components in this path.

    The first item in the list will be either os.curdir, os.pardir, empty,
    or the root directory of this path (for example, '/' or 'C:\\').
    The other items in the list will be strings.

    os.path.join(*result) will yield the original path.
    """
    parts = []
    loc = path
    while loc != os.curdir and loc != os.pardir:
        prev = loc
        loc, child = os.path.split(prev)
        if loc == prev:
            break
        parts.append(child)
    parts.append(loc)
    parts.reverse()
    return parts


#===================================================================================================
# RelativePath
#===================================================================================================
def RelativePath(path, dest):
    '''Returns the relative path from "path" to "dest".
    :type path: the original path.
    :param path:
    :type dest: the path to make relative to.
    :param dest:
    '''
    assert path is not None
    assert dest is not None
    origin = os.path.abspath(path)
    dest = os.path.abspath(dest)

    orig_list = SplitAll(os.path.normcase(origin))
    # Don't normcase dest!  We want to preserve the case.
    dest_list = SplitAll(dest)

    if orig_list[0] != os.path.normcase(dest_list[0]):
        # Can't get here from there.
        return dest

    # Find the location where the two paths start to differ.
    i = 0
    for start_seg, dest_seg in zip(orig_list, dest_list):
        if start_seg != os.path.normcase(dest_seg):
            break
        i += 1

    # Now i is the point where the two paths diverge.
    # Need a certain number of "os.pardir"s to work up
    # from the origin to the point of divergence.
    segments = [os.pardir] * (len(orig_list) - i)
    # Need to add the diverging part of dest_list.
    segments += dest_list[i:]
    if len(segments) == 0:
        # If they happen to be identical, use os.curdir.
        return os.curdir
    else:
        return os.path.join(*segments)


#===================================================================================================
# Join
#===================================================================================================
def Join(*args):
    joinned = os.path.join(*args)
    norm = os.path.normpath(joinned)
    return norm


#===================================================================================================
# SameFile
#===================================================================================================
def SameFile(src, dst):
    # Macintosh, Unix.
    if hasattr(os.path, 'samefile'):
        try:
            return os.path.samefile(src, dst)
        except OSError:
            return False

    # All other platforms: check for same pathname.
    return (os.path.normcase(os.path.abspath(src)) ==
            os.path.normcase(os.path.abspath(dst)))


#===================================================================================================
# GetAppDir
#===================================================================================================
def GetAppDir():
    '''Find the Application Working Directory
    '''
    import coilib50

    if coilib50.IsFrozen():
        return os.path.abspath(os.path.dirname(sys.executable))
    else:
        raise RuntimeError('Cannot find App Dir in development mode')


# Holder of Regexp we want to the compiled regexp.
_REGEXPS = {}
#===================================================================================================
# _GetInvalidCharsRegExp
#===================================================================================================
def _GetInvalidCharsRegExp(accept_directory_structure):
    '''
    :param boolean accept_directory_structure:
        If True returns a regexp that accepts '/', '\' and ':', if True, those
        chars won't be accepted (although ':' being accepted depends on the platform).
    '''
    import re

    def _Get(key, pattern):
        ret = _REGEXPS.get(key)
        if ret is None:
            ret = _REGEXPS.setdefault(key, re.compile(pattern))
        return ret


    windows_platform = sys.platform == 'win32'
    if accept_directory_structure:
        return _Get('default', r'[\*\?"<>|]')

    else:
        if windows_platform:
            return _Get('no_directory_structure_win', r'[\*\?"<>|/\\:]')
        else:
            return _Get('no_directory_structure_linux', r'[\*\?"<>|/\\]')


#===================================================================================================
# GetInvalidCharsInFilename
#===================================================================================================
def GetInvalidCharsInFilename(filename, accept_directory_structure=True):
    '''
    :param str filename:
        The name of the file.

    :param bool accept_directory_structure:
        If False, it won't accept /, \ or :

    @return str:
        A string with the invalid chars found in the filename.
    '''
    invalid_chars_found = ''

    windows_platform = sys.platform == 'win32'

    regexp = _GetInvalidCharsRegExp(accept_directory_structure)

    # The Characters *?"<>| are not accepted in the filename. The extra '\' inserted in the
    # regular expression are there because some characters (such as '*') are also meta characters
    # in regular expressions (i.e we are not validating the bars the separates the files in the
    # file system).
    result = regexp.findall(filename)
    if result is not None and len(result) > 0:
        # Invalid chars found in the filename.
        invalid_chars_found = result

    # The ':' character is not accepted in the filename in windows, except if the ':'
    # is the second char (c:\...).
    colons = filename.count(':')
    if colons > 0:
        if windows_platform:  # : is ok in linux
            for i, c in enumerate(filename[:]):
                if c == ':':
                    if i == 1:
                        continue

                    invalid_chars_found += ':'
                    break

    return invalid_chars_found


#===================================================================================================
# IsValidFilename
#===================================================================================================
def IsValidFilename(filename, accept_directory_structure=True):
    '''
    :param str filename:
        The name of the file.
        
    :param bool accept_directory_structure:
        If False, it won't accept /, \ or :

    :rtype: bool
    :returns:
        Returns whether the passed filename is valid.
    '''
    return len(GetInvalidCharsInFilename(filename, accept_directory_structure)) == 0

#===================================================================================================
# MakeValidFilename
#===================================================================================================
def MakeValidFilename(filename):
    '''
    :param str filename:
        The name of the file.

    :rtype: str
    :returns:
        Returns a new filename where invalid chars are changed to '_'.
    '''
    # Changed all but ':'
    new_filename = list('_'.join(
        _GetInvalidCharsRegExp(accept_directory_structure=True).split(filename)))

    windows_platform = sys.platform == 'win32'

    if windows_platform:
        for i, c in enumerate(new_filename[:]):
            if c == ':':
                if i == 1:
                    continue
                new_filename[i] = '_'

    new_filename = ''.join(new_filename)

    return new_filename



#===================================================================================================
# GetUnusedFilenameInDirectory
#===================================================================================================
def GetUnusedFilenameInDirectory(directory_path, base_filename):
    '''
    Obtains the path to a filename not created yet in the given directory. In order to generate new
    filenames an integer will be appended in the end of the received base filename. The given 
    directory will be populated as follows: 

        - C:\filename.csv
        - C:\filename002.csv

    If the base filename ends with under, then an index will always be added, even if the base does
    not exist. The given directory will be populated as follows:
    
        - C:\filename_001.csv
        - C:\filename_002.csv
        
    This is useful when we want to save some data without overwriting any existing file (For 
    example when we are dealing with multiple datas). 
    
    :param str directory_path:
        The path to the reference directory
        
    :param str base_filename:
        The base filename to generate new filenames
    '''
    # If the received file does not exist, return it
    index = 1
    base_name, ext = os.path.splitext(base_filename)

    not_found = True

    if not base_name.endswith('_'):
        # If the base name does not ends with underscore then the base is a valid
        # candidate, let us test it
        candidate = os.path.join(directory_path, base_filename)
        not_found = os.path.exists(candidate)

        # If already exist a file with the base name, there is no sense in create a 'base_file'_001
        # so the index will start in two.
        index = 2

        # Also adding an underscore to separate the indexes to create
        base_name += '_'

    while not_found:
        # The received base is either invalid or already exists. Appending an index to the end of it
        # to search for an unused filename.
        base_name_with_index = '%s%03d%s' % (base_name, index, ext)
        candidate = os.path.join(directory_path, base_name_with_index)
        index += 1
        not_found = os.path.exists(candidate)

    return candidate

#===================================================================================================
# CheckInvalidCharsInFilename
#===================================================================================================
def CheckInvalidCharsInFilename(filename, accept_directory_structure=True):
    '''
    Checks if a given filename has any invalid chars.

    :param str filename:
        The name of the file to check for invalid chars

    :param bool accept_directory_structure:
        If False, it won't accept /, \ or :
        
    :raises ValueError:
        Raises this error if there's some invalid char in the filename.
    '''
    invalid_chars_found = GetInvalidCharsInFilename(filename, accept_directory_structure)

    if len(invalid_chars_found) > 0:
        # this code is just to remove duplications from the list, to avoid multiple reports of a
        # invalid char.
        invalid_chars_found = list(set(invalid_chars_found))

        invalid_chars_found = str(invalid_chars_found)
        raise ValueError(
            tr('The characters: %s are not accepted in filename') % invalid_chars_found)

