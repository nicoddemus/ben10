try:
    import _ordereddict
    odict = _ordereddict.ordereddict
except ImportError:
    # Fallback to python's implementation
    # We don't have our _orderedict available on pypi so we must fallback on travis-ci tests.
    import collections
    odict = collections.OrderedDict
