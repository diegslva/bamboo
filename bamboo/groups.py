
from collections import OrderedDict

import pandas as pd

from bamboo import plotting
from helpers import combine_data_frames


from types import *
import inspect


import matplotlib.pyplot as plt
from math import floor, ceil


"""

Functions that act on data frame group by objects

"""


def filter_groups(dfgb, filter_function, on_index=False):
    """
    Filter the groups of a DataFrameGroupBy
    and return a DataFrameGroupBy containing
    only the groups that return true.
    In pseudocode:
    return [group for group in dfgb.groups
            if filter_function(group)]
    If on_index is true, the filter function is applied
    to the group value (the index)
    """

    return_groups = []

    for val, group in dfgb:
        if on_index and filter_function(val):
            return_groups.append(group)
        if not on_index and filter_function(group):
            return_groups.append(group)

    return combine_data_frames(return_groups).groupby(dfgb.keys)


def sorted_groups(dfgb, key):
    """
    Return a sorted version of the
    grouped dataframe.  The required
    key function is a function of each
    group and determins the sort order
    """

    sort_list = []

    for name, group in dfgb:

        sort_val = key(group)
        sort_list.append((sort_val, group))

    sorted_groups = [group for val, group
                     in sorted(sort_list, key=lambda x: x[0])]

    return combine_data_frames(sorted_groups).groupby(dfgb.keys, sort=False)


def map_groups(dfgb, func, name=None):
    """
    Take a DataFrameGroupBy and apply a function
    to the DataFrames, returning a seriesgroupby
    of the values
    """

    if name is None:
        name = func.__name__

    transformed = dfgb.obj.apply(func, axis=1, reduce=False)
    return pd.DataFrame({name: transformed}).groupby(dfgb.grouper)


def take_groups(dfgb, n):
    """
    Return a DataFrameGroupBy holding the
    up to the first n groups
    """

    return_groups = []

    for i, (key, group) in enumerate(dfgb):
        if i >= n:
            break
        return_groups.append(group)

    return combine_data_frames(return_groups).groupby(dfgb.keys)


def pivot_groups(dfgb, **kwargs):
    """
    Pivot a DataFrameGroupBy.
    Takes all the normal keyword args of a pivot
    """
    return dfgb.reset_index().pivot(**kwargs)


def apply_groups(dfgb, *args, **kwargs):
    """
    Return a DataFrameGroupBy object with each
    group of the original DataFrameGroupBy
    transformed into a new dataframe, where
    each column of these new dataframes is the
    result of one of the arg functions supplied.
    """

    res = OrderedDict()
    for idx, arg in enumerate(args):
        name = arg.__name__
        if name == '<lambda>':
            name += '_{}'.format(idx)
        res[name] = dfgb.obj.apply(arg, axis=1, **kwargs)

    return pd.DataFrame(res).groupby(dfgb.grouper)




def hist(dfgb, var=None, *args, **kwargs):
    """
    Takes a data frame (grouped by a variable)
    and plots histograms of the variable 'var'
    for each of the groups.
    """

    if isinstance(dfgb, pd.core.groupby.SeriesGroupBy):
        plotting._series_hist(dfgb, *args, **kwargs)

    elif isinstance(dfgb, pd.core.groupby.DataFrameGroupBy):
        if var is not None:
            plotting._series_hist(dfgb[var], *args, **kwargs)
        else:
            for (var, series) in dfgb._iterate_column_groupbys():
                plt.figure()
                try:
                    plotting._series_hist(series, *args, **kwargs)
                    plt.xlabel(var)
                except TypeError as e:
                    print "Failed to plot %s" % var
                    print e
                finally:
                    pass
    else:
        pass


def hist_functions(dfgb, functions, cols=2, **kwargs):
    """
    Take a DataFrameGroupBy and a list of functions and make a
    grid of plots showing a histogram of the values of each
    function applied to each group individually.
    Each function should take a row in the dataframe and
    can reference columns using dict-like access on that row.
    Useful for exploring new features in classification
    """

    rows = math.ceil(len(functions) / cols)

    for i, function in enumerate(functions):
        plt.subplot(rows, cols, i+1)
        hist(map_groups(dfgb, function), **kwargs)
        plt.xlabel(function.__name__)


def scatter(dfgb, x, y, **kwargs):
    """
    Takes a grouped data frame and draws a scatter
    plot of the suppied variables wtih a different
    color for each group
    """
    ax = plt.gca()
    color_cycle = ax._get_lines.color_cycle
    for (color, (key, grp)) in zip(color_cycle, dfgb):
        plt.scatter(grp[x], grp[y], color=color, label=key, **kwargs)
    plt.legend(loc='best')
    plt.xlabel(x)
    plt.ylabel(y)


def stacked_counts_plot(dfgb, category, ratio=False, **kwargs):
    """
    Takes a dataframe that has been grouped and
    plot a stacked bar-plot representing the makeup of
    the input category per group.
    Optionally, show the ratio of the category in each group.

    Convert this:
    category  group
    A         1
    A         1
    A         2
    B         1
    B         2

    Into this:
    1: A A B
    2: A B
    as a barplot
    """

    counts = dfgb[category].value_counts().unstack().fillna(0.)

    if ratio:
        denom = counts.sum(axis=1)
        counts = counts.divide(denom, axis='index')

    ax = plt.gca()
    plot = counts.plot(kind="bar", stacked=True, subplots=False, ax=ax, **kwargs)
    for container in plot.containers:
        plt.setp(container, width=1)


def save_grouped_hists(dfgb, output_file, title=None, *args, **kwargs):
    _save_plots(dfgb, plotting._series_hist, output_file, title, *args, **kwargs)