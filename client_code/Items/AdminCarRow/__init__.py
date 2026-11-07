from anvil import *

from ._anvil_designer import AdminCarRowTemplate
from ... import router, state


class AdminCarRow(AdminCarRowTemplate):
    """One car in Admin -> Cars: hide/show it in the catalogue, or delete it. item = from admin_cars."""

    def __init__(self, **properties):
        super().__init__(**properties)
        self._draw()

    def _draw(self):
        it = self.item
        hidden = it["status"] == "hidden"
        self.meta.text = "%s · %d facts · updated %s" % (it["source"] or "no source", it["fields"], state.short_date(it["updated"]))
        self.status.text = "Hidden" if hidden else "Shown"
        self.status.role = ["badge", "badge-warn" if hidden else "badge-good"]
        self.toggle_button.text = "Show" if hidden else "Hide"
        self.row.classes["is-hidden"] = hidden
        state.set_attr(self.link, "href", router.href("car", it["id"]))
        state.set_control_attr(self.toggle_button, "aria-label", "%s %s" % (self.toggle_button.text, it["name"]))
        state.set_control_attr(self.delete_button, "aria-label", "Delete %s" % it["name"])

    @handle("toggle_button", "click")
    def toggle_button_click(self, **event_args):
        new = "published" if self.item["status"] == "hidden" else "hidden"
        if state.call("admin_car_status", self.item["id"], new) is not None:
            self.item["status"] = new
            self._draw()
            self.parent.raise_event("x-changed")

    @handle("delete_button", "click")
    def delete_button_click(self, **event_args):
        if confirm("It leaves the catalogue and people's fives (their saved listings stay, without the car).",
                   title="Delete the %s?" % self.item["name"], buttons=[("Cancel", False), ("Delete", True)], role="app-dialog"):
            if state.call("admin_delete_car", self.item["id"]) is not None:
                self.parent.raise_event("x-deleted")
