import anvil.server
from anvil import *

from ._anvil_designer import SaveSearchTemplate
from ... import state


class SaveSearch(SaveSearchTemplate):
    """Name and save the current Explore filters (or rename a saved search: pass search=).
    Closes with the saved search, or None."""

    def __init__(self, filters=None, summary="", count=None, suggestion="", search=None, **properties):
        super().__init__(**properties)
        self.filters, self.count, self.search = filters or {}, count, search
        self.summary.text = summary or "All models (no filters yet)"
        self.name_box.text = (search or {}).get("name") or suggestion
        if search:
            self.heading.text = "Rename the search"
            self.save_button.text = "Save name"
            self.summary.text = search.get("summary") or ""
        state.heading(self.heading, 2)
        self._summary = summary

    @handle("", "show")
    def form_show(self, **event_args):
        self.name_box.focus()
        self.name_box.select()

    @handle("name_box", "pressed_enter")
    def name_box_pressed_enter(self, **event_args):
        self.save_button_click()

    @handle("cancel_button", "click")
    def cancel_button_click(self, **event_args):
        self.raise_event("x-close-alert", value=None)

    @handle("save_button", "click")
    def save_button_click(self, **event_args):
        name = (self.name_box.text or "").strip()
        if len(name) < 2:
            self.message.text, self.message.visible = "Give the search a name (at least 2 characters).", True
            return
        self.save_button.enabled = False
        try:
            if self.search:
                r = anvil.server.call("rename_search", self.search["id"], name)
            else:
                r = anvil.server.call("save_search", name, self.filters, self._summary, self.count)
        finally:
            self.save_button.enabled = True
        if not r.get("ok"):
            self.message.text, self.message.visible = r.get("error") or "That didn't work.", True
            return
        self.raise_event("x-close-alert", value=r["search"])
