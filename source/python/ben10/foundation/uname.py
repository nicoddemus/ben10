from ben10.foundation.is_frozen import IsFrozen
from ben10.foundation.platform_ import Platform
import os
import sys



#===================================================================================================
# IsRunningOn64BitMachine
#===================================================================================================
def IsRunningOn64BitMachine():
    '''
    TODO: BEN-19: Refactor: Move uname stuff to Platform class.

    :rtype: bool
    :returns:
        Returns true if the current machine is a 64 bit machine (regardless of the way this
        executable was compiled).
    '''
    platform_short_name = str(Platform.GetCurrentPlatform())

    # If python is compiled on 64 bits and running, this is a 64 bit machine.
    if platform_short_name == 'win64':
        return True

    # Otherwise,
    elif platform_short_name == 'win32':
        import ctypes
        i = ctypes.c_int()
        process = ctypes.windll.kernel32.GetCurrentProcess()
        ctypes.windll.kernel32.IsWow64Process(process, ctypes.byref(i))
        is64bit = (i.value != 0)
        return is64bit

    # If python is compiled on 64 bits and running, this is a 64 bit machine.
    elif platform_short_name == 'redhat64':
        return True

    else:
        raise AssertionError('Unsupported for: %s' % (platform_short_name,))



#===================================================================================================
# GetApplicationDir
#===================================================================================================
def GetApplicationDir():
    '''
    Returns the application directory, that is, the complete path to the application executable
    or main python file.

    Expects that the application executable is installed in a sub directory of the application
    directory.
    '''
    if IsFrozen():
        result = os.path.dirname(sys.executable)
        result = os.path.normpath(os.path.join(result, '..'))
    else:
        result = sys.path[0]

    return result


#===================================================================================================
# GetExecutableDir
#===================================================================================================
def GetExecutableDir():
    '''
    :return str:
        Directory containing sys.executable
    '''
    return os.path.dirname(sys.executable)


#===================================================================================================
# GetUserHomeDir
#===================================================================================================
def GetUserHomeDir():
    '''
        :rtype: the user directory to be used (platform-dependent).
        In windows that means something as:
            C:\Documents and Settings\user_name
        In linux it's something as:
            /usr/home/user_name
    '''
    # where to save
    if sys.platform == 'win32':
        path = os.environ['HOMEDRIVE'] + os.environ['HOMEPATH']
    else:
        path = os.environ['HOME']

    return path
