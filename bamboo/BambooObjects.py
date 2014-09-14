
import pandas as pd
import pandas
from pandas.core.groupby import GroupBy

from inspect import getmembers, isfunction, ismethod

import bamboo, groups, frames, plotting


_bamboo_methods = {name:func  for name, func in getmembers(bamboo) if isfunction(func)}
_frames_methods = {name:func  for name, func in getmembers(frames) if isfunction(func)}
_groups_methods = {name:func  for name, func in getmembers(groups) if isfunction(func)}
_plot_methods = {name:func  for name, func in getmembers(plotting) if isfunction(func)}


def _wrap_with_bamboo(obj):

    if isinstance(obj, pandas.DataFrame):
        return BambooDataFrame(obj)

    elif isinstance(obj, pandas.core.groupby.SeriesGroupBy):
        return BambooSeriesGroupBy(obj)

    elif isinstance(obj, pandas.core.groupby.DataFrameGroupBy):
        return BambooDataFrameGroupBy(obj)

    else:
        return obj


def _create_bamboo_wrapper(obj, func):
    def callable(*args, **kwargs):
        print "Calling with %s args and %s kwargs" % (len(args), len(kwargs))
        res = func(obj, *args, **kwargs)
        ret =  _wrap_with_bamboo(res)
        return ret
    return callable


def _wrap_instance_method(method):
    def wrapped_method(*args, **kwargs):
        res = method.__call__(*args, **kwargs)
        ret =  _wrap_with_bamboo(res)
        return ret
    return wrapped_method


class BambooDataFrame(pandas.DataFrame):

    def __init__(self, *args, **kwargs):
        super(BambooDataFrame, self).__init__(*args, **kwargs)

    def groupby(self, *args, **kwargs):
        return _wrap_with_bamboo(super(BambooDataFrame, self).groupby(*args, **kwargs))

    def __getattribute__(self, *args, **kwargs):
        #print "getattribute: %s" % args
        val = super(BambooDataFrame, self).__getattribute__(*args, **kwargs)
        #print "Got val for arg %s: %s" % (args, type(val))
        ret = _wrap_with_bamboo(val)
        #print "Wrapped for arg %s: %s" % (args, type(ret))
        return ret



    def __getattr__(self, *args, **kwargs):

        name, pargs = args[0], args[1:]

        if name in _bamboo_methods:
            return _create_bamboo_wrapper(self, _bamboo_methods[name])

        if name in _plot_methods:
            return _create_bamboo_wrapper(self, _plot_methods[name])

        if name in _frames_methods:
            return _create_bamboo_wrapper(self, _frames_methods[name])

        res = super(BambooDataFrame, self).__getattr__(*args, **kwargs)
        return _wrap_with_bamboo(res)
        #return _create_bamboo_wrapper(self, super(BambooDataFrame, self).__getattribute__(*args, **kwargs))


class BambooDataFrameGroupBy(pandas.core.groupby.DataFrameGroupBy):

    def __init__(self, other):
        if not isinstance(other, pandas.core.groupby.DataFrameGroupBy):
            raise TypeError()

        super(BambooDataFrameGroupBy, self).__init__(
                                             other.obj,
                                             other.keys,
                                             other.axis,
                                             other.level,
                                             other.grouper,
                                             other.exclusions,
                                             other._selection,
                                             other.as_index,
                                             other.sort,
                                             other.group_keys,
                                             other.squeeze)


    def head(self, *args, **kwargs):
        return bamboo.head(self, *args, **kwargs)


    def __getattribute__(self, *args, **kwargs):

        if args[0]=='mean':
            print "MEAN"

        #print "getattribute: %s" % args
        val = super(BambooDataFrameGroupBy, self).__getattribute__(*args, **kwargs)

        print "Type: %s" % type(val)

        if ismethod(val):
        #if type(val)=='instancemethod':
            print "Returning instancemethod"
            #return _create_bamboo_wrapper(self, val)
            return _wrap_instance_method(val)
        else:
            return val

        if args[0]=='mean':
            print "Got val for arg %s: %s" % (args, type(val))
            print "of type: %s" % type(val.__call__())

        print type(val)
        #ret = _create_bamboo_wrapper(self, val)
        ret = _wrap_with_bamboo(val)
        #if args[0]=='mean':
        #    print "Wrapped for arg %s: %s" % (args, type(ret))
        #    print "to type: %s" % type(ret.__call__())
        return ret


    def __getattr__(self, *args, **kwargs):

        print "getattr: %s" % args

        name, pargs = args[0], args[1:]

        if name in _bamboo_methods:
            return _create_bamboo_wrapper(self, _bamboo_methods[name])

        if name in _plot_methods:
            return _create_bamboo_wrapper(self, _plot_methods[name])

        if name in _groups_methods:
            print "Using groups methods for: %s" % name
            return _create_bamboo_wrapper(self, _groups_methods[name])
            return ret_val

        res = super(BambooDataFrameGroupBy, self).__getattr__(*args, **kwargs)
        return _wrap_with_bamboo(res)
        #return _create_bamboo_wrapper(self, res)


class BambooSeriesGroupBy(pandas.core.groupby.SeriesGroupBy):

    def __init__(self, other):
        if not isinstance(other, pandas.core.groupby.SeriesGroupBy):
            raise TypeError()
        super(BambooSeriesGroupBy, self).__init__(
                                             other.obj,
                                             other.keys,
                                             other.axis,
                                             other.level,
                                             other.grouper,
                                             other.exclusions,
                                             other._selection,
                                             other.as_index,
                                             other.sort,
                                             other.group_keys,
                                             other.squeeze)

    def head(self, *args, **kwargs):
        return bamboo.head(self, *args, **kwargs)

    def __getattr__(self, *args, **kwargs):

        name, pargs = args[0], args[1:]

        if name in _bamboo_methods:
            return _create_bamboo_wrapper(self, _bamboo_methods[name])

        if name in _plot_methods:
            return _create_bamboo_wrapper(self, _plot_methods[name])

        if name in _groups_methods:
            return _create_bamboo_wrapper(self, _groups_methods[name])

        res = super(BambooSeriesGroupBy, self).__getattr__(*args, **kwargs)
        return _wrap_with_bamboo(res)
        #return _create_bamboo_wrapper(self, super(BambooSeriesGroupBy, self).__getattribute__(*args, **kwargs))

