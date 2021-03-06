from __future__ import print_function, division, absolute_import

from functools import reduce as _reduce
import logging

log = logging.getLogger(__name__)

def _toposort(data):
    """Dependencies are expressed as a dictionary whose keys are items
and whose values are a set of dependent items. Output is a list of
sets in topological order. The first set consists of items with no
dependences, each subsequent set consists of items that depend upon
items in the preceding sets.
"""

    # Special case empty input.
    if len(data) == 0:
        return

    # Ignore self dependencies.
    for k, v in data.items():
        v.discard(k)
    # Find all items that don't depend on anything.
    extra_items_in_deps = _reduce(set.union, data.values()) - set(data.keys())
    # Add empty dependences where needed.
    data.update({item:set() for item in extra_items_in_deps})
    while True:

        ordered = sorted(set(item for item, dep in data.items() if len(dep) == 0))
        if not ordered:
            break

        for item in ordered:
            yield item
            data.pop(item, None)

        for dep in sorted(data.values()):
            dep -= set(ordered)
#         data = {item: (dep - ordered)
#                 for item, dep in data.items()
#                     if item not in ordered}

    if len(data) != 0:
        msg = 'Cyclic dependencies exist among these items: {}'
        raise ValueError(msg.format(' -> '.join(repr(x) for x in data.keys())))

def pop_key(data):
    '''
    Pop an item from the graph that has the fewest dependencies in the case of a tie
    The winners will be sorted alphabetically
    '''
    items = sorted(data.items(), key=lambda item: (len(item[1]), item[0]))
    key = items[0][0]

    data.pop(key)

    for dep in data.values():
        dep.discard(key)

    return key

def _safe_toposort(data):
    """Dependencies are expressed as a dictionary whose keys are items
and whose values are a set of dependent items. Output is a list of
sets in topological order. The first set consists of items with no
dependencies, each subsequent set consists of items that depend upon
items in the preceding sets.
"""

    # Special case empty input.
    if len(data) == 0:
        return

    t = _toposort(data)

    while True:
        try:
            value = next(t)
            yield value
        except ValueError as err:
            log.debug(err.args[0])

            if not data:
                return

            yield pop_key(data)

            t = _toposort(data)

            continue
        except StopIteration:
            return


def toposort(data, safe=True):

    data = {k:set(v) for k, v in data.items()}

    if safe:
        return list(_safe_toposort(data))
    else:
        return list(_toposort(data))
