from coilib50 import unittest
from coilib50.cache.memoize import Memoize
from coilib50.debug.profiling import ProfileMethod, PrintProfileMultiple


#===================================================================================================
# Test
#===================================================================================================
class Test(unittest.TestCase):


    def profileMemoize(self):
        @Memoize(maxsize=1, prune_method=Memoize.LRU)
        def Call():
            return 1

        @ProfileMethod('test.prof')
        def Check():

            for _i in xrange(100000):
                Call()

        Check()
        PrintProfileMultiple('test.prof')


#===================================================================================================
# main
#===================================================================================================
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.profileMemoize']
    unittest.main()
