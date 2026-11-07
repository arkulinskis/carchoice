from anvil import *

from ._anvil_designer import MarketEditRowTemplate
from ... import state


class MarketEditRow(MarketEditRowTemplate):
    """A marketplace in Admin -> Marketplaces. Edit raises x-edit; Delete asks, then x-deleted."""

    def __init__(self, **properties):
        super().__init__(**properties)
        it = self.item
        self.meta.text = " · ".join(x for x in [it["region"], it["kind"], it["url"].split("//")[-1], "" if it["active"] else "hidden"] if x)
        self.search.text = "Own search" if it["search_url"] else "Google search"
        self.search.role = ["badge", "badge-good" if it["search_url"] else ""]
        self.row.classes["is-hidden"] = not it["active"]
        state.set_control_attr(self.edit_button, "aria-label", "Edit %s" % it["name"])
        state.set_control_attr(self.delete_button, "aria-label", "Delete %s" % it["name"])

    @handle("edit_button", "click")
    def edit_button_click(self, **event_args):
        self.parent.raise_event("x-edit", item=self.item)

    @handle("delete_button", "click")
    def delete_button_click(self, **event_args):
        if confirm("It disappears from Where to buy and from every search list.", title="Delete %s?" % self.item["name"],
                   buttons=[("Cancel", False), ("Delete", True)], role="app-dialog"):
            if state.call("delete_market", self.item["id"]) is not None:
                self.parent.raise_event("x-deleted")
