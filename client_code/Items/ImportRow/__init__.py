from anvil import *

from ._anvil_designer import ImportRowTemplate
from ... import state


class ImportRow(ImportRowTemplate):
    """One import in Admin -> Car data. item = from admin_imports. Undo raises x-undo on the panel."""

    def __init__(self, **properties):
        super().__init__(**properties)
        it = self.item
        undone = it["status"] == "undone"
        self.status.text = "Undone" if undone else ("Starter set" if it["kind"] == "seed" else "Active")
        self.status.role = ["badge", "badge-warn" if undone else "badge-good"]
        self.meta.text = " · ".join(x for x in [state.short_date(it["created"]) + " " + it["created"][:4], it["who"], it["source"]] if x)
        self.counts.text = "%s added, %s updated · %s still in the catalogue" % (it["added"], it["updated"], it["still_here"])
        self.undo_button.visible = not undone and it["still_here"] > 0
        state.set_control_attr(self.undo_button, "aria-label", "Remove the cars %s added" % it["filename"])

    @handle("undo_button", "click")
    def undo_button_click(self, **event_args):
        self.parent.raise_event("x-undo", item=self.item)
