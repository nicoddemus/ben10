'''
Implements PushPop "context manager", a generic attribute stack.

Example::

  with PushPop(sys, 'stdout', StringIO()) as output:
    print "Hello, world!"
    assert output.gettext() == "Hello, world!"
'''
import contextlib


#=======================================================================================================================
# PushPop
#=======================================================================================================================
@contextlib.contextmanager
def PushPop(obj, name, value):
    '''
    A context manager to replace and restore a variable/attribute.
    
    :param object obj: The object to replace/restore
    :param str name: The variable/attribute to replace/restore
    :param object value: The value to replace 
    '''
    old_value = getattr(obj, name)
    setattr(obj, name, value)
    yield value
    setattr(obj, name, old_value)
