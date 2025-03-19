from enum import Enum

import awkward
import numpy
import textual
import textual.widgets

from ..array_parse import ArraySummaryType, detect_summary_type


class DistributionSummary(textual.widgets.TextArea):
    """Statistical summary of the generated figure"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.can_focus = False
        self.border_title = "Distribution summary"
        self.styles.border = ("solid", "gray")

    def update_content(self, array: awkward.Array):
        self.clear()
        summary_type = detect_summary_type(array)
        if summary_type is ArraySummaryType.boolean:
            self.insert(self._boolean_summary(array))
        elif summary_type is ArraySummaryType.discrete:
            self.insert(self._discrete_summary(array))
        else:
            self.insert(self._default_summary(array))

    @classmethod
    def _boolean_summary(cls, array: awkward.Array) -> str:
        num = awkward.count(array, axis=None)
        n_true = awkward.sum(array, axis=None)
        n_false = num - n_true
        eff = n_true / num
        return "\n".join(
            [
                f"Entries    :  {num}",
                f"True/False :  {n_true}/{n_false}",
                f"Ratio (T/F):  {eff}/{1 - eff}",
            ]
        )

    @classmethod
    def _discrete_summary(cls, array: awkward.Array) -> str:
        num = awkward.count(array, axis=None)
        if array.ndim != 1:
            array = awkward.flatten(array, axis=None)
        unique, counts = numpy.unique(array.to_numpy(), return_counts=True)
        mode = None if len(unique) == 0 else unique[numpy.argmax(counts)]
        return "\n".join(
            [
                f"Entries : {num}",
                f"Distinct: {unique}",
                f"mode: {mode}",
            ]
        )

    @classmethod
    def _default_summary(cls, array: awkward.Array) -> str:
        # Default behavior for continuous arrays
        num = awkward.count(array, axis=None)
        min = awkward.min(array, axis=None)
        max = awkward.max(array, axis=None)
        mean = numpy.mean(awkward.flatten(array, axis=None))
        std = numpy.std(awkward.flatten(array, axis=None))
        return "\n".join(
            [
                f"Entries:  {num}",
                f"min/max:  {min}/{max}",
                f"mean   :  {mean}",
                f"stddev :  {std}",
            ]
        )
