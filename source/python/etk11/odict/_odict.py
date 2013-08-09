from UserDict import DictMixin



#===================================================================================================
# PythonOrderedDict
#===================================================================================================
class PythonOrderedDict(DictMixin):
    '''
    Python implementation of a ordered dict.
    This class replaces the odict from the shared-resource "ordered_dict" when the shared-resource
    is not available.
    
    :ivar dict _data:
        Keeps a dictionary with all the values stored by the instance
        
    :ivar list _keys:
        A list with all the keps added in the ordered-dict in the same order they were added.
    '''

    def __init__(self, init=None):
        '''
        Mimics dict interface
        
        :type init: list of 2-tuple
        :param init:
            Initial values for the ordered dict.
        '''
        self._keys = []
        self._data = {}
        if init:
            for key, value in init:
                self[key] = value


    def __setitem__(self, key, value):
        '''
        Mimics dict interface
        Adds the item on both _data and _keys.
        '''
        if key not in self._data:
            self._keys.append(key)
        self._data[key] = value
        assert len(self._data) == len(self._keys)


    def __getitem__(self, key):
        '''
        Mimics dict interface
        '''
        return self._data[key]


    def __delitem__(self, key):
        '''
        Mimics dict interface
        '''
        del self._data[key]
        self._keys.remove(key)


    def keys(self):
        '''
        Mimics dict interface
        '''
        return list(self._keys)


    def copy(self):
        '''
        Mimics dict interface
        '''
        copyDict = PythonOrderedDict()
        copyDict._data = self._data.copy()
        copyDict._keys = self._keys[:]
        return copyDict


    def popitem(self, index):
        '''
        Removes the item from the given index.
        
        :param int index:
            The index of the item to remove.
        '''
        key = self._keys[index]
        del self._keys[index]
        del self._data[key]


    def insert(self, index, key, value):
        '''
        Inserts a given value ordering it at the given index.
        
        :param int index:
            The index in which it should be inserted.
            
        :param object key:
            The key of the value.
            
        :param object value:
            The value to be inserted.
        '''
        if key in self._data:
            self._keys.remove(key)

        self._keys.insert(index, key)
        self._data[key] = value


    def reverse(self):
        '''
        Reverse the order of the dict
        '''
        self._keys.reverse()
