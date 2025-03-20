import argparse
import os
from typing import Optional

# Methods for opening an array
import awkward

# Textual TUI element
import textual
import textual.app
import textual.containers
import uproot

# Custom widgets for array information display and manipulation
from .widgets.array_summary import ArraySummary
from .widgets.branch_select import BranchSelectInput, BranchSelectList
from .widgets.dist_figure import DistributionFigure
from .widgets.dist_summary import DistributionSummary
from .widgets.file_selector import DisplayCurrentFile, FilePicker


class UprootBrowser(textual.app.App):
    BINDINGS = [
        textual.app.Binding("ctrl+o", "open_file_dialog", "[O]pen File"),
        textual.app.Binding("ctrl+r", "redraw_plot", "[R]edraw Plot"),
    ]

    def __init__(
        self, file_path: Optional[str] = None, tree_path: Optional[str] = None
    ):
        super().__init__()
        # Identifier for what is opened
        self.file: Optional[str] = None
        self.tree_path: Optional[str] = None
        # The array proper for what is going to be displayed
        self.array: Optional[awkward.Array] = None
        self._load_file_memory(file_path, tree_path)

        # Display elements for choosing branches
        self.branch_select_list = BranchSelectList(array=self.array)
        self.branch_select_input = BranchSelectInput(list_view=self.branch_select_list)
        self._var_select_group = textual.containers.VerticalGroup(
            self.branch_select_input, self.branch_select_list
        )

        # Display elements for generating plots
        self.def_input = PlotDefineInput()
        self.array_summary = ArraySummary()
        self.dist_summary = DistributionSummary()
        self.dist_figure = DistributionFigure()
        self._summary_cont = textual.containers.HorizontalGroup(
            self.array_summary, self.dist_summary
        )
        self._output_group = textual.containers.VerticalGroup(
            self.def_input,
            textual.containers.VerticalGroup(self.dist_figure, self._summary_cont),
        )

        # Display elements for what the file that is opened
        self.file_display = DisplayCurrentFile(file_path, tree_path)
        # Floating elements for displaying text help messages and dialog
        self.warn = WarningBlock()
        self.error = ErrorBlock()

        # Styling of display elements is place somewhere else
        self._init_style()

    def _init_style(self):
        self._var_select_group.styles.width = "35%"

        # Limiting the amount of information that can be displayed
        self.dist_figure.styles.height = "3fr"
        self.array_summary.styles.max_height = 6
        self.dist_summary.styles.max_height = 6
        self.array_summary.styles.min_height = 3
        self.dist_summary.styles.min_height = 3
        self._summary_cont.styles.height = "1fr"

    def compose(self) -> textual.app.ComposeResult:
        # Main layout for the fixed elements
        yield textual.containers.VerticalGroup(
            self.file_display,
            textual.containers.HorizontalGroup(
                self._var_select_group, self._output_group
            ),
            textual.widgets.Rule(),
            textual.widgets.Footer(),
        )
        # Floating elements
        yield self.warn
        yield self.error

    def open_file(self, file_path: str, tree_path: str):
        if self._load_file_memory(file_path, tree_path):
            self._load_file_interface()

    def action_open_file_dialog(self):
        self.push_screen(FilePicker(self.file_display))

    def _load_file_memory(self, file_path: str | None, tree_path: str | None) -> bool:
        self.file = None
        self.tree_path = None
        self.array = None

        if file_path is None or tree_path is None:
            return False
        if not os.path.isfile(file_path):
            textual.app.warnings.warn("Requested path is not a file")
            return False
        try:
            uproot_file = uproot.open(file_path)
        except Exception:  # Capturing all errors
            textual.app.warnings.warn("Failed to open file")
            return False

        self.file = file_path
        if tree_path not in uproot_file:
            textual.app.warnings.warn("Tree path does not exist")
            return False

        tree = uproot_file[tree_path]
        if not (
            isinstance(tree, uproot.models.TTree.Model_TTree)
            or isinstance(tree, uproot.models.TTree.Model_TTree_v16)
            or isinstance(tree, uproot.models.TTree.Model_TTree_v17)
            or isinstance(tree, uproot.models.TTree.Model_TTree_v18)
            or isinstance(tree, uproot.models.TTree.Model_TTree_v19)
            or isinstance(tree, uproot.models.TTree.Model_TTree_v20)
        ):
            textual.app.warnings.warn("Tree path does not point to a tree")
            textual.app.warnings.warn(f"Got type {type(uproot_file[tree_path])}")
            return False

        self.tree_path = tree_path
        self.array = uproot_file[tree_path].arrays()
        return True

    def _load_file_interface(self) -> None:
        # Calling the various items to be updated
        self.file_display.update_paths(self.file, self.tree_path)
        self._clear_plot_display()
        self.branch_select_input.clear()
        self.branch_select_list._update_with_array(self.array)

    def _update_file_display(self):
        self.display_file.clear()
        self.display_file.insert(str(self.file))
        self.display_tree.clear()
        self.display_tree.insert(str(self.file))

    def _clear_plot_display(self):
        self.def_input.clear()
        self.array_summary.clear()
        self.dist_summary.clear()

    def submit_branch_to_plot(self, branch_name):
        self.def_input.value = f"array['{branch_name}']"
        self.execute_plot()

    def action_redraw_plot(self):
        self.execute_plot()

    def execute_plot(self):
        run_process = self.def_input.value.replace("array", "self.array")
        array = eval(run_process)
        self.array_summary.update_content(array)
        self.dist_summary.update_content(array)
        self.dist_figure.update_content(array)


class PlotDefineInput(textual.widgets.Input):
    BINDINGS = [
        textual.app.Binding(
            "enter",
            "execute_plot",
            description="Sending array distribution for plotting",
            show=False,
        ),
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.can_focus = True
        self.border_title = "Plot definition"
        self.styles.border = ("solid", "gray")

    def action_execute_plot(self):
        self.app.execute_plot()


class WarningBlock(textual.widgets.Static):
    """
    Displaying warning messages as a block of text, even when this message is
    displayed, non of the user interactivity should be broken
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.styles.background = "yellow"
        self.styles.color = "black"
        self.border_title = "!!Warning!!"
        self.styles.border = ("solid", "orange")
        self.styles.max_height = 10  # Warning messages should be at most 10 lines tall
        self.styles.max_width = 40
        self.styles.position = "absolute"
        self.styles.display = "none"

    def display_message(self, msg):
        self.update(msg)


class ErrorBlock(textual.widgets.Static):
    """
    Display error message. If an error is generated, it should disable focus on
    all other elements. Untile the user acknowledges the error
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "file", nargs="?", type=str, help="Specifying a root file to be used"
    )
    parser.add_argument(
        "--tree_path",
        type=str,
        help="Path to tree within the root file",
        default="Events",
    )
    args = parser.parse_args()
    app = UprootBrowser(args.file, args.tree_path)
    app.run()
