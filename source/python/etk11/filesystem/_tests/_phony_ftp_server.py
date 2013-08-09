#===================================================================================================
# PhonyFtpServer
#===================================================================================================
class PhonyFtpServer(object):
    '''
    Creates a phony ftp-server in the given port serving the given directory. Register
    two users:
        - anonymous 
        - dev (password: 123)
        
    Both users map to the given directory.
    '''

    def __init__(self, directory):
        self._directory = directory


    def Start(self, port=0):
        '''
        :param int port:
            The port to serve.
            Default to zero with selects an available port (return value)
            
        :rtype: int
        :returns:
            The port the ftp-server is serving
        '''
        from threading import Thread
        from pyftpdlib import ftpserver

        authorizer = ftpserver.DummyAuthorizer()
        authorizer.add_user("dev", "123", self._directory, perm="elradfmw")
        authorizer.add_anonymous(self._directory)

        handler = ftpserver.FTPHandler
        handler.authorizer = authorizer

        address = ("127.0.0.1", port)
        self.ftpd = ftpserver.FTPServer(address, handler)
        if port == 0:
            _address, port = self.ftpd.getsockname()

        self.thread = Thread(target=self.ftpd.serve_forever)
        self.thread.start()

        return port


    def Stop(self):
        self.ftpd.stop_serve_forever()
        self.thread.join()
