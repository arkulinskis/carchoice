import anvil.server
from anvil import *

from ._anvil_designer import EditSourceTemplate
from ... import state


class EditSource(EditSourceTemplate):
    """Add or edit a data source on the wishlist (admins). Closes with the saved one, or None."""

    def __init__(self, source=None, kinds=(), statuses=(), **properties):
        super().__init__(**properties)
        s = source or {}
        self.source = s
        self.heading.text = "Edit the source" if s.get("id") else "Add a data source"
        state.heading(self.heading, 2)
        self.kind_dd.items, self.status_dd.items = list(kinds), list(statuses)
        self.kind_dd.selected_value = s.get("kind") or "Book"
        self.status_dd.selected_value = s.get("status") or "Wishlist"
        self.title_box.text, self.publisher_box.text = s.get("title", ""), s.get("publisher", "")
        self.year_box.text = str(s["year"]) if s.get("year") else ""
        self.url_box.text, self.notes_box.text = s.get("url", ""), s.get("notes", "")

    @handle("cancel_button", "click")
    def cancel_button_click(self, **event_args):
        self.raise_event("x-close-alert", value=None)

    @handle("save_button", "click")
    def save_button_click(self, **event_args):
        data = {"id": self.source.get("id"), "title": self.title_box.text, "kind": self.kind_dd.selected_value,
                "status": self.status_dd.selected_value, "publisher": self.publisher_box.text, "year": self.year_box.text,
                "url": (self.url_box.text or "").strip(), "notes": self.notes_box.text}
        r = anvil.server.call("admin_save_source", data)
        if not r.get("ok"):
            self.message.text, self.message.visible = r.get("error"), True
            return
        self.raise_event("x-close-alert", value=r["source"])
