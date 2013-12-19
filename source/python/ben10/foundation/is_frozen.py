'''
frozen
Setup the sys.frozen attribute when the application is not in release mode.
This attribute is automatically set when the source code is in an executable.

Use "IsFrozen" instead of "sys.frozen == False" because some libraries (pywin32) checks for the
attribute existence, not the value.
'''
import sys



_is_frozen = hasattr(sys, 'frozen') and getattr(sys, 'frozen')


def IsFrozen():
    '''
    Returns true if the code is frozen, that is, the code is inside a generated executable.

    Frozen == False means the we are running the code using Python interpreter, usually associated with the code being
    in development.
    '''
    return _is_frozen


def SetIsFrozen(is_frozen):
    '''
    Sets the is_frozen value manually, overriding the "calculated" value.

    :param bool is_frozen: The new value for is_frozen.
    :returns bool: Returns the original value, before the given value is set.
    '''
    global _is_frozen
    try:
        return _is_frozen
    finally:
        _is_frozen = is_frozen



#===================================================================================================
# IsDevelopment
# The is-development global flag signs we are working in a development environment. This flag is
# used to enable/disable expansive checks during the development and testing phases.
# Since we perform the application checks in the executable we can't use IsFrozen.
# The following checks are tied to this flag:
# - DevelopmentCheckType
# - Interface class check (TODO)
#===================================================================================================
def IsDevelopment():
    '''
    :rtype: bool
    :returns:
        Returns whether we are working in a development (True) or release (False) environment.
    '''
    return not _is_frozen


def SetIsDevelopment(is_development):
    '''
    Set the is-development global value.

    :param bool is_development:
        The new is-development value
    '''
    SetIsFrozen(not is_development)
