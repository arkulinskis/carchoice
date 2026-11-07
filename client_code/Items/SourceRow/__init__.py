from anvil import *

from ._anvil_designer import SourceRowTemplate
from ... import state

STATUS_ROLE = {"Wishlist": "badge-warn", "Requested": "badge-brand", "Have it": "badge-good", "Imported": "badge-good"}


class SourceRow(SourceRowTemplate):
    """A data source in Admin -> Data sources (books, manuals, datasets to get). Edit raises x-edit; Delete x-deleted."""

    def __init__(self, **properties):
        super().__init__(**properties)
        it = self.item
        self.meta.text = " · ".join(str(x) for x in [it["kind"], it["publisher"], it["year"]] if x)
        self.status.role = ["badge", STATUS_ROLE.get(it["status"], "")]
        state.set_attr(self.url_link, "rel", "noopener")
        state.set_control_attr(self.edit_button, "aria-label", "Edit %s" % it["title"])
        state.set_control_attr(self.delete_button, "aria-label", "Delete %s" % it["title"])

    @handle("edit_button", "click")
    def edit_button_click(self, **event_args):
        self.parent.raise_event("x-edit", item=self.item)

    @handle("delete_button", "click")
    def delete_button_click(self, **event_args):
        if confirm("It leaves the list.", title="Delete this source?", buttons=[("Cancel", False), ("Delete", True)],
                   role="app-dialog"):
            if state.call("admin_delete_source", self.item["id"]) is not None:
                self.parent.raise_event("x-deleted")
