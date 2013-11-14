'''
Duplicates methods from coilib50 that should be moved to filesystem.
'''
import os



#===================================================================================================
# ExtendedPathMask
#===================================================================================================
class ExtendedPathMask(object):
    '''
    This class is a place-holder for functions that handle the exteded path mask.

    Extended Path Mask
    ------------------

    The extended path mask is a file search path description used to find files based on the filename.
    This extended path mask includes the following features:
        - Recursive search (prefix with a "+" sign)
        - The possibility of adding more than one filter to match files (separated by ";")
        - The possibility of negate an mask (prefix the mask with "!").

    The extended path mask has the following syntax:

        [+|-]<path>/<filter>(;<filter>)*

    Where:
        + : recursive and copy-tree flag
        - : recursive and copy-flat flag (copy files to the target directory with no tree structure)
        <path> : a usual path, using '/' as separator
        <filter> : A filename filter, as used in dir command:
            Ex:
                *.zip;*.rar
                units.txt;*.ini
                *.txt;!*-002.txt
    '''


    @classmethod
    def Split(cls, extended_path_mask):
        '''
        Splits the given path into their components: recursive, dirname, in_filters and out_filters

        :param str: extended_path_mask:
            The "extended path mask" to split

        :rtype: tuple(bool,bool,str,list(str),list(str))
        :returns:
            Returns the extended path 5 components:
            - The tree-recurse flag
            - The flat-recurse flag
            - The actual path
            - A list of masks to include
            - A list of masks to exclude
        '''
        import os.path
        r_tree_recurse = extended_path_mask[0] in '+-'
        r_flat_recurse = extended_path_mask[0] in '-'

        r_dirname, r_filters = os.path.split(extended_path_mask)
        if r_tree_recurse:
            r_dirname = r_dirname[1:]

        filters = r_filters.split(';')
        r_in_filters = [i for i in filters if not i.startswith('!')]
        r_out_filters = [i[1:] for i in filters if i.startswith('!')]

        return r_tree_recurse, r_flat_recurse, r_dirname, r_in_filters, r_out_filters



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
        files = FindFiles(path)

        if len(files) > 0:
            return max(map(os.path.getmtime, files))

    return os.path.getmtime(path)



#===================================================================================================
# CheckForUpdate
#===================================================================================================
def CheckForUpdate(source, target):
    '''
    Checks if the given target filename should be re-generated because the source has changed.
    :param  source:
            the source filename.
    :param  target:
            the target filename.
    @return:
        True if the target is out-dated, False otherwise.
    '''
    return \
        not os.path.isfile(target) or \
        os.path.getmtime(source) > os.path.getmtime(target)



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

    for i_filter in filters:
        if fnmatch.fnmatch(filename, i_filter):
            return True
    return False



#===================================================================================================
# FindFiles
#===================================================================================================
def FindFiles(dir_, in_filters=None, out_filters=None, recursive=True, include_root_dir=True, standard_paths=False):
    '''
    Searches for files in a given directory that match with the given patterns.

    :type dir_: the directory root, to search the files.
    :param dir_:
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
    for dir_root, directories, filenames in os.walk(dir_):

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
        dir_prefix = len(dir_) + 1
        result = [file[dir_prefix:] for file in result]

    if standard_paths:
        result = map(StandardizePath, result)

    return result
