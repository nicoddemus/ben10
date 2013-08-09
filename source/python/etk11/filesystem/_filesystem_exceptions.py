#===================================================================================================
# UnknownPlatformError
#===================================================================================================
class UnknownPlatformError(RuntimeError):

    def __init__(self, platform):
        self.platform = platform
        RuntimeError.__init__(self, 'Unknown platform "%s".' % platform)


#===================================================================================================
# NotImplementedProtocol
#===================================================================================================
class NotImplementedProtocol(RuntimeError):
    def __init__(self, protocol):
        RuntimeError.__init__(self, "Function can't handle protocol '%s'." % protocol)
        self.protocol = protocol


#===================================================================================================
# NotImplementedForRemotePathError
#===================================================================================================
class NotImplementedForRemotePathError(NotImplementedError):
    def __init__(self):
        NotImplementedError.__init__(self, 'Function not implemented remote paths.')


#===================================================================================================
# FileError
#===================================================================================================
class FileError(RuntimeError):
    def __init__(self, filename):
        self.filename = filename
        RuntimeError.__init__(self, self.GetMessage(filename))

    def GetMessage(self, filename):
        return 'Error while operating in file "%s".' % filename



#===================================================================================================
# FileNotFoundError
#===================================================================================================
class FileNotFoundError(FileError):
    def GetMessage(self, filename):
        return 'File "%s" not found.' % filename


#===================================================================================================
# CantOpenFileThroughProxyError
#===================================================================================================
class CantOpenFileThroughProxyError(FileError):
    def GetMessage(self, filename):
        return 'Can\'t open file "%s" through a proxy.' % filename



#===================================================================================================
# DirectoryNotFoundError
#===================================================================================================
class DirectoryNotFoundError(FileError):
    def GetMessage(self, directory):
        return 'Directory "%s" not found.' % directory


#===================================================================================================
# DirectoryAlreadyExistsError
#===================================================================================================
class DirectoryAlreadyExistsError(FileError):
    def GetMessage(self, directory):
        return 'Directory "%s" already exists.' % directory


#===================================================================================================
# ServerTimeoutError
#===================================================================================================
class ServerTimeoutError(FileError):
    def GetMessage(self, filename):
        return 'Server timeout while accessing file "%s"' % filename



#===================================================================================================
# FileAlreadyExistsError
#===================================================================================================
class FileAlreadyExistsError(FileError):
    def GetMessage(self, filename):
        return 'File "%s" already exists.' % filename



#===================================================================================================
# FileOnlyActionError
#===================================================================================================
class FileOnlyActionError(FileError):
    def GetMessage(self, filename):
        return 'Action performed over "%s" only possible with a file.' % filename
