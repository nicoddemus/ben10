
#===================================================================================================
# DumpDirHashToStringIO
#===================================================================================================
def DumpDirHashToStringIO(directory, stringio, base='', exclude=None, include=None):
    '''
    Helper to iterate over the files in a directory putting those in the passed StringIO in ini
    format.
    
    :param str directory:
        The directory for which the hash should be done.
        
    :param StringIO stringio:
        The string to which the dump should be put.
        
    :param str base:
        If provided should be added (along with a '/') before the name=hash of file.
        
    :param str exclude:
        Pattern to match files to exclude from the hashing. E.g.: *.gz
        
    :param str include:
        Pattern to match files to include in the hashing. E.g.: *.zip
    '''
    from path import path
    p = path(directory)
    for f in p.files():
        if include is not None:
            if not f.fnmatch(include):
                continue

        if exclude is not None:
            if f.fnmatch(exclude):
                continue

        md5 = Md5Hex(f)
        if base:
            stringio.write('%s/%s=%s\n' % (base, f.name, md5))
        else:
            stringio.write('%s=%s\n' % (f.name, md5))


#===================================================================================================
# Md5Hex
#===================================================================================================
def Md5Hex(filename=None, contents=None):
    '''
    :param str filename:
        The file from which the md5 should be calculated. If the filename is given, the contents
        should NOT be given.
        
    :param str contents:
        The contents for which the md5 should be calculated. If the contents are given, the filename
        should NOT be given.
        
    :rtype: str
    :returns:
        Returns a string with the hex digest of the stream.
    '''
    import hashlib
    md5 = hashlib.md5()

    if filename:
        stream = file(filename, 'rb')
        try:
            while True:
                data = stream.read(md5.block_size * 128)
                if not data:
                    break
                md5.update(data)
        finally:
            stream.close()

    else:
        md5.update(contents)

    return md5.hexdigest()
