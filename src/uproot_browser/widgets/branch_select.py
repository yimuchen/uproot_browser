import time
from typing import List

import awkward
import textual
import textual.widgets
from fuzzyfinder import fuzzyfinder


class BranchSelectInput(textual.widgets.Input):
    """
    User input field to the branch fuzzy finder
    """

    BINDINGS = [
        textual.app.Binding(
            "up",
            "move_list_up",
            description="Move to the previous selection",
            show=False,
        ),
        textual.app.Binding(
            "down",
            "move_list_down",
            description="Move to the next selection",
            show=False,
        ),
        textual.app.Binding(
            "enter",
            "submit",
            description="Send the selected branch to be displayed",
            show=False,
        ),
    ]

    def __init__(self, list_view: textual.widgets.ListView, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.can_focus = True
        self.border_title = "Select branch"
        # Reference to the list display use for fuzzy searching
        self.list_ref = list_view

    def replace(self, text: str, start: int, end: str) -> None:
        super().replace(text, start, end)
        self.list_ref.fuzzy_filter(self.value)

    def action_move_list_up(self):
        self.list_ref.action_cursor_up()

    def action_move_list_down(self):
        self.list_ref.action_cursor_down()

    def action_submit(self):
        highlight = self.list_ref.highlighted_child
        if highlight is not None:
            self.clear()
            self.value = str(highlight.name)
            self.action_end()
            self.app.submit_branch_to_plot(highlight.name)
        else:
            print("Nothing was selected")
        textual.app.warnings.warn(str(self.list_ref.text_selection))


class BranchSelectList(textual.widgets.ListView):
    """
    List display of a the candidates of the fuzzy finder. Notice that we
    intentially make this unfocusable, as all interactions with this items
    should be handled by the main text input field.
    """

    def __init__(self, array: awkward.Array | None, *args, **kwargs):
        self.original_fields = self.get_fields(array)
        super().__init__(*self.make_listitems(self.original_fields), *args, **kwargs)
        self.can_focus = False
        self.border_title = "Matched branches"
        self.styles.border = ("solid", "gray")
        self.last_update = time.time()

    @classmethod
    def get_fields(cls, array: awkward.Array | None) -> List[str]:
        if array is None:
            return []
        return [f for f in array.fields]

    @classmethod
    def make_listitems(cls, fields: List[str]) -> List[textual.widgets.ListItem]:
        return [
            textual.widgets.ListItem(textual.widgets.Static(x), name=x) for x in fields
        ]

    def _update_with_array(self, array: awkward.Array):
        self.original_fields = array.fields
        self.clear()
        self.extend(self.make_listitems(self.original_fields))

    def fuzzy_filter(self, input_str: str):
        if time.time() - self.last_update < 0.050:
            return  # De-bouncing
        self.clear()
        new_list = (
            self.original_fields
            if input_str == ""
            else fuzzyfinder(input_str, self.original_fields)
        )
        self.extend(
            [
                textual.widgets.ListItem(textual.widgets.Static(f), name=f)
                for f in new_list
            ]
        )
        self.last_update = time.time()
