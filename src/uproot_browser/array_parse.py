from enum import Enum

import awkward
import numpy


class ArraySummaryType(Enum):
    boolean = 0
    discrete = 1
    continuous = 2


def detect_summary_type(array: awkward.Array) -> str:
    def determine_layout_type(layout):
        if hasattr(layout, "layout"):
            return determine_layout_type(layout.layout)
        elif hasattr(layout, "content"):
            return determine_layout_type(layout.content)
        return layout.dtype

    dtype = determine_layout_type(array.layout)
    # Boolean type
    if dtype == numpy.bool:
        return ArraySummaryType.boolean
    # Integer types
    if dtype not in [
        numpy.uint,
        numpy.uint8,
        numpy.uint16,
        numpy.uint32,
        numpy.uint64,
        numpy.int8,
        numpy.int16,
        numpy.int32,
        numpy.int64,
    ]:
        return ArraySummaryType.continuous

    # Checking for continuity
    if array.ndim != 1:
        array = awkward.flatten(array)
    unique = numpy.unique(array.to_numpy())
    if len(unique) == 0:
        return ArraySummaryType.discrete
    min, max = numpy.min(unique), numpy.max(unique)
    span = numpy.arange(min, max + 1)

    # Integer arrays are considered "pseudo-continuous" if:
    # - The unique values density covers the min/max values (>90% occupancy).
    # - There are more than 10 distinct values.
    # If both are true, then we are assuming that this integer array is some form of counting array
    if (len(unique) > 0.9 * len(span)) and len(span) > 10:
        return ArraySummaryType.continuous
    else:
        return ArraySummaryType.discrete


if __name__ == "__main__":
    import uproot

    arr = uproot.open("treemaker.root")["PreSelection"].arrays()
    for field in arr.fields:
        print(field, type(awkward.type(arr[field])))
    print(arr.fields)
