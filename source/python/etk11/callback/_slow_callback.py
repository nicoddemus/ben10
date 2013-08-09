from etk11.reraise import Reraise
from _callback_wrapper import _CallbackWrapper



#===================================================================================================
# SlowCallback
#===================================================================================================
class SlowCallback(object):
    '''
    Object that provides a way for others to connect in it and later call it to call
    those connected.
    
    .. note:: this implementation is the old implementation and should be removed soon (still around
    because of the events manager).
    
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
    DEFAULT_THROW_ERROR_ON_UNREGISTER = True

    def __init__(self, handle_errors=None):
        '''
        Constructor.
        
        :param bool handle_errors:
            If True, any errors raised while calling the callbacks will not stop the execution
            flow of the application, but will call the system error handler so that error
            does not fail silently.
        '''
        self._callbacks = []  # a list of (weakmethod, [extra_args]) instance.
        if handle_errors is None:
            handle_errors = self.DEFAULT_HANDLE_ERRORS
        self._handle_errors = handle_errors


    def __call__(self, *args, **kwargs):
        '''Calls every registered function with the given args and kwargs.
        '''
        # Note: Event.__call__ copies the code below (so, changes must be propagated).
        callbacks = []
        to_call = []

        for ref_and_args in self._callbacks:
            ref, extra_args = ref_and_args

            original_method = ref()
            initial_original_method = original_method
            if type(original_method) == _CallbackWrapper:
                original_method = original_method.OriginalMethod()

            if original_method is not None:
                callbacks.append(ref_and_args)
                to_call.append((initial_original_method, extra_args))

        self._callbacks = callbacks
        # End copied code


        # let's keep the 'if' outside of the iteration...
        if self._handle_errors:
            for func, extra_args in to_call:
                try:
                    func(*extra_args + list(args), **kwargs)
                except Exception, e:
                    from _callback import ErrorNotHandledInCallback
                    # Note that if some error shouldn't really be handled here, clients can raise
                    # a subclass of ErrorNotHandledInCallback
                    if isinstance(e, ErrorNotHandledInCallback):
                        Reraise(e, 'Error while trying to call %r' % func)
                    else:
                        from _callback import HandleErrorOnCallback
                        HandleErrorOnCallback(func, *extra_args + list(args), **kwargs)
        else:
            for func, extra_args in to_call:
                try:
                    func(*extra_args + list(args), **kwargs)
                except Exception, e:
                    Reraise(e, 'Error while trying to call %r' % func)


    _EXTRA_ARGS_CONSTANT = tuple()

    def Register(self, func, extra_args=_EXTRA_ARGS_CONSTANT):
        '''
            Register a function in the callback.
            :type func: method or function that will be called later.
            :param func:
        '''
        if self.Contains(func):
            self.Unregister(func)
        if extra_args is self._EXTRA_ARGS_CONSTANT:
            extra_args = []

        ref = WeakMethodRef(func)
        self._callbacks.append((ref, extra_args))


    def Contains(self, func):
        '''@return: True if the function is already registered within the callbacks and False
        otherwise.
        '''
        for ref, _extra_args in self._callbacks:
            original_method = ref()
            if type(original_method) == _CallbackWrapper:
                original_method = original_method.OriginalMethod()

            if self._IsSameCallable(original_method, func):
                return True
        return False


    def Unregister(self, func):
        '''Unregister a function previously registered with C{Register}.
        :type func: the function to be unregistered.
        :param func:
        '''
        for index, (ref, _extra_args) in enumerate(self._callbacks):
            original_method = ref()
            if type(original_method) == _CallbackWrapper:
                original_method = original_method.OriginalMethod()

            if self._IsSameCallable(original_method, func):
                del self._callbacks[index]
                break
        else:
            if self.DEFAULT_THROW_ERROR_ON_UNREGISTER:
                from _callback import FunctionNotRegisteredError
                raise FunctionNotRegisteredError('Function "%s" was not registered.' % func)


    def _IsSameCallable(self, func1, func2):
        '''
        Checks if the given callables are the same.
        
        This has two implementations because of the differences between functions and bound-methods:
        in the case of functions, we simply check for identity of the functions. If it is a 
        method, we have to check for the identity of both the referee and the function.
         
        :type func1: C{function} or C{bound-method}
        :param func1:
            first callable to check
        
        :type func2: C{function} or C{bound-method}
        :param func2:
            second callable to check
        
        .. note:: we have to use this function because simply using the "is" operator won't work
               for bound-methods, since every time the callback is referenced from the instance,
               a new bound-method instance is created.
        '''
        import types
        if isinstance(func1, types.MethodType) and isinstance(func2, types.MethodType):
            return func1.im_self is func2.im_self and func1.im_func is func2.im_func
        else:
            return func1 is func2


    def UnregisterAll(self):
        '''Unregister all functions
        '''
        self._callbacks = []


    def __len__(self):
        return len(self._callbacks)


