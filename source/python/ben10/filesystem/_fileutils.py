'''
This module contains an open function that should be used with care.

Reading files in windows can have a good performance gain is the reading is made sequentially and
a flag is set in the file opened
'''

import os
import sys



def _GetFileFlagConstants(sys_platform):
    '''
    Using function for constants filling in order to test it AND enable 100% coverage.
    '''
    if sys_platform == 'win32':
        # os.O_SEQUENTIAL:
        #   Access is intended to be sequential from beginning to end. The system can use this as a
        #   hint to optimize file caching.
        #   This flag should not be used if read-behind (that is, reverse scans) will be used.
        #   This flag has no effect if the file system does not support cached I/O and
        #   FILE_FLAG_NO_BUFFERING.
        # os.O_BINARY:
        #   When opening a binary file, you should append 'b' to the mode value for improved
        #   portability. (It's useful even on systems which don't treat binary and text files
        #   differently, where it serves as documentation.)
        return os.O_SEQUENTIAL, os.O_BINARY
    else:
        # Any other system than windows (linux) does not support such type of flags
        # In linux the random or sequential file access have the same performance
        #
        # Any other system than windows (linux) have no such option
        return 0, 0

FILE_FLAG_SEQUENTIAL, FILE_FLAG_BINARY = _GetFileFlagConstants(sys.platform)



#===================================================================================================
# OpenReadOnlyFile
#===================================================================================================
def OpenReadOnlyFile(filename, binary=False, sequential=False):
    '''
    Return a new file object.

    This is a specialized open file function to abstract handling files in different operational
    systems.

    Windows files can be configured with a attribute for reading sequentially that have a good
    impact in reading files, specially if reading network files.

    :param str filename:
        File name to be opened

    :param bool binary:
        True if opening a binary file, should be used for improved portability. (It's useful even on
        systems which don't treat binary and text files differently, where it serves as
        documentation.)

    :param bool sequential:
        True if access is intended to be sequential from beginning to end
        .. see:: FILE_FLAG_SEQUENTIAL

    .. note:: In linux operational system the binary and sequential flags are not supported
    '''
    if binary:
        mode = 'rb'
    else:
        mode = 'r'

    if sequential:
        flags = os.O_RDONLY | FILE_FLAG_SEQUENTIAL
        if binary:
            flags |= FILE_FLAG_BINARY

        file_desc = os.open(filename, flags)
        read_only_file = os.fdopen(file_desc, mode)
        return read_only_file

    else:
        return file(filename, mode)
