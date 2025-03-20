import textual
import textual.app
import textual.containers
import textual.screen
import textual.widgets


class DisplayCurrentFile(textual.containers.HorizontalGroup):
    """Always on items that is used to display the opened files"""

    def __init__(self, file_path: str, tree_path: str, *args, **kwargs):
        self.display_filename = textual.widgets.Static(str(file_path))
        self.display_treepath = textual.widgets.Static(str(tree_path))
        super().__init__(self.display_filename, self.display_treepath)

        # Common styling items
        for comp in [self.display_filename, self.display_treepath]:
            comp.styles.border = ("solid", "gray")
            comp.styles.height = 3
            comp.can_focus = False

        # Distinct styling
        self.display_filename.border_title = "File path:"
        self.display_filename.styles.width = "60%"
        self.display_treepath.border_title = "Tree path:"
        self.display_treepath.styles.width = "40%"

    def update_paths(self, file_path: str | None, tree_path: str | None):
        self.display_filename.update(str(file_path))
        self.display_treepath.update(str(tree_path))


class FilePicker(textual.screen.ModalScreen):
    BINDINGS = [
        textual.app.Binding("ctrl+b", "cancel", "Exiting without opening new file"),
        textual.app.Binding("ctrl+o", "open_file", "Open new file"),
    ]

    def __init__(self, current_display: DisplayCurrentFile, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.file_input = textual.widgets.Input(current_display.display_filename._content)
        self.tree_input = textual.widgets.Input(current_display.display_treepath._content)

        self.open_button = textual.widgets.Button(
            "[O]pen array", variant="primary", id="open"
        )
        self.cancel_button = textual.widgets.Button(
            "[B]ack", variant="error", id="cancel"
        )

        self._container = textual.containers.VerticalGroup(
            self.file_input,
            self.tree_input,
            textual.containers.HorizontalGroup(self.open_button, self.cancel_button),
        )

        self.styles.background = "black"
        self.styles.align = ("center", "middle")
        self.file_input.border_title = "File path:"
        self.tree_input.border_title = "Tree path:"
        self.file_input.styles.border = ("solid", "white")
        self.tree_input.styles.border = ("solid", "white")
        self._container.border_title = "Opening new array"
        self._container.styles.border = ("solid", "white")
        self._container.styles.max_width = "80%"
        self.open_button.styles.width = "50%"
        self.cancel_button.styles.width = "50%"

    def on_button_pressed(self, event: textual.widgets.Button.Pressed) -> None:
        if event.button.id == "open":
            self.action_open_file()
        else:
            self.action_cancel()

    def action_open_file(self):
        self.app.open_file(self.file_input.value, self.tree_input.value)
        self.app.pop_screen()

    def action_cancel(self):
        self.app.pop_screen()

    def compose(self):
        yield self._container
        yield textual.widgets.Footer()
