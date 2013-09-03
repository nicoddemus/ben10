from etk11.foundation.platform_ import Platform



#=======================================================================================================================
# IsUrlEqual
#=======================================================================================================================
def IsUrlEqual(url_or_path_1, url_or_path_2):
    '''
    :param str url_or_path_1:
    
    :param str url_or_path_2:
    
    :rtype: bool
    :returns:
        True if Url's are equal.
        
        Ignores case if url protocol is 'file' in a Windows machine (Windows ignores case for local
        directories).
    '''
    from urlparse import urlparse

    protocol = urlparse(url_or_path_1)[0].lower()
    is_local = protocol == 'file'

    # Ignore case if dealing with a local file in a Windows machine
    if is_local:
        is_windows = Platform.GetCurrentFlavour() == 'windows'
        if is_windows:
            return url_or_path_1.lower() == url_or_path_2.lower()

    # All other cases are case sensitive
    return url_or_path_1 == url_or_path_2



#=======================================================================================================================
# HideURLPassword
#=======================================================================================================================
def HideURLPassword(url):
    '''
    Hides username and password in a URL, useful when you want to print an URL without showing
    protected information.
    
    :param str url:
        A URL
    
    :rtype: str
    :returns:
        The given FTP URL with hidden username and password
    '''
    import re
    return re.sub('(\w+)://[^@]*@(.*)', '\\1://USERNAME:PASSWORD@\\2', url, count=1)
