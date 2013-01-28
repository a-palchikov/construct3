
from __future__ import print_function
import itertools
import operator

_counter = itertools.count()

def _special_name(name):
    return (name[:2] == "__" and name[-2:] == "__")


class Container(dict):
    __slots__ = ["__order__"]
    def __init__(self, iterable = (), **kwargs):
        dict.__setattr__(self, "__order__", {})
        self.update(iterable, **kwargs)
    def __setitem__(self, key, val):
        dict.__setitem__(self, key, val)
        if key not in self.__order__:
            self.__order__[key] = next(_counter)
    def __delitem__(self, key):
        dict.__delitem__(self, key)
        del self.__order__[key]
    def update(self, iterable, **kwargs):
        for k, v in iterable:
            self[k] = v
        for k, v in kwargs.items():
            self[k] = v
    def pop(self, key, *default):
        dict.pop(self, key, *default)
        self.__order__.pop(key, None)
    #__getattr__ = dict.__getitem__
    # ap: if implemented as __getitem__, hasattr will fail on non-existing
    # attribute as it expects an AttributeError to be raised in this case
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)
    __setattr__ = __setitem__
    __delattr__ = __delitem__
    def __iter__(self):
        items = self.__order__.items()
        #items.sort(key = lambda item: item[1])
        #return (k for k, _ in items)
        return (k for k, _ in sorted(items, key=operator.itemgetter(1)))
    def keys(self):
        return list(iter(self))
    def values(self):
        return [self[k] for k in self]
    def items(self):
        for k in self:
            yield k, self[k]
    iterkeys = keys
    itervalues = values
    iteritems = items
    def __repr__(self):
        if not self:
            return "%s()" % (self.__class__.__name__,)
        attrs = "\n  ".join("%s = %s" % (k, "\n  ".join(repr(v).splitlines()))
            for k, v in self.items())
        return "%s:\n  %s" % (self.__class__.__name__, attrs)

class ChainedContainer(Container):
    def __getitem__(self, name):
        if not _special_name(name) and name not in self \
                and "_" in self:
            # perform hierarchical attribute lookup
            return self._lookup_in_chain(name)
        return super(ChainedContainer, self).__getitem__(name)

    def _lookup_in_chain(self, name):
        assert "_" in self
        ctx = self.get("_", None)
        while ctx:
            if name in ctx:
                return ctx[name]
            ctx = ctx.get("_", None)
        raise AttributeError(name)


if __name__ == "__main__":
    c = Container(aa = 6, b = 7, c = Container(d = 8, e = 9, f = 10))
    del c.aa
    c.aa = 0
    c.xx = Container()
    print([c, c, c])

    for a in c:
        print(a)

    c = ChainedContainer(a=10, _=ChainedContainer(b=10, foo=Container(bar="baz")))
    print(c.a, c.b, c.foo, c["foo"])

    if hasattr(c, "foo"):
        print("c.foo")


