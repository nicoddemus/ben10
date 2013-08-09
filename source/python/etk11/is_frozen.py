#===================================================================================================
# frozen
# Setup the sys.frozen attribute when the application is not in release mode.
# This attribute is automatically set when the source code is in an executable.
#
# Use "IsFrozen" instead of "sys.frozen == False" because some libraries (pywin32) checks for the
# attribute existence, not the value.
#===================================================================================================
import sys

_is_frozen = hasattr(sys, 'frozen') and getattr(sys, 'frozen')

def IsFrozen():
    return _is_frozen
