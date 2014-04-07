from ben10.foundation.namedtuple import namedtuple



#===================================================================================================
# Test
#===================================================================================================
class Test:

    def testNamedTupleAsTuple(self):
        MyTuple = namedtuple('MyTuple', 'alpha, beta, gamma')

        result = MyTuple(105, 4.5, 'not delta')

        assert result[0] == 105
        assert result[1] == 4.5
        assert result[2] == 'not delta'

        assert list(result) == [105, 4.5, 'not delta']

        assert result.gamma == 'not delta'
        assert result.beta == 4.5
        assert result.alpha == 105


    def testNamedTuplePickling(self):
        '''
        NOTE: Adapted from test code from: http://code.activestate.com/recipes/500261/ (r15)
        NOTE: The namedtuple cannot be created locally for this to work (must be at module scope)
        '''
        # verify that instances can be pickled
        from ben10.foundation.namedtuple import _test_namedtuple_Point
        from cPickle import dumps, loads

        p = _test_namedtuple_Point(x=10, y=20)
        assert p == loads(dumps(p, -1))


    def testNamedTupleOverride(self):
        '''
        NOTE: Adapted from test code from: http://code.activestate.com/recipes/500261/ (r15)
        '''
        # test and demonstrate ability to override methods
        class Point(namedtuple('Point', 'x y')):
            @property
            def hypot(self):
                return (self.x ** 2 + self.y ** 2) ** 0.5
            def __str__(self):
                return 'Point: x=%6.3f y=%6.3f hypot=%6.3f' % (self.x, self.y, self.hypot)

        assert str(Point(3, 4)) == 'Point: x= 3.000 y= 4.000 hypot= 5.000'
        assert str(Point(14, 5)) == 'Point: x=14.000 y= 5.000 hypot=14.866'
        assert str(Point(9. / 7, 6)) == 'Point: x= 1.286 y= 6.000 hypot= 6.136'


    def testNamedTupleReplace(self):
        '''
        NOTE: Adapted from test code from: http://code.activestate.com/recipes/500261/ (r15)
        '''
        class Point(namedtuple('Point', 'x y')):
            'Point class with optimized _make() and _replace() without error-checking'
            _make = classmethod(tuple.__new__)
            def _replace(self, _map=map, **kwds):
                return self._make(_map(kwds.get, ('x', 'y'), self))

        assert Point(11, 22)._replace(x=100) == Point(x=100, y=22)
