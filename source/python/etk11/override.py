


#===================================================================================================
# Override
#===================================================================================================
def Override(method):
    '''
    Decorator that marks that a method overrides a method in the superclass.
        
    :param type method:
        The overridden method
    
    :rtype: type
    :returns:
        The decorated function
    
    .. note:: this decorator actually works by only making the user to access the class and
    the overridden method at class level scope, so if in the future that method gets
    deleted or renamed, the import of the decorated method will fail.
    '''
    def Wrapper(func):
        if func.__name__ != method.__name__:
            msg = "Wrong @Override: %r expected, but overwriting %r."
            msg = msg % (func.__name__, method.__name__)
            raise AssertionError(msg)

        if func.__doc__ is None:
            func.__doc__ = method.__doc__

        return func

    return Wrapper
