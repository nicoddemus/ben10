import contextlib


#=======================================================================================================================
# PushPop
#=======================================================================================================================
@contextlib.contextmanager
def PushPop(obj, name, value):
    old_value = getattr(obj, name)
    setattr(obj, name, value)
    yield value
    setattr(obj, name, old_value)
