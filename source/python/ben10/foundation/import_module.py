


#===================================================================================================
# ImportModule
#===================================================================================================
def ImportModule(p_import_path):
    '''
        Import the module in the given import path.
        
        * Returns the "final" module, so importing "coilib50.subject.visu" return the "visu"
        module, not the "coilib50" as returned by __import__
    '''
    try:
        result = __import__(p_import_path)
        for i in p_import_path.split('.')[1:]:
            result = getattr(result, i)
        return result
    except ImportError, e:
        from _reraise import Reraise
        Reraise(
            e,
            'Error importing module %s' % p_import_path)



#===================================================================================================
# ImportToken
#===================================================================================================
def ImportToken(path):
    '''
    The import token extends the functionality provided by ImportModule by importing members inside
    other members. This is useful to import constants, exceptions and enums wich are usually
    declared inside other module.
    
    '''
    try:
        return ImportModule(path)
    except ImportError:
        try:
            mod, name = path.rsplit('.', 1)
        except ValueError:
            raise ImportError('Cannot import %s' % (path,))

        try:
            ret = ImportToken(mod)
        except ImportError:
            raise ImportError('Cannot import %s' % (path,))
        try:
            return getattr(ret, name)
        except AttributeError:
            raise ImportError('Cannot find %s in module: %s' % (ret, mod))
