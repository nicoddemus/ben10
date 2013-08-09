


#===================================================================================================
# Implements
#===================================================================================================
def Implements(method):
    '''
    Decorator that marks that a method implements a method in some interface.
        
    :param function method:
        The implemented method
    
    :rtype: function 
    :returns:
        The decorated function
    
    .. note:: this decorator actually works by only making the user to access the class and
    the implemented method at class level scope, so if in the future that method gets
    deleted or renamed, the import of the decorated method will fail.
    
    :raises AssertionError:
        if the implementation method's name is different from the one
        that is being defined. This is a common error when copying/pasting the @Implements code.
    '''
    def Wrapper(func):
        if func.__name__ != method.__name__:
            msg = "Wrong @Implements: %r expected, but overwriting %r."
            msg = msg % (func.__name__, method.__name__)
            raise AssertionError(msg)

        if func.__doc__ is None:
            func.__doc__ = method.__doc__

        return func

    return Wrapper
