'''
Inspired in a code obtained from the INTERNET.
    http://www.thescripts.com/forum/thread46361.html
'''


#===================================================================================================
# ReraiseKeyError
#===================================================================================================
class ReraiseKeyError(KeyError):
    '''
        Replaces KeyError storing the original message. This is used to keep the EOL in the message
    '''

    def __init__(self, message):
        KeyError.__init__(self, message)
        self._message = message

    def __str__(self):
        return self._message



#===================================================================================================
# ReraiseSyntaxError
#===================================================================================================
class ReraiseSyntaxError(SyntaxError):
    '''
    Replaces SyntaxError storing the original message. This is used because a syntax error
    does not use the 'message' attribute to change the message of the error.
    '''

    def __init__(self, message):
        SyntaxError.__init__(self, message)
        self._message = message

    def __str__(self):
        return self._message



#===================================================================================================
# Reraise
#===================================================================================================
def Reraise(exception, message):
    '''
    In Python 2.5 overriding the exception "__str__" has no effect in "str()". Instead, we must
    change the "args" attribute which is used to build the string representation.

    Even though the documentation says "args" will be deprecated, it uses its first argument in
    str() implementation and not "message".
    '''
    import sys



    # >>> Get the current message
    current_message = str(exception)
    if not current_message.startswith('\n'):
        current_message = '\n' + current_message

    # >>> Build the new message
    message = '\n' + message + current_message

    # >>> Special case: OSError
    #     Create a new exception, since OSError behaves differently from other exceptions
    if isinstance(exception, OSError):
        exception = RuntimeError(message)
    # >>> Replace KeyError by RuntimeError to keep the line-ends.
    if isinstance(exception, KeyError):
        exception = ReraiseKeyError(message)
    elif isinstance(exception, SyntaxError):
        exception = ReraiseSyntaxError(message)
    else:
        exception.message = message
        exception.args = (exception.message,)

    # >>> Reraise the exception with the EXTRA message information
    raise exception, None, sys.exc_info()[-1]
