'''
    Interfaces module.

    A Interface describes a behaviour that some objects must implement.

    To declare a interface, just subclass from Interface::

        class IFoo(interface.Interface):
            ...

    To create a class that implements that interface, use interface.Implements:

        class Foo(object):
            interface.Implements(IFoo)

    If Foo doesn't implement some method from IFoo, an exception is raised at class creation time.
'''
from _adaptable_interface import IAdaptable
from _cached_method import AttributeBasedCachedMethod, CachedMethod, LastResultCachedMethod
from _interface import (AssertDeclaresInterface, AssertImplements, AssertImplementsFullChecking,
    Attribute, BadImplementationError, CacheInterfaceAttrs, DeclareClassImplements,
    GetImplementedInterfaces, ImplementsInterface, Interface, InterfaceError,
    InterfaceImplementationMetaClass, InterfaceImplementorStub, IsImplementation,
    IsImplementationOfAny, ReadOnlyAttribute, ScalarAttribute)

__all__ = [
    'AssertDeclaresInterface',
    'AssertImplements',
    'AssertImplementsFullChecking',
    'Attribute',
    'BadImplementationError',
    'CacheInterfaceAttrs',
    'GetImplementedInterfaces',
    'IAdaptable',
    'Interface',
    'InterfaceError',
    'InterfaceImplementationMetaClass',
    'InterfaceImplementorStub',
    'IsImplementation',
    'ReadOnlyAttribute',
    'ScalarAttribute',
    # _cached_method
    'CachedMethod',
    'LastResultCachedMethod',
    'AttributeBasedCachedMethod',
]
