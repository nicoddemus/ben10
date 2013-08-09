


#=======================================================================================================================
# Test
#=======================================================================================================================
class Test(object):

    def test_Equals(self):
        from etk11.odict import odict
        x = odict([(1, 1)])
        y = {1:1}
        assert x == y


    def _Testodict(self, DictClass):
        test_dict = DictClass()
        for x in range(200):
            test_dict[str(x)] = x

        assert test_dict.values() == range(200)

        itemsIteration = []
        for _key, value in test_dict.iteritems():
            itemsIteration.append(value)
        valuesIteration = []
        for value in test_dict.itervalues():
            valuesIteration.append(value)

        assert itemsIteration == range(200)
        assert valuesIteration == range(200)


        otherDict = DictClass()
        for x in range(201, 300):
            otherDict[str(x)] = x

        test_dict.update(otherDict)
        assert test_dict.get('250', None) == 250

        copyDict = test_dict.copy()
        copyDict['250'] = 0
        assert test_dict.get('250', None) == 250

        test_dict.clear()
        assert len(test_dict) == 0

        o = DictClass()
        o[0] = 0
        o[2] = 2
        o.insert(1, 1, 1)
        assert o == DictClass([(0, 0), (1, 1), (2, 2)])

        # Change the order if it was already there
        o.insert(1, 0, 0)
        assert o == DictClass([(1, 1), (0, 0), (2, 2)])


    def testodict(self):
        from etk11.odict import odict
        self._Testodict(odict)

        from etk11.odict import odict as our_odict
        assert our_odict is odict


    def testPythonImplementation(self):
        from etk11.odict import PythonOrderedDict
        self._Testodict(PythonOrderedDict)


    def testDeepcopy(self):
        from etk11.odict import odict
        m = odict([(1, 1)])

        import sys
        import gc

        import copy
        for i in xrange(100):
            gc.collect()
            if i < 25:
                prev = sys.getrefcount(None)
            else:
                curr = sys.getrefcount(None)
                if curr < prev:
                    self.fail(
                        'The ref count cannot get lower for None (previous:%s current:%s).' %
                        (prev, curr)
                    )

            # Notice that print sys.getrefcount(None) is always decrementing (this is the error)
            m = copy.deepcopy(m)


    def testReverse(self):
        from etk11.odict import odict
        m = odict([(1, 'a'), (3, 'c'), (2, 'b')])

        assert [1, 3, 2] == m.keys()
        m.reverse()
        assert [2, 3, 1] == m.keys()


    def testOrderedDictOrigin(self):
        '''
        Tests which implementation of OrderedDict we are using. In all situations we should be using
        the binary implementation, not the python one.
        '''
        from etk11.odict import odict
        assert odict.__name__ != 'PythonOrderedDict'
