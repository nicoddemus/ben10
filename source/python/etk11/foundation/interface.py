import inspect
import sys

from etk11.foundation import immutable
from etk11.foundation.decorators import Override, Deprecated
from etk11.foundation.is_frozen import IsFrozen
from etk11.foundation.klass import IsInstance
from etk11.foundation.memoize import Memoize
from etk11.foundation.odict import odict
from etk11.foundation.reraise import Reraise
from etk11.foundation.types_ import Null
from etk11.foundation.weak_ref import WeakMethodRef


#===================================================================================================
# InterfaceError
#===================================================================================================
class InterfaceError(RuntimeError):
    pass



#===================================================================================================
# BadImplementationError
#===================================================================================================
class BadImplementationError(InterfaceError):
    pass



#===================================================================================================
# InterfaceImplementationMetaClass
#===================================================================================================
class InterfaceImplementationMetaClass(type):
    def __new__(cls, name, bases, dct):
        C = type.__new__(cls, name, bases, dct)
        if not IsFrozen():  # Only doing check in dev mode.
            for I in dct.get('__implements__', []):
                AssertImplementsFullChecking(C, I, check_attr=False)
        return C



#===================================================================================================
# InterfaceImplementorStub
#===================================================================================================
class InterfaceImplementorStub(object):
    '''
    A helper for acting as a stub for some object (in this way, we're only able to access
    attributes declared directly in the interface.

    It forwards the calls to the actual implementor (the wrapped object)
    '''

    def __init__(self, wrapped, implemented_interface):
        self.__wrapped = wrapped
        self.__implemented_interface = implemented_interface

        self.__interface_methods, self.__attrs = \
            cache_interface_attrs.GetInterfaceMethodsAndAttrs(implemented_interface)


    def GetWrappedFromImplementorStub(self):
        '''
        Really big and awkward name because we don't want name-clashes
        '''
        return self.__wrapped


    def __getattr__(self, attr):
        if attr not in self.__attrs and attr not in self.__interface_methods:
            raise AttributeError("Error. The interface %s does not have the attribute '%s' declared." % (self.__implemented_interface, attr))
        return getattr(self.__wrapped, attr)


    def __getitem__(self, *args, **kwargs):
        if '__getitem__' not in self.__interface_methods:
            raise AttributeError("Error. The interface %s does not have the attribute '%s' declared." % (self.__implemented_interface, '__getitem__'))
        return self.__wrapped.__getitem__(*args, **kwargs)

    def __setitem__(self, *args, **kwargs):
        if '__setitem__' not in self.__interface_methods:
            raise AttributeError("Error. The interface %s does not have the attribute '%s' declared." % (self.__implemented_interface, '__setitem__'))
        return self.__wrapped.__setitem__(*args, **kwargs)

    def __repr__(self):
        return '<InterfaceImplementorStub %s>' % self.__wrapped

    def __call__(self, *args, **kwargs):
        if '__call__' not in self.__interface_methods:
            raise AttributeError("Error. The interface %s does not have the attribute '%s' declared." % (self.__implemented_interface, '__call__'))
        return self.__wrapped.__call__(*args, **kwargs)



#=======================================================================================================================
# Interface
#=======================================================================================================================
class Interface(object):
    '''Base class for interfaces.
    
    A interface describes a behavior that some objects must implement.
    '''

    # : instance to check if we are receiving an argument during __new__
    _SENTINEL = []

    def __new__(cls, class_=_SENTINEL):
        # if no class is given, raise InterfaceError('trying to instantiate interface')
        # check if class_or_object implements this interface

        if class_ is cls._SENTINEL:
            raise InterfaceError('Can\'t instantiate Interface.')
        else:
            if isinstance(class_, type):
                # We're doing something as Interface(InterfaceImpl) -- not instancing
                AssertImplementsFullChecking(class_, cls, check_attr=False)
                return class_
            elif isinstance(class_, InterfaceImplementorStub):
                return class_
            else:
                implemented_interfaces = GetImplementedInterfaces(class_)

                if cls in implemented_interfaces:
                    return InterfaceImplementorStub(class_, cls)

                elif IAdaptable in implemented_interfaces:
                    adapter = class_.GetAdapter(cls)
                    if adapter is not None:
                        return InterfaceImplementorStub(adapter, cls)

                # We're doing something as Interface(InterfaceImpl()) -- instancing
                AssertImplementsFullChecking(class_, cls, check_attr=True)
                return InterfaceImplementorStub(class_, cls)



#=======================================================================================================================
# IAdaptable
#=======================================================================================================================
class IAdaptable(Interface):
    '''
        An interface for an object that is adaptable.
        
        Adaptable objects can be queried about interfaces they adapt to (to which they
        may respond or not).
        
        For example:
        
        a = [some IAdaptable];
        x = a.GetAdapter(IFoo);
        if x is not None:
            [do IFoo things with x]
    '''

    def GetAdapter(self, interface_class):
        '''
            :type interface_class: this is the interface for which an adaptation is required
            :param interface_class:
            :rtype: an object implementing the required interface or None if this object cannot
            adapt to that interface.
        '''



#=======================================================================================================================
# IsImplementation
#=======================================================================================================================
@Deprecated('IsImplementationFullChecking')
def IsImplementation(class_or_instance, interface):
    '''
    Deprecated: 44547: Remove AssertImplements and IsImplementation
    '''
    return IsImplementationFullChecking(class_or_instance, interface)


#===================================================================================================
# IsImplementationFullChecking
#===================================================================================================
def IsImplementationFullChecking(class_or_instance, interface):
    '''
    Returns True if the given object or class implements the given interface.
    
    :type class_or_instance: type or instance
    :param class_or_instance:
        Class or instance to check
    
    :param interface.Interface interface:
        Interface to check
    
    :rtype: bool
    :returns:
        If it implements the interface
    '''
    try:
        AssertImplementsFullChecking(class_or_instance, interface)
    except BadImplementationError:
        return False
    else:
        return True



#===================================================================================================
# CacheInterfaceAttrs
#===================================================================================================
class CacheInterfaceAttrs(object):
    '''
        Cache for holding the attrs for a given interface (separated by attrs and methods).
    '''

    def __GetInterfaceMethodsAndAttrs(self, interface):
        '''
            :type interface: the interface from where the methods and attributes should be gotten.
            :param interface:
            :rtype: the interface methods and attributes available in a given interface.
        '''
        all_attrs = dir(interface)

        interface_methods = dict()
        interface_attrs = dict()

        for attr in all_attrs:
            val = getattr(interface, attr)
            if type(val) in (Attribute, ReadOnlyAttribute, ScalarAttribute):
                interface_attrs[attr] = val

            if _IsMethod(val, False):
                interface_methods[attr] = val

        return interface_methods, interface_attrs

    def GetInterfaceMethodsAndAttrs(self, interface):
        '''
            We have to make the creation of the ImmutableParamsCacheManager lazy because
            otherwise we'd enter a cyclic import.
            
            :type interface: the interface from where the methods and attributes should be gotten
            :param interface:
                (used as the cache-key)
            :rtype: @see: CacheInterfaceAttrs.__GetInterfaceMethodsAndAttrs
        '''
        try:
            cache = self.cache
        except AttributeError:
            # create it on the 1st access
            cache = self.cache = ImmutableParamsCachedMethod(self.__GetInterfaceMethodsAndAttrs)
        return cache(interface)



# cache for the interface attrs (for Methods and Attrs).
cache_interface_attrs = CacheInterfaceAttrs()

#===================================================================================================
# _IsMethod
#===================================================================================================
def _IsMethod(member, include_functions):
    '''
    Consider method the following:
        1) Methods
        2) Functions (if include_functions is True)
        3) instances of Method (should it be implementors of "IMethod"?)
        
    USER: cache mechanism for coilib50.basic.process
    '''
    if include_functions and inspect.isfunction(member):
        return True
    elif inspect.ismethod(member):
        return True
    elif isinstance(member, Method):
        return True
    return False



#===================================================================================================
# AssertImplements
#===================================================================================================
@Deprecated('AssertImplementsFullChecking')
def AssertImplements(class_or_instance, interface, check_attr=True):
    '''
    Deprecated: 44547: Remove AssertImplements and IsImplementation
    '''
    return AssertImplementsFullChecking(class_or_instance, interface, check_attr=check_attr)


#===================================================================================================
# AssertImplementsFullChecking
#===================================================================================================
def AssertImplementsFullChecking(class_or_instance, interface, check_attr=True):
    '''
    Make sure the object or class implements the given interface. 
    
    This method will check each member of the given instance (or class) comparing them against the
    ones declared in the interface, making sure that it actually implements it even if it does not
    declare it so using interface.Implements.
    
    .. note:: this method is *slow*, so make sure to never use it in hot-spots. Usually you should
           use AssertDeclaresInterface, which is much faster. 
    
    @raise: BadImplementationError class_or_instance doesn't implement this interface.
    
    :type chk_attr: bool, verify attributes in instance or not
    :param chk_attr:
    '''
    # Moved from the file to avoid cyclic import:
    try:
        is_interface = issubclass(interface, Interface)
    except TypeError, e:
        Reraise(e, "interface=%s (type %s)" % (interface, type(interface)))

    if not is_interface:
        raise InterfaceError(
            'To check against an interface, an interface is required (received: %s -- mro:%s)' %
            (interface, interface.__mro__)
        )

    if isinstance(class_or_instance, Null):
        return True

    try:
        classname = class_or_instance.__name__
    except:
        classname = class_or_instance.__class__.__name__


    if classname == 'InterfaceImplementorStub':
        return AssertImplementsFullChecking(class_or_instance.GetWrappedFromImplementorStub(), interface, check_attr)

    interface_methods, interface_attrs = cache_interface_attrs.GetInterfaceMethodsAndAttrs(interface)
    if check_attr:
        for attr_name, val in interface_attrs.iteritems():
            if hasattr(class_or_instance, attr_name):
                attr = getattr(class_or_instance, attr_name)
                match, match_msg = val.Match(attr)
                if not match:
                    msg = 'Attribute %r for class %s does not match the interface %s'
                    msg = msg % (attr_name, class_or_instance, interface)
                    if match_msg:
                        msg += ': ' + match_msg
                    raise BadImplementationError(msg)
            else:
                msg = 'Attribute %r is missing in class %s and it is required by interface %s'
                msg = msg % (attr_name, class_or_instance, interface)
                raise BadImplementationError(msg)


    def GetArgSpec(method):
        '''
            Get the arguments for the method, considering the possibility of instances of Method,
            in which case, we must obtain the arguments of the instance "__call__" method.
            
            USER: cache mechanism for coilib50.basic.process
        '''
        if isinstance(method, Method):
            return inspect.getargspec(method.__call__)
        else:
            return inspect.getargspec(method)


    for name in interface_methods:
        # only check the interface methods (because trying to get all the instance methods is
        # too slow).
        try:
            cls_method = getattr(class_or_instance, name)
            if not _IsMethod(cls_method, True):
                raise AttributeError

        except AttributeError:
            msg = 'Method %r is missing in class %r (required by interface %r)'
            raise BadImplementationError(msg % (name, classname, interface.__name__))
        else:
            interface_method = interface_methods[name]

            c_args, c_varargs, c_varkw, c_defaults = GetArgSpec(cls_method)

            if c_varargs is not None and c_varkw is not None:
                if not c_args or c_args == ['self'] or c_args == ['cls']:
                    # Accept the implementor if it matches the signature: (*args, **kwargs)
                    # Accept the implementor if it matches the signature: (self, *args, **kwargs)
                    # Accept the implementor if it matches the signature: (cls, *args, **kwargs)
                    continue

            i_args, i_varargs, i_varkw, i_defaults = inspect.getargspec(interface_method)

            # Rules:
            #
            #   1. Variable arguments or keyword arguments: if present
            #      in interface, then it MUST be present in class too
            #
            #   2. Arguments: names must be the same
            #
            #   3. Defaults: for now we assume that default values
            #      must be the same too
            mismatch_varargs = i_varargs is not None and c_varargs is None
            mismatch_varkw = i_varkw is not None and c_varkw is None
            mismatch_args = i_args != c_args
            mismatch_defaults = i_defaults != c_defaults
            if mismatch_varargs or mismatch_varkw or mismatch_args or mismatch_defaults:
                class_sign = inspect.formatargspec(c_args, c_varargs, c_varkw, c_defaults)
                interface_sign = inspect.formatargspec(i_args, i_varargs, i_varkw, i_defaults)
                msg = '\nMethod %s.%s signature:\n  %s\ndiffers from defined in interface %s\n  %s'
                msg = msg % (classname, name, class_sign, interface.__name__, interface_sign)
                raise BadImplementationError(msg)



# #===================================================================================================
# # PROFILING FOR ASSERT IMPLEMENTS -- it can be quite slow, so, this is useful for seeing where exactly
# # it is being slow
# #===================================================================================================
# PROFILE_ASSERT_IMPLEMENTS = False
# if PROFILE_ASSERT_IMPLEMENTS:
#     __original_assert_implements = AssertImplements
#     __cache = {}
#     def AssertImplementsWithCount(class_or_instance, interface_, check_attr=True):
#         try:
#             classname = class_or_instance.__name__
#         except:
#             classname = class_or_instance.__class__.__name__
#
#         cache_key = (classname, interface_)
#         v = __cache.setdefault(cache_key, 0)
#         __cache[cache_key] = v + 1
#
#         __original_assert_implements(class_or_instance, interface_, check_attr)
#
#     AssertImplements = AssertImplementsWithCount
#
#     def PrintAssertImplementsCount():
#         p = []
#         for key, value in __cache.iteritems():
#             p.append((value, key))
#
#         for value, key in sorted(p):
#             print '%s: %s' % (value, key)



#===================================================================================================
# Implements
#===================================================================================================
def Implements(*interfaces, **kwargs):
    '''Make sure a class implements the given interfaces. Must be used in the class scope during class
    creation:
        
        class Foo(object):
            Implements(IFoo)
        
    For old-style classes, use:
        
        class Foo(QWidget): 
            Implements(IFoo, old_style=True)
        
    For not having it checked on its creation -- may happen for performance reasons -- use:
        
        class Foo(object): 
            Implements(IFoo, no_init_check=True)

    '''
    # Just get the previous frame
    frame = sys._getframe().f_back
    try:
        namespace = frame.f_locals
        curr = namespace.get('__implements__', None)
        if curr is not None:
            namespace['__implements__'] = curr + interfaces
        else:
            namespace['__implements__'] = interfaces

        # only put the metaclass on new-style classes (which want to be checked)
        if not kwargs.get('old_style', False) and not kwargs.get('no_init_check', False):
            namespace['__metaclass__'] = InterfaceImplementationMetaClass

        kwargs.pop('old_style', None)
        kwargs.pop('no_init_check', None)
        assert len(kwargs) == 0, \
            'Expected only no_init_check or old_style as kwargs. Found: %s' % (kwargs,)

    finally:
        del frame



#===================================================================================================
# GetClassImplementedInterfaces
#===================================================================================================
@Memoize(10000)  # Really big cache
def _GetClassImplementedInterfaces(class_):
    result = set()

    for c in class_.__mro__:
        result.update(getattr(c, '__implements__', ()))

    # If an element declares that in implements a given interface, then it also implements all
    # superclasses of that interface
    interface_superclasses = set()

    for declared_interface in result:
        interface_superclasses.update(declared_interface.__mro__)

    # Discarding object (it will always be returned in the mro collection)
    interface_superclasses.discard(object)

    # Also discarding the Interface module (that will be returned in the mro but is not a real
    # interface to be implemented
    interface_superclasses.discard(Interface)

    result = result.union(interface_superclasses)
    return frozenset(result)



#===================================================================================================
# GetImplementedInterfaces
#===================================================================================================
def GetImplementedInterfaces(class_or_object):
    '''
       :rtype: frozenset([interfaces]) with the interfaces implemented by the object or class passed.
    '''

    if not hasattr(class_or_object, '__mro__'):
        class_ = class_or_object.__class__
    else:
        class_ = class_or_object

    # we have to build the cache attribute given the name of the class, otherwise setting in a base
    # class before a subclass may give errors.
    return _GetClassImplementedInterfaces(class_)



#===================================================================================================
# IsInterfaceDeclared
#===================================================================================================
def IsInterfaceDeclared(class_or_instance, interface):
    '''
        :type interface: Interface or iterable(Interface)
        :param interface:
            The target interface(s). If multitple interfaces are passed the method will return True
            if the given class or instance implements any of the given interfaces.
            
        :rtype: True if the object declares the interface passed and False otherwise. Note that
        to declare an interface, the class MUST have declared 
        
            >>> interface.Implements(Class) 
    '''
    if class_or_instance is None:
        return False

    is_collection = False
    if isinstance(interface, (set, list, tuple)):
        is_collection = True
        for i in interface:
            if not issubclass(i, Interface):
                raise InterfaceError('To check against an interface, an interface is required (received: %s -- mro:%s)' %
                                     (interface, interface.__mro__))
    elif not issubclass(interface, Interface):
        raise InterfaceError('To check against an interface, an interface is required (received: %s -- mro:%s)' %
                             (interface, interface.__mro__))

    if class_or_instance.__class__ == InterfaceImplementorStub:
        class_or_instance = class_or_instance.GetWrappedFromImplementorStub()

    declared_interfaces = GetImplementedInterfaces(class_or_instance)
    if not is_collection:
        return interface in declared_interfaces
    else:
        return bool(set(interface).intersection(declared_interfaces))



# #===================================================================================================
# # PROFILING FOR IsInterfaceDeclared -- it can be somewhat slow, so, this is useful for seeing
# # where exactly it is being called
# #===================================================================================================
# PROFILE_IS_INTERFACE_DECLARED = False
# if PROFILE_IS_INTERFACE_DECLARED:
#     _count_calls = CountCalls()
#     _original_is_interface_declared = IsInterfaceDeclared
#     _cache_is_interface_declared = {}
#
#     def IsInterfaceDeclaredWithCount(class_or_instance, interface_):
#         try:
#             classname = class_or_instance.__name__
#         except:
#             classname = class_or_instance.__class__.__name__
#
#         cache_key = (classname, interface_)
#         v = _cache_is_interface_declared.setdefault(cache_key, 0)
#         _cache_is_interface_declared[cache_key] = v + 1
#         _count_calls.AddCallerToCount()
#         return _original_is_interface_declared(class_or_instance, interface_)
#
#     IsInterfaceDeclared = IsInterfaceDeclaredWithCount
#
#     def PrintIsInterfaceDeclaredCount():
#         for value, key in sorted((value, key) for key, value in _cache_is_interface_declared.iteritems()):
#             print '%s: %s' % (value, key)
#         _count_calls.PrintStatistics()



#===================================================================================================
# AssertDeclaresInterface
#===================================================================================================
def AssertDeclaresInterface(class_or_instance, interface):
    if not IsInterfaceDeclared(class_or_instance, interface):
        raise AssertionError(
            'The class %s does not implement the interface %s'
            % (class_or_instance, interface)
        )



#===================================================================================================
# Attribute
#===================================================================================================
class Attribute(object):

    _do_not_check_instance = object()

    def __init__(self, attribute_type, instance=_do_not_check_instance):
        '''
        :param type attribute_type:
            Will check the attribute type in the implementation against this type.
            Checks if the attribute is a direct instance of attribute_type, or of it implements it.
            
        :param object instance:
            If passed, will check for *equality* against this instance. The default is to not check
            for equality.
        '''
        self.attribute_type = attribute_type
        self.instance = instance


    def Match(self, attribute):
        '''
        :param object attribute:
            Object that will be compared to see if it matches the expected interface.
            
        :rtype: (bool, str)
        :returns:
            If the given object implements or inherits from the interface expected by this
            attribute, will return (True, None), otherwise will return (False, message), where
            message is an error message of why there was a mismatch (may be None also).
        '''
        msg = None

        if isinstance(attribute, self.attribute_type):
            return (True, None)

        if self.instance is not self._do_not_check_instance:
            if self.instance == attribute:
                return (True, None)
            else:
                return (
                    False,
                    'The instance (%s) does not match the expected one (%s).' % (
                        self.instance, attribute)
                )

        try:
            if IsImplementationFullChecking(attribute, self.attribute_type):
                return (True, msg)
        except InterfaceError, exception_msg:
            # Necessary because whenever a value is compared to an interface it does not inherits
            # from, IsImplementation raises an InterfaceError. In this context, an error like that
            # will mean that our candidate attribute is in fact not matching the interface, so we
            # capture this error and return False.
            msg = exception_msg

        return (False, None)



#===================================================================================================
# ReadOnlyAttribute
#===================================================================================================
class ReadOnlyAttribute(Attribute):
    '''
    This is an attribute that should be treated as read-only (note that usually this means that
    the related property should be also declared as read-only).
    '''


#===================================================================================================
# Method
#===================================================================================================
class Method(object):
    '''
    This class is an 'organization' class, so that subclasses are considered as methods (and its
    __call__ method is checked for the parameters)
    '''


#===================================================================================================
# ScalarAttribute
#===================================================================================================
class ScalarAttribute(Attribute):

    def __init__(self, category):
        '''
        :param str quantity_type:
            String with the category of the Scalar.
        '''
        self.category = category


    @Override(Attribute.Match)
    def Match(self, attribute):
        if not IsInstance(attribute, 'Scalar'):
            return (False, 'The attribute is not a Scalar instance.')
        elif attribute.GetCategory() != self.category:
            return (
                False,
                'The Scalar category (%s) does not match the expected category of the'
                ' interface (%s).' % (attribute.GetCategory(), self.category)
            )

        return (True, None)



#=======================================================================================================================
#=======================================================================================================================
# CACHED METHOD
#=======================================================================================================================
#=======================================================================================================================



#=======================================================================================================================
# AbstractCachedMethod
#=======================================================================================================================
class AbstractCachedMethod(Method):
    '''
    Base class for cache-manager.
    The abstract class does not implement the storage of results.
    '''

    def __init__(self, cached_method=None):
        # REMARKS: Use WeakMethodRef to avoid cyclic reference.
        self._method = WeakMethodRef(cached_method)
        self.enabled = True
        self.ResetCounters()


    def __call__(self, *args, **kwargs):
        key = self.GetCacheKey(*args, **kwargs)
        result = None

        if self.enabled and self._HasResult(key):
            self.hit_count += 1
            result = self._GetCacheResult(key, result)
        else:
            self.miss_count += 1
            result = self._CallMethod(*args, **kwargs)
            self._AddCacheResult(key, result)

        self.call_count += 1
        return result


    def _CallMethod(self, *args, **kwargs):
        return self._method()(*args, **kwargs)


    def GetCacheKey(self, *args, **kwargs):
        '''
            Use the arguments to build the cache-key.
        '''
        if args:
            if kwargs:
                return immutable.AsImmutable(args), immutable.AsImmutable(kwargs)

            return immutable.AsImmutable(args)

        if kwargs:
            return immutable.AsImmutable(kwargs)


    def _HasResult(self, key):
        raise NotImplementedError()


    def _AddCacheResult(self, key, result):
        raise NotImplementedError()


    def DoClear(self):
        raise NotImplementedError()


    def Clear(self):
        self.DoClear()
        self.ResetCounters()


    def ResetCounters(self):
        self.call_count = 0
        self.hit_count = 0
        self.miss_count = 0


    def _GetCacheResult(self, key, result):
        raise NotImplementedError()



#===================================================================================================
# CachedMethod
#===================================================================================================
class CachedMethod(AbstractCachedMethod):
    '''
    Stores ALL the different results and never delete them.
    '''

    def __init__(self, cached_method=None):
        super(CachedMethod, self).__init__(cached_method)
        self._results = {}


    def _HasResult(self, key):
        return key in self._results


    def _AddCacheResult(self, key, result):
        self._results[key] = result


    def DoClear(self):
        self._results.clear()


    def _GetCacheResult(self, key, result):
        return self._results[key]



#===================================================================================================
# ImmutableParamsCachedMethod
#===================================================================================================
class ImmutableParamsCachedMethod(CachedMethod):
    '''
    Expects all parameters to already be immutable
    Considers only the positional parameters of key, ignoring the keyword arguments 
    '''

    def GetCacheKey(self, *args, **kwargs):
        '''
        Use the arguments to build the cache-key.
        '''
        return args



#===================================================================================================
# LastResultCachedMethod
#===================================================================================================
class LastResultCachedMethod(AbstractCachedMethod):
    '''
        A cache that stores only the last result.
    '''

    def __init__(self, cached_method=None):
        super(LastResultCachedMethod, self).__init__(cached_method)
        self._key = None
        self._result = None


    def _HasResult(self, key):
        return self._key == key


    def _AddCacheResult(self, key, result):
        self._key = key
        self._result = result


    def DoClear(self):
        self._key = None
        self._result = None


    def _GetCacheResult(self, key, result):
        return self._result



#===================================================================================================
# AttributeBasedCachedMethod
#===================================================================================================
class AttributeBasedCachedMethod(CachedMethod):
    '''
    This cached method consider changes in object attributes
    '''


    def __init__(self, cached_method, attr_name_list, cache_size=1, results=None):
        '''
        :type cached_method: bound method to be cached
        :param cached_method:
        :type attr_name_list: attr names in a C{str} separated by spaces OR in a sequence of C{str}
        :param attr_name_list:
        :type cache_size: the cache size
        :param cache_size:
        :type results: an optional ref. to an C{odict} for keep cache results
        :param results:
        '''
        CachedMethod.__init__(self, cached_method)
        if isinstance(attr_name_list, str):
            self._attr_name_list = attr_name_list.split()
        else:
            self._attr_name_list = attr_name_list
        self._cache_size = cache_size
        if results is None:
            self._results = odict()
        else:
            self._results = results


    def GetCacheKey(self, *args, **kwargs):
        object = self._method().im_self
        for attr_name in self._attr_name_list:
            kwargs['_object_%s' % attr_name] = getattr(object, attr_name)
        return AbstractCachedMethod.GetCacheKey(self, *args, **kwargs)


    def _AddCacheResult(self, key, result):
        CachedMethod._AddCacheResult(self, key, result)
        if len(self._results) > self._cache_size:
            key0 = self._results.keys()[0]
            del self._results[key0]
