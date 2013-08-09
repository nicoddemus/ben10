from _weak_method import WeakMethodProxy
from _weak_method import WeakMethodRef
from types import LambdaType
import inspect
import weakref



#===================================================================================================
# IsWeakProxy
#===================================================================================================
def IsWeakProxy(obj):
    '''
        Returns whether the given object is a weak-proxy
    '''
    return isinstance(obj, (weakref.ProxyType, WeakMethodProxy))


#===================================================================================================
# IsWeakRef
#===================================================================================================
def IsWeakRef(obj):
    '''
        Returns wheter ths given object is a weak-reference.
    '''
    return isinstance(obj, (weakref.ReferenceType, WeakMethodRef)) and not isinstance(obj, WeakMethodProxy)


#===================================================================================================
# IsWeakObj
#===================================================================================================
def IsWeakObj(obj):
    '''
        Returns whether the given object is a weak object. Either a weak-proxy or a weak-reference.

        :param  obj:
            The object that may be a weak reference or proxy
        @return
            True if it is a proxy or a weak reference.
    '''
    return IsWeakProxy(obj) or IsWeakRef(obj)


#===================================================================================================
# GetRealObj
#===================================================================================================
def GetRealObj(obj):
    '''
        Returns the real-object from a weakref, or the object itself otherwise.
    '''
    if IsWeakRef(obj):
        return obj()
    if isinstance(obj, LambdaType):
        return obj()
    return obj



#===================================================================================================
# GetWeakProxy
#===================================================================================================
def GetWeakProxy(obj):
    '''
    :type obj: this is the object we want to get as a proxy
    :param obj:
    @return the object as a proxy (if it is still not already a proxy or a weak ref, in which case the passed 
                                   object is returned itself)
    '''
    if obj is None:
        return None

    if not IsWeakProxy(obj):

        if IsWeakRef(obj):
            obj = obj()

        #for methods we cannot create regular weak-refs
        if inspect.ismethod(obj):
            return WeakMethodProxy(obj)

        return weakref.proxy(obj)


    return obj

#Keep the same lambda for weak-refs (to be reused among all places that use GetWeakRef(None)
_EMPTY_LAMBDA = lambda:None

#===================================================================================================
# GetWeakRef
#===================================================================================================
def GetWeakRef(obj):
    '''
    :type obj: this is the object we want to get as a weak ref
    :param obj:
    @return the object as a proxy (if it is still not already a proxy or a weak ref, in which case the passed 
                                   object is returned itself)
    '''
    if obj is None:
        return _EMPTY_LAMBDA

    if IsWeakProxy(obj):
        raise RuntimeError('Unable to get weak ref for proxy.')

    if not IsWeakRef(obj):

        #for methods we cannot create regular weak-refs
        if inspect.ismethod(obj):
            return WeakMethodRef(obj)

        return weakref.ref(obj)
    return obj


#===================================================================================================
# IsSame
#===================================================================================================
def IsSame(o1, o2):
    '''
        This checks for the identity even if one of the parameters is a weak reference
    
        :param  o1:
            first object to compare

        :param  o2:
            second object to compare

        @raise
            RuntimeError if both of the passed parameters are weak references
    '''
    #get rid of weak refs (we only need special treatment for proxys)
    if IsWeakRef(o1):
        o1 = o1()
    if IsWeakRef(o2):
        o2 = o2()

    #simple case (no weak objects)
    if not IsWeakObj(o1) and not IsWeakObj(o2):
        return o1 is o2

    #all weak proxys
    if IsWeakProxy(o1) and IsWeakProxy(o2):
        if not o1 == o2:
            #if they are not equal, we know they're not the same
            return False

        #but we cannot say anything if they are the same if they are equal
        raise ReferenceError('Cannot check if object is same if both arguments passed are weak objects')

    #one is weak and the other is not
    if IsWeakObj(o1):
        weak = o1
        original = o2
    else:
        weak = o2
        original = o1

    weaks = weakref.getweakrefs(original)
    for w in weaks:
        if w is weak: #check the weak object identity
            return True

    return False
