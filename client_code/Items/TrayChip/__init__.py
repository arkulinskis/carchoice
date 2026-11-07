from anvil import *

from ._anvil_designer import TrayChipTemplate
from ... import router, state


class TrayChip(TrayChipTemplate):
    """One of the five slots in the Explore tray. item = {i, id, name} or {i, empty: True}.
    Remove raises x-unpick on the panel."""

    def __init__(self, **properties):
        super().__init__(**properties)
        it = self.item
        empty = bool(it.get("empty"))
        self.num.text = str(it["i"] + 1)
        self.slot.classes["empty"] = empty
        self.link.visible = not empty
        self.remove_button.visible = not empty
        self.empty_txt.visible = empty
        if not empty:
            self.name.text = it["name"]
            state.set_attr(self.link, "href", router.href("car", it["id"]))
            self.remove_button.tooltip = "Take %s out of your five" % it["name"]
            state.set_control_attr(self.remove_button, "aria-label", "Take %s out of your five" % it["name"])
            state.set_control_attr(self.remove_button, "data-key", "x" + it["id"])

    @handle("remove_button", "click")
    def remove_button_click(self, **event_args):
        self.parent.raise_event("x-unpick", car_id=self.item["id"])
