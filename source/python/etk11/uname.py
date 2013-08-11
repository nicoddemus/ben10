import os
import sys
import platform



#===================================================================================================
# The algorithms
#===================================================================================================
def __dist_algorithm_Windows():
    if sys.platform != 'win32':
        return (None, None, None)
    else:
        if 'AMD64' in platform.python_compiler():
            return ('amd64', 'win32', '')
        else:
            return ('i686', 'win32', '')


#===================================================================================================
# __dist_algorithm_DefaultPlatform
#===================================================================================================
def __dist_algorithm_DefaultPlatform():
    dist, version = (platform.dist()[0], platform.dist()[1])
    if dist in ['', None, '0', ' ']:
        return (None, None, None)
    else:
        return (platform.machine(), dist, version)


#===================================================================================================
# __dist_algorithm_SlackWare
#===================================================================================================
def __dist_algorithm_SlackWare():
    result = (0, 0, 0)
    version_ = '/etc/slackware-version'
    if os.path.isfile(version_):
        version = file(version_, 'r').read()
        version = version.split()[1]
        version = version.split('.')[0:2]
        result = (platform.machine(), 'slack', ''.join(version))
    return result


#===================================================================================================
# UNAME
#===================================================================================================
def UNAME():
    '''
        Returns a call to system 'uname', returning the parameters:
            - distribution
            - version
            - machine
    '''
    result = platform.uname()
    return result[0], result[2], result[4]


#===================================================================================================
# __dist_algorithm_uname
#===================================================================================================
def __dist_algorithm_uname():
    dist, version, machine = UNAME()
    dist = dist.lower()
    version = version.replace('.', '')
    return (machine, dist, version)


#===================================================================================================
# __Dist
#===================================================================================================
def __Dist():
    '''Returns the current machine distribution, using several algorithms to find out the correct 
    distribution name, which usually includes the operation system name and version.
    
    Examples: 
        - win32
        - irix65
        - redhat9
    '''
    dist_algorithms = [
        __dist_algorithm_Windows,
        __dist_algorithm_DefaultPlatform,
        __dist_algorithm_SlackWare,
        __dist_algorithm_uname,
    ]

    for i_algorithm in dist_algorithms:
        machine, dist, version = i_algorithm()
        if dist:
            break
    return machine, dist, version.replace('.', '')


#===================================================================================================
# IsRunningOn64BitMachine
#===================================================================================================
def IsRunningOn64BitMachine():
    '''
    :rtype: bool
    :returns:
        Returns true if the current machine is a 64 bit machine (regardless of the way this
        executable was compiled).
    '''
    platform_short_name = GetPlatformShortName()
    if platform_short_name == 'win64':
        return True #If python is compiled on 64 bits and running, this is a 64 bit machine.

    elif platform_short_name == 'win32':
        #Otherwise,
        import ctypes
        i = ctypes.c_int()
        kernel32 = ctypes.windll.kernel32
        process = kernel32.GetCurrentProcess()
        kernel32.IsWow64Process(process, ctypes.byref(i))
        is64bit = (i.value != 0)
        return is64bit

    elif platform_short_name == 'redhat64':
        return True #If python is compiled on 64 bits and running, this is a 64 bit machine.

    else:
        raise AssertionError('Unsupported for: %s' % (platform_short_name,))


#===================================================================================================
# Platform
#===================================================================================================
def Platform():
    '''Returns the current platform, in the format:
    <Machine>.<Distribution>
    
    Examples:
        - i686.win32
        - mips.irix65
        - i686.redhat9
    '''
    machine, dist, version = __Dist()
    return '%s.%s%s' % (machine, dist, version)


#===================================================================================================
# SimplePlatform
#===================================================================================================
def SimplePlatform():
    '''Returns a simplified platform string in the format:
    <Machine>.<Distribution>
    
    Examples:
        - i686.win32
        - amd64.win32
        - mips.irix
        - i686.redhat
    '''
    machine_map = {
        'i686'   : 'i686',
        'i386'   : 'i686',
        'x86_64' : 'amd64',
        'amd64'  : 'amd64',
    }
    dist_map = {
        'win32'  : 'win32',
        'redhat' : 'redhat',
        'SUSE'   : 'redhat',
        'darwin' : 'darwin',
    }

    machine, dist, dummy = __Dist()
    try:
        machine = machine_map[machine]
    except KeyError:
        raise KeyError('Unspected machine "%s". Please review coilib50.system.uname module.' % machine)

    try:
        dist = dist_map[dist]
    except KeyError:
        raise KeyError('Unspected dist "%s". Please review coilib50.system.uname module.' % dist)
    return '%s.%s' % (machine, dist)


#===================================================================================================
# Machine
#===================================================================================================
def Machine():
    '''
    Returns the current machine nick name:
        
    Examples:
        - i686
        - mips
    '''

    result = sys.platform
    if result == 'win32':
        if 'AMD64' in platform.python_compiler():
            return 'amd64'
        else:
            return 'i686'
    else:
        result, dist, version = __Dist()
    return result


#===================================================================================================
# Distribution
#===================================================================================================
def Distribution():
    '''
    Returns the distribution name for the current platform:
    
    Examples:
        - win32
        - redhat9
        - irix65
    '''

    machine, dist, version = __Dist()
    result = '%s%s' % (dist, version)
    return result



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
    from etk11.is_frozen import IsFrozen
    if IsFrozen():
        result = os.path.dirname(sys.executable)
        result = os.path.normpath(os.path.join(result, '..'))
    else:
        result = sys.path[0]

    return result


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
    #where to save
    if sys.platform == 'win32':
        path = os.environ['HOMEDRIVE'] + os.environ['HOMEPATH']
    else:
        path = os.environ['HOME']

    return path


#===================================================================================================
# GetPlatformMneumonic
#===================================================================================================
def GetPlatformMneumonic(platform=None):
    '''
    Returns the mneumonic name of the current platform, used in the prompt and Builds configuration
    file. 
    
    :rtype: str
    :returns:
        Returns the platform mneumonic
    '''
    names = {
        'i686.win32' : 'w32',
        'amd64.win32' : 'w64',

        'i686.redhat' : 'r32',
        'amd64.redhat' : 'r64',

        'i686.darwin' : 'mac',
    }
    if platform is None:
        platform = SimplePlatform()

    try:
        return names[platform]
    except KeyError:
        raise KeyError('Platform not mapped: %r. Please review this method.' % platform)


#===================================================================================================
# GetPlatformShortName
#===================================================================================================
def GetPlatformShortName(platform=None):
    '''
    Returns the short name of the current platform, used in filenames (such as the 
    application installer). 
    
    :rtype: str
    :returns:
        The short name of the current platform.
        
        I.e.: 
            - 'win32' on python compiled in 32 bit running on windows 
            - 'win64' on python compiled in 64 bit running on windows 
            - 'redhat64' on python compiled in 64 bit running on linux
    '''
    names = {
        'i686.win32' : 'win32',
        'amd64.win32' : 'win64',

        'i686.redhat' : 'redhat32',
        'amd64.redhat' : 'redhat64',

        'i686.darwin' : 'mac',
    }
    if platform is None:
        platform = SimplePlatform()

    try:
        return names[platform]
    except KeyError:
        raise KeyError('Platform not mapped: %r. Please review this method.' % platform)


#===================================================================================================
# GetPlatformLongName
#===================================================================================================
def GetPlatformLongName(platform=None):
    '''
    Returns the long name of the current platform, which should be used when displaying
    machine information to the user (as in the About dialog).
    
    :rtype: C{str} 
    :returns:
        the long name of the current platform
    '''
    names = {
        'i686.win32' : 'Windows 32-bit',
        'amd64.win32' : 'Windows 64-bit',

        'i686.redhat' : 'RedHat Linux 32-bit',
        'amd64.redhat' : 'RedHat Linux 64-bit',

        'i686.darwin' : 'MacOS',
    }
    if platform is None:
        platform = SimplePlatform()

    try:
        return names[platform]
    except KeyError:
        raise KeyError('Platform not mapped: %r. Please review this method.' % platform)
