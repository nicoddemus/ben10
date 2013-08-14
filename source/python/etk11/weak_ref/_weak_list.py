from etk11.weak_ref import GetWeakRef
from etk11.decorators import Implements



#===================================================================================================
# WeakList
#===================================================================================================
class WeakList(object):
    '''
    The weak list is a list that will only keep weak-references to objects passed to it.
    
    When iterating the actual objects are used, but internally, only weakrefs are kept.
    
    It does not contain the whole list interface (but can be extended as needed).
    '''

    def __init__(self, initlist=None):
        self.data = []

        if initlist is not None:
            for x in initlist:
                self.append(x)


    @Implements(list.append)
    def append(self, item):
        self.data.append(GetWeakRef(item))


    @Implements(list.extend)
    def extend(self, lst):
        for o in lst:
            self.append(o)


    def __iter__(self):
        # iterate in a copy
        for ref in self.data[:]:
            d = ref()
            if d is None:
                self.data.remove(ref)
            else:
                yield d


    def remove(self, item):
        '''
        Remove first occurrence of a value.
        
        It differs from the normal version because it will not raise an exception if the
        item is not found (because it may be garbage-collected already).
        
        :param object item:
            The object to be removed.
        '''
        # iterate in a copy
        for ref in self.data[:]:
            d = ref()

            if d is None:
                self.data.remove(ref)

            elif d == item:
                self.data.remove(ref)
                break

    def __len__(self):
        i = 0
        for _k in self:  # we make an iteration to remove dead references...
            i += 1
        return i

    def __delitem__(self, i):
        del self.data[i]

    def __getitem__(self, i):
        return self.data[i]()

    def __getslice__(self, i, j):
        '''
        :rtype: WeakList
        :returns:
            A new WeakList with the given slice (note that the actual size may not be what the user
            initially requested, as object may be garbage collected during that process).
        '''
        i = max(i, 0)
        j = max(j, 0)

        slice = []

        for ref in self.data[i:j]:
            d = ref()
            if d is not None:
                slice.append(d)

        return WeakList(slice)

    def __delslice__(self, i, j):
        i = max(i, 0)
        j = max(j, 0)

        del self.data[i:j]


    def __setitem__(self, i, item):
        '''
        Set a weakref of item on the ith position
        '''
        self.data[i] = GetWeakRef(item)

    def __str__(self):
        return '\n'.join(str(x) for x in self)

