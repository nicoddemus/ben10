def _GetSymbol():
    try:
        import _ordereddict
        return _ordereddict.ordereddict
    except ImportError:
        # Fallback to python's implementation
        # We don't have our _orderedict available on pypi so we must fallback on travis-ci tests.
        import collections
        return collections.OrderedDict

odict = _GetSymbol()
