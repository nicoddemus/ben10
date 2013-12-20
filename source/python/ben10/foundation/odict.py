import collections



#===================================================================================================
# _OrderedDict
#===================================================================================================
class _OrderedDict(collections.OrderedDict):

    def insert(self, index, key, value, dict_setitem=dict.__setitem__):
        '''
        Inserts an key/value at the given index.
        '''
        if key not in self:
            assert isinstance(index, int)
            index = max(0, min(len(self._OrderedDict__map), index))

            curr = self._OrderedDict__root
            while index > 0:
                curr = curr[1]  # Next
                index -= 1

            next_ = curr[1]
            curr[1] = next_[0] = self._OrderedDict__map[key] = [curr, next_, key]

        return dict_setitem(self, key, value)



def _GetSymbol():
    try:
        import _ordereddict
        return _ordereddict.ordereddict
    except ImportError:
        # Fallback to python's implementation
        # We don't have our _orderedict available on pypi so we must fallback on travis-ci tests.
        return _OrderedDict

odict = _GetSymbol()
