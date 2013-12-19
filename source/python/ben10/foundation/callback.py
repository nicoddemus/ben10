from ben10.foundation.decorators import Override
from ben10.foundation.odict import odict
from ben10.foundation.reraise import Reraise
from ben10.foundation.weak_ref import WeakMethodRef
import new
import weakref



#===================================================================================================
# Callback
#===================================================================================================
class Callback(object):
    '''
    Object that provides a way for others to connect in it and later call it to call
    those connected.

    .. note:: This implementation is improved in that it works directly accessing functions based
    on a key in an ordered dict, so, Register, Unregister and Contains are much faster than the
    old callback.

    .. note:: it only stores weakrefs to objects connected

    .. note:: __slots__ added, so, it cannot have weakrefs to it (but as it stores weakrefs
        internally, that shouldn't be a problem). If weakrefs are really needed,
        __weakref__ should be added to the slots.
    '''

    __slots__ = [
        '_callbacks',
        '_handle_errors',
        '__weakref__'  # We need this to be able to add weak references to callback objects.
    ]

    # This constant defines whether the errors will be handled by default in all Callbacks or not.
    # Handled errors won't stop the execution if an exception happens when executing the callbacks.
    DEFAULT_HANDLE_ERRORS = False

    INFO_POS_FUNC_OBJ = 0
    INFO_POS_FUNC_FUNC = 1
    INFO_POS_FUNC_CLASS = 2

    def __init__(self, handle_errors=None):
        '''
        :param bool handle_errors:
            If True, any errors raised while calling the callbacks will not stop the execution
            flow of the application, but will call the system error handler so that error
            does not fail silently.
        '''
        # _callbacks is lazily created!
        if handle_errors is None:
            handle_errors = self.DEFAULT_HANDLE_ERRORS
        self._handle_errors = handle_errors


    def _GetKey(self, func):
        '''
        :param object func:
            The function for which we want the key.

        :rtype: object
        :returns:
            Returns the key to be used to access the object.

        .. note:: The key is guaranteed to be unique among the living objects, but if the object
        is garbage collected, a new function may end up having the same key.
        '''
        if func.__class__ == _CallbackWrapper:
            func = func.OriginalMethod()

        try:
            assert func.im_self is not None, "The listener function must be bound, otherwise it can't be called"
            return (id(func.im_self), id(func.im_func), id(func.im_class))

        except AttributeError:
            # not a method -- a callable: create a strong reference (the CallbackWrapper
            # is depending on this behaviour... is it correct?)
            return id(func)


    def _GetInfo(self, func):
        '''
        :rtype: tuple(func_obj, func_func, func_class)
        :returns:
            Returns a tuple with the information needed to call a method later on (close to the
            WeakMethodRef, but a bit more specialized -- and faster for this context).
        '''
        # Note: if it's a _CallbackWrapper, we want to register it and not the 'original method'
        # at this point
        try:
            if func.im_self is None:
                # unbound method
                return (None, func.im_func, func.im_class)
            else:
                # bound method
                return (weakref.ref(func.im_self), func.im_func, func.im_class)
        except AttributeError:
            # not a method -- a callable: create a strong reference (the CallbackWrapper
            # is depending on this behaviour... is it correct?)
            return (None, func, None)


    def __call__(self, *args, **kwargs):
        '''
        Calls every registered function with the given args and kwargs.
        '''
        # Note: There's a copy of this code in the _CalculateToCall method below. It's a copy
        # because we don't want to had a function call overhead here.
        # ------------------------------------------------------------------------------------------
        try:
            callbacks = self._callbacks
        except AttributeError:
            return  # No callbacks registered

        to_call = []

        for id_, info_and_extra_args in callbacks.items():  # iterate in a copy

            info = info_and_extra_args[0]
            func_obj = info[self.INFO_POS_FUNC_OBJ]
            if func_obj is not None:
                # Ok, we have a self.
                func_obj = func_obj()
                if func_obj is None:
                    # self is dead
                    del callbacks[id_]
                else:
                    func_func = info[self.INFO_POS_FUNC_FUNC]
                    to_call.append(
                        (
                            new.instancemethod(func_func, func_obj, info[self.INFO_POS_FUNC_CLASS]),
                            info_and_extra_args[1]
                        )
                    )
            else:
                func_func = info[self.INFO_POS_FUNC_FUNC]
                if func_func.__class__ == _CallbackWrapper:
                    # The instance of the _CallbackWrapper already died! (func_obj is None)
                    original_method = func_func.OriginalMethod()
                    if original_method is None:
                        del callbacks[id_]
                        continue

                # No self: either classmethod or just callable
                to_call.append((func_func, info_and_extra_args[1]))
        # ------------------------------------------------------------------------------------------

        # let's keep the 'if' outside of the iteration...
        if self._handle_errors:
            for func, extra_args in to_call:
                try:
                    func(*extra_args + args, **kwargs)
                except Exception, e:
                    # Note that if some error shouldn't really be handled here, clients can raise
                    # a subclass of ErrorNotHandledInCallback
                    if isinstance(e, ErrorNotHandledInCallback):
                        Reraise(e, 'Error while trying to call %r' % func)
                    else:
                        HandleErrorOnCallback(func, *extra_args + args, **kwargs)
        else:
            for func, extra_args in to_call:
                try:
                    func(*extra_args + args, **kwargs)
                except Exception, e:
                    Reraise(e, 'Error while trying to call %r' % func)


    def _CalculateToCall(self):
        '''
        Copy of the code above so that subclasses can use it (we don't want the overhead in the
        call above).
        '''
        try:
            callbacks = self._callbacks
        except AttributeError:
            return []  # No callbacks registered

        to_call = []

        for _id, info_and_extra_args in callbacks.items():  # iterate in a copy

            info = info_and_extra_args[0]
            func_obj = info[self.INFO_POS_FUNC_OBJ]
            if func_obj is not None:
                # Ok, we have a self.
                func_obj = func_obj()
                if func_obj is None:
                    # self is dead
                    del callbacks[id]
                else:
                    func_func = info[self.INFO_POS_FUNC_FUNC]
                    to_call.append(
                        (
                            new.instancemethod(func_func, func_obj, info[self.INFO_POS_FUNC_CLASS]),
                            info_and_extra_args[1]
                        )
                    )
            else:
                func_func = info[self.INFO_POS_FUNC_FUNC]
                if func_func.__class__ == _CallbackWrapper:
                    # The instance of the _CallbackWrapper already died! (func_obj is None)
                    original_method = func_func.OriginalMethod()
                    if original_method is None:
                        del callbacks[id]
                        continue

                # No self: either classmethod or just callable
                to_call.append((func_func, info_and_extra_args[1]))

        return to_call


    # Should be OK using a mutable object here as it'll only be accessed internally and
    # should never have anything appended.
    _EXTRA_ARGS_CONSTANT = tuple()


    def Register(self, func, extra_args=_EXTRA_ARGS_CONSTANT):
        '''
        Registers a function in the callback.

        :param object func:
            Method or function that will be called later.

        :param list(object) extra_args:
            A list with the objects to be used
        '''
        if extra_args is not self._EXTRA_ARGS_CONSTANT:
            extra_args = tuple(extra_args)

        key = self._GetKey(func)
        try:
            callbacks = self._callbacks
        except:
            callbacks = self._callbacks = odict()

        callbacks.pop(key, None)  # Remove if it exists
        callbacks[key] = (self._GetInfo(func), extra_args)


    def Contains(self, func):
        '''
        :param object func:
            The function that may be contained in this callback.

        :rtype: bool
        :returns:
            True if the function is already registered within the callbacks and False
            otherwise.
        '''
        key = self._GetKey(func)

        try:
            callbacks = self._callbacks
        except AttributeError:
            return False

        info_and_extra_args = callbacks.get(key)
        if info_and_extra_args is None:
            return False

        # We must check if it's actually the same, because it may be that the ids we've gotten for
        # this object were actually from a garbage-collected function that was previously registered.

        info = info_and_extra_args[0]
        func_obj = info[self.INFO_POS_FUNC_OBJ]
        func_func = info[self.INFO_POS_FUNC_FUNC]
        if func_obj is not None:
            # Ok, we have a self.
            func_obj = func_obj()
            if func_obj is None:
                # self is dead
                del callbacks[key]
                return False
            else:
                return func == new.instancemethod(
                    func_func, func_obj, info[self.INFO_POS_FUNC_CLASS])
        else:
            if func_func.__class__ == _CallbackWrapper:
                # The instance of the _CallbackWrapper already died! (func_obj is None)
                original_method = func_func.OriginalMethod()
                if original_method is None:
                    del callbacks[key]
                    return False
                return original_method == func

            if func_func == func:
                return True
            try:
                f = func.im_func
            except AttributeError:
                return False
            else:
                return f == func_func


    def Unregister(self, func):
        '''
        Unregister a function previously registered with Register.

        :param object func:
            The function to be unregistered.
        '''
        key = self._GetKey(func)

        try:
            # As there can only be 1 instance with the same id alive, it should be OK just
            # deleting it directly (because if there was a dead reference pointing to it it will
            # be already dead anyways)
            del self._callbacks[key]
        except (KeyError, AttributeError):
            # Even when unregistering some function that isn't registered we shouldn't trigger an
            # exception, just do nothing
            pass



    def UnregisterAll(self):
        '''
        Unregisters all functions
        '''
        try:
            del self._callbacks
        except AttributeError:
            # The _callbacks attribute only exists after a callback is registered,
            #    so we can ignore this error.
            pass


    def __len__(self):
        try:
            return len(self._callbacks)
        except AttributeError:
            return 0  # Ignore: no self._callbacks.



#===================================================================================================
# Callbacks
#===================================================================================================
class Callbacks(object):
    '''
    Holds created callbacks, making it easy to disconnect later.

    Note: keeps a strong reference to the callback and the sender, thus, they won't be garbage-
    collected while still connected in this case.
    '''

    def __init__(self):
        self._callbacks = []


    def Before(self, sender, *callbacks, **kwargs):
        sender = Before(sender, *callbacks, **kwargs)
        for callback in callbacks:
            self._callbacks.append((sender, callback))
        return sender


    def After(self, sender, *callbacks, **kwargs):
        sender = After(sender, *callbacks, **kwargs)
        for callback in callbacks:
            self._callbacks.append((sender, callback))
        return sender


    def RemoveAll(self):
        for sender, callback in self._callbacks:
            Remove(sender, callback)
        self._callbacks[:] = []


#===================================================================================================
# PriorityCallback
#===================================================================================================
class PriorityCallback(Callback):
    '''
    Class that's able to give a priority to the added callbacks when they're registered.
    '''

    INFO_POS_PRIORITY = 3

    @Override(Callback._GetInfo)
    def _GetInfo(self, func, priority):
        '''
        Overridden to add the priority to the info.

        :param int priority:
            The priority to be set to the added callback.
        '''
        info = Callback._GetInfo(self, func)
        return info + (priority,)


    @Override(Callback.Register)
    def Register(self, func, extra_args=Callback._EXTRA_ARGS_CONSTANT, priority=5):
        '''
        Register a function in the callback.
        :param object func:
            Method or function that will be called later.

        :param int priority:
            If passed, it'll be be used to put the callback into the correct place based on the
            priority passed (lower numbers have higher priority).
        '''
        if extra_args is not self._EXTRA_ARGS_CONSTANT:
            extra_args = tuple(extra_args)

        key = self._GetKey(func)
        try:
            callbacks = self._callbacks
        except AttributeError:
            callbacks = self._callbacks = odict()

        callbacks.pop(key, None)  # Remove if it exists
        new_info = self._GetInfo(func, priority)

        i = 0
        for i, (info, _extra) in enumerate(callbacks.itervalues()):
            if info[self.INFO_POS_PRIORITY] > priority:
                break
        else:
            # Iterated all... so, go one more the last position.
            i += 1

        callbacks.insert(i, key, (new_info, extra_args))



#===================================================================================================
# _CallbackWrapper
#===================================================================================================
class _CallbackWrapper(object):

    def __init__(self, weak_method_callback):
        self.weak_method_callback = weak_method_callback

        # Maintaining the OriginalMethod() interface that clients expect.
        self.OriginalMethod = weak_method_callback

    def __call__(self, sender, *args, **kwargs):
        c = self.weak_method_callback()

        assert c is not None, (
            'This should never happen: '
            'The sender already died, so, how can this method still be called?'
        )
        c(sender(), *args, **kwargs)



#===================================================================================================
# Shortcuts
#===================================================================================================

def Before(method, callback, sender_as_parameter=False):
    '''
        Registers the given callback to be executed before the given method is called, with the
        same arguments.

        The method can be eiher an unbound method or a bound method. If it is an unbound method,
        *all* instances of the class will generate callbacks when method is called. If it is a bound
        method, only the method of the instance will generate callbacks.

        Remarks:
            The function has changed its signature to accept an extra parameter (sender_as_parameter).
            Using "*args" as before made impossible to add new parameters to the function.
    '''
    return _CreateBeforeOrAfter(method, callback, sender_as_parameter)



def After(method, callback, sender_as_parameter=False):
    '''
        Registers the given callbacks to be execute after the given method is called, with the same
        arguments.

        The method can be eiher an unbound method or a bound method. If it is an unbound method,
        *all* instances of the class will generate callbacks when method is called. If it is a bound
        method, only the method of the instance will generate callbacks.

        Remarks:
            This function has changed its signature to accept an extra parameter (sender_as_parameter).
            Using "*args" as before made impossible to add new parameters to the function.
    '''
    return _CreateBeforeOrAfter(method, callback, sender_as_parameter, before=False)



def Remove(method, callback):
    '''
        Removes the given callback from a method previously connected using after or before.
        Return true if the callback was removed, false otherwise.
    '''
    wrapped = _GetWrapped(method)
    if wrapped:
        return wrapped.Remove(callback)
    return False



#===================================================================================================
# Implementation Details
#===================================================================================================

def _CreateBeforeOrAfter(method, callback, sender_as_parameter, before=True):

    wrapper = WrapForCallback(method)
    original_method = wrapper.OriginalMethod()

    extra_args = []

    if sender_as_parameter:
        im_self = original_method.im_self
        extra_args.append(weakref.ref(im_self))

        # this is not garbage collected directly when added to the wrapper (which will create a WeakMethodRef to it)
        # because it's not a real method, so, WeakMethodRef will actually maintain a strong reference to it.
        callback = _CallbackWrapper(WeakMethodRef(callback))

    if before:
        wrapper.AppendBefore(callback, extra_args)
    else:
        wrapper.AppendAfter(callback, extra_args)

    return wrapper



#===================================================================================================
# CallbackMethodWrapper
#===================================================================================================
class CallbackMethodWrapper:  # It needs to be a subclass of Method for interface checks.

    __slots__ = [
        '_before',
        '_after',
        '_method',
        '_name',
        'OriginalMethod',
    ]

    def __init__(self, method):
        self._before = None
        self._after = None
        self._method = WeakMethodRef(method)
        self._name = method.__name__

        # Maintaining the OriginalMethod() interface that clients expect.
        self.OriginalMethod = self._method


    def __call__(self, *args, **kwargs):

        if self._before is not None:
            self._before(*args, **kwargs)

        m = self._method()
        if m is None:
            raise ReferenceError(
                "Error: the object that contained this method (%s) has already been garbage collected"
                % self._name)

        result = m(*args, **kwargs)

        if self._after is not None:
            self._after(*args, **kwargs)

        return result

    def AppendBefore(self, callback, extra_args, handle_errors=True):
        '''
            Append the given callbacks in the list of callback to be executed BEFORE the method.
        '''
        assert isinstance(extra_args, list)
        if self._before is None:
            self._before = Callback(handle_errors=handle_errors)
        self._before.Register(callback, extra_args)


    def AppendAfter(self, callback, extra_args, handle_errors=True):
        '''
        Append the given callbacks in the list of callback to be executed AFTER the method.
        '''

        assert isinstance(extra_args, list)
        if self._after is None:
            self._after = Callback(handle_errors=handle_errors)
        self._after.Register(callback, extra_args)


    def Remove(self, callback):
        '''
        Remove the given callback from both the BEFORE and AFTER callbacks lists.
        '''
        result = False

        if self._before is not None and self._before.Contains(callback):
            self._before.Unregister(callback)
            result = True
        if self._after is not None and self._after.Contains(callback):
            self._after.Unregister(callback)
            result = True

        return result



#===================================================================================================
# _GetWrapped
#===================================================================================================
def _GetWrapped(method):
    '''
        Returns true if the given method is already wrapped.
    '''
    if isinstance(method, CallbackMethodWrapper):
        return method
    try:
        return method._wrapped_instance
    except AttributeError:
        return None



#===================================================================================================
# WrapForCallback
#===================================================================================================
def WrapForCallback(method):
    '''
    Generates a wrapper for the given method, or returns the method itself if it is already a
    wrapper.
    '''
    wrapped = _GetWrapped(method)
    if wrapped is not None:
        # its a wrapper already
        if not hasattr(method, 'im_self'):
            return wrapped

        # Taking care for the situation where we add a callback to the class and later to the
        # instance.
        # Note that the other way around does not work at all (i.e.: if a callback is first added
        # to the instance, there's no way we'll find about that when adding it to the class
        # anyways).
        if method.im_self is None:
            if wrapped._method._obj is None:
                return wrapped

    wrapper = CallbackMethodWrapper(method)
    if method.im_self is None:
        # override the class method

        # we must make it a regular call for classmethods (it MUST not be a bound
        # method nor class when doing that).
        def call(*args, **kwargs):
            return wrapper(*args, **kwargs)
        call.__name__ = method.__name__
        call._wrapped_instance = wrapper

        setattr(method.im_class, method.__name__, call)
    else:
        # override the instance method
        setattr(method.im_self, method.__name__, wrapper)
    return wrapper



#===================================================================================================
# FunctionNotRegisteredError
#===================================================================================================
class FunctionNotRegisteredError(RuntimeError):
    pass



#===================================================================================================
# ErrorNotHandledInCallback
#===================================================================================================
class ErrorNotHandledInCallback(RuntimeError):
    '''
    This class identifies an error that should not be handled in the callback.
    '''



#===================================================================================================
# HandleErrorOnCallback
#===================================================================================================
def HandleErrorOnCallback(func, *args, **kwargs):
    '''
    Called when there's some error calling a callback.

    :param object func:
        The callback called.

    :param list args:
        The arguments passed to the callback.

    :param dict kwargs:
        The keyword arguments passed to the callback.
    '''
    if hasattr(func, 'func_code'):
        name, filename, line = (
            func.func_code.co_name,
            func.func_code.co_filename,
            func.func_code.co_firstlineno
        )
        # Use default python trace format so that we have linking on pydev.
        func = '\n  File "%s", line %s, in %s (Called from Callback)\n' % (filename, line, name)
    else:
        # That's ok, it may be that it's not really a method.
        func = '%r\n' % (func,)

    msg = 'Error while trying to call %s' % (func,)
    if args:
        msg += 'Args: %s\n' % (args,)
    if kwargs:
        msg += 'Kwargs: %s\n' % (kwargs,)

    from ben10.foundation import handle_exception
    handle_exception.HandleException(msg)

