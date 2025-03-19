import awkward
import textual
import textual.widgets


class ArraySummary(textual.widgets.TextArea):
    """Simple output description"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.can_focus = False
        self.border_title = "Array summary"
        self.styles.border = ("solid", "gray")

    def update_content(self, array: awkward.Array):
        self.clear()
        self.insert(f"Type  : {awkward.type(array)}\n")
        self.insert(f"Dims  : {array.ndim}\n")
        self.insert(f"values: {array}")
