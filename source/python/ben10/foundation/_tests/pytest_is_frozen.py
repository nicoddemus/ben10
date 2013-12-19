from ben10.foundation.is_frozen import IsDevelopment, IsFrozen, SetIsDevelopment, SetIsFrozen



#===================================================================================================
# Test
#===================================================================================================
class Test:

    def testIsFrozen(self):
        is_frozen = IsFrozen()
        try:
            assert not IsFrozen() == IsDevelopment()

            SetIsDevelopment(True)
            assert IsFrozen() == False
            assert not IsFrozen() == IsDevelopment()

            SetIsDevelopment(False)
            assert IsFrozen() == True
            assert not IsFrozen() == IsDevelopment()

            SetIsFrozen(False)
            assert IsFrozen() == False
            assert not IsFrozen() == IsDevelopment()

            SetIsFrozen(True)
            assert IsFrozen() == True
            assert not IsFrozen() == IsDevelopment()
        finally:
            SetIsFrozen(is_frozen)


