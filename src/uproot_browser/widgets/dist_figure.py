from enum import Enum

import awkward
import numpy
import textual_plotext

from ..array_parse import ArraySummaryType, detect_summary_type


class _DisplayBackend(Enum):
    text = 0


class DistributionFigure(textual_plotext.PlotextPlot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.can_focus = False
        self.border_title = "Distribution figure"
        self.styles.border = ("solid", "gray")
        self.backend = _DisplayBackend.text

    def update_content(self, array: awkward.Array):
        self.plt.clear_data()
        self.plt.clear_figure()

        def _fail(array):
            pass

        AType = ArraySummaryType
        BEnd = _DisplayBackend
        _map = {
            (AType.boolean, BEnd.text): self._boolean_figure_text,
            (AType.discrete, BEnd.text): self._discrete_figure_text,
            (AType.continuous, BEnd.text): self._continuous_figure_text,
        }
        _map.get((detect_summary_type(array), self.backend), _fail)(array)
        self.refresh()

    def _boolean_figure_text(self, array: awkward.Array) -> str:
        n_true = awkward.sum(array, axis=None)
        n_false = awkward.count(array, axis=None) - n_true
        self.plt.bar(["True", "False"], [n_true, n_false])

    def _discrete_figure_text(self, array: awkward.Array):
        if array.ndim != 1:
            array = awkward.flatten(array, axis=None)
        unique, counts = numpy.unique(array, return_counts=True)
        counts = counts[numpy.argsort(unique)]
        unique = unique[numpy.argsort(unique)]
        self.plt.bar(unique, counts)

    def _continuous_figure_text(self, array: awkward.Array) -> str:
        if array.ndim != 1:
            array = awkward.flatten(array, axis=None)
        bins = 40
        self.plt.hist(array, bins=bins)
