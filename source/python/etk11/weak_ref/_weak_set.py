from etk11.weak_ref import GetWeakRef


#===================================================================================================
# WeakSet
#===================================================================================================
class WeakSet(object):
    '''
    The weak set is a set that will only keep weak-references to objects passed to it.
    
    When iterating the actual objects are used, but internally, only weakrefs are kept.
    
    It does not contain the whole set interface (but can be extended as needed).
    '''

    def __init__(self, initlist=None):
        self.data = set()


    def add(self, item):
        self.data.add(GetWeakRef(item))


    def clear(self):
        self.data.clear()


    def __iter__(self):
        # iterate in a copy
        for ref in self.data.copy():
            d = ref()
            if d is None:
                self.data.remove(ref)
            else:
                yield d


    def remove(self, item):
        '''
        Remove an item from the available data.
        
        :param object item:
            The object to be removed.
        '''
        self.data.remove(GetWeakRef(item))


    def discard(self, item):
        try:
            self.remove(item)
        except KeyError:
            pass

    def __len__(self):
        i = 0
        for _k in self:  # we make an iteration to remove dead references...
            i += 1
        return i


    def __str__(self):
        return '\n'.join(str(x) for x in self)

