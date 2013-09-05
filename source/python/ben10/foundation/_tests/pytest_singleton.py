from ben10.foundation.callback import After
from ben10.foundation.decorators import Override
from ben10.foundation.singleton import PushPopSingletonError, Singleton, SingletonAlreadySetError, SingletonNotSetError
import pytest



#=======================================================================================================================
# Test
#=======================================================================================================================
class Test:

    def _TestCurrentSingleton(self, singleton_class, value):
        singleton = singleton_class.GetSingleton()
        assert singleton.value == value


    def testSingleton(self):

        class MySingleton(Singleton):

            def __init__(self, value):
                self.value = value

            @classmethod
            @Override(Singleton.CreateDefaultSingleton)
            def CreateDefaultSingleton(cls):
                return MySingleton(value=0)

        # Default singleton (created automatically and also put in the stack)
        self._TestCurrentSingleton(MySingleton, 0)
        default_singleton = MySingleton.GetSingleton()
        default_singleton.value = 10

        # SetSingleton must be called only when there is no singleton set. In this case,
        # GetSingleton already set the singleton.
        with pytest.raises(SingletonAlreadySetError):
            MySingleton.SetSingleton(MySingleton(value=999))
        self._TestCurrentSingleton(MySingleton, 10)

        # push a new instance and test it
        MySingleton.PushSingleton(MySingleton(2000))
        self._TestCurrentSingleton(MySingleton, 2000)

        # Calling SetSingleton after using Push/Pop is an error: we do this so that
        # in tests we know someone is doing a SetSingleton when they shouldn't
        with pytest.raises(PushPopSingletonError):
            MySingleton.SetSingleton(MySingleton(value=10))

        # pop, returns to the initial
        MySingleton.PopSingleton()
        self._TestCurrentSingleton(MySingleton, 10)

        # SetSingleton given SingletonAlreadySet when outside Push/Pop
        with pytest.raises(SingletonAlreadySetError):
            MySingleton.SetSingleton(MySingleton(value=999))
        self._TestCurrentSingleton(MySingleton, 10)

        # The singleton set with "SetSingleton" or created automatically by "GetSingleton" is not
        # part of the stack
        with pytest.raises(IndexError):
            MySingleton.PopSingleton()


    def testSetSingleton(self):

        class MySingleton(Singleton):

            def __init__(self, value):
                self.value = value

        assert not MySingleton.HasSingleton()

        MySingleton.SetSingleton(MySingleton(value=999))
        assert MySingleton.HasSingleton()
        self._TestCurrentSingleton(MySingleton, 999)

        with pytest.raises(SingletonAlreadySetError):
            MySingleton.SetSingleton(MySingleton(value=999))

        MySingleton.ClearSingleton()
        assert not MySingleton.HasSingleton()

        with pytest.raises(SingletonNotSetError):
            MySingleton.ClearSingleton()


    def testSingletonOptimization(self):
        class MySingleton(Singleton):
            pass

        def _ObtainStack(*args, **kwargs):
            self._called = True

        After(MySingleton._ObtainStack, _ObtainStack)

        self._called = False
        MySingleton.GetSingleton()
        assert self._called

        self._called = False
        MySingleton.GetSingleton()
        assert not self._called
