from etk11.debug import IsPythonDebug


#=======================================================================================================================
# Test
#=======================================================================================================================
class Test():

    def testIsPythonDebug(self):
        assert IsPythonDebug() in (True, False)