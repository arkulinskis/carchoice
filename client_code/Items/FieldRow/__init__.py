from anvil import *

from ._anvil_designer import FieldRowTemplate
from ... import state

BETTER = [("–", ""), ("Higher", "high"), ("Lower", "low")]


class FieldRow(FieldRowTemplate):
    """One field (column/filter) in Admin -> Fields: its label, group, unit, which way is better, and whether it is a
    filter and a default column. item = from admin_fields."""

    def __init__(self, **properties):
        super().__init__(**properties)
        it = self.item
        self.info.text = "%s · %s" % (it["kind"], state.plural(it.get("cars") or 0, "car") + " with data")
        self.label_box.text, self.group_box.text, self.unit_box.text = it["label"], it["group"], it["unit"]
        self.better_dd.items = BETTER
        self.better_dd.selected_value = it.get("better") or ""
        self.filter_box.checked, self.show_box.checked = it["filter"], it["show"]
        for c, what in ((self.label_box, "Label"), (self.group_box, "Group"), (self.unit_box, "Unit"), (self.better_dd, "Better when")):
            state.set_control_attr(c, "aria-label", "%s of %s" % (what, it["key"]))
        state.set_control_attr(self.save_button, "aria-label", "Save %s" % it["key"])

    @handle("save_button", "click")
    def save_button_click(self, **event_args):
        data = {"label": self.label_box.text, "group": self.group_box.text, "unit": self.unit_box.text,
                "kind": self.item["kind"], "filter": self.filter_box.checked, "show": self.show_box.checked,
                "better": self.better_dd.selected_value, "help": self.item.get("help") or ""}
        if state.call("admin_save_field", self.item["key"], data) is not None:
            state.toast("Saved %s." % self.item["key"], "ok")
            self.parent.raise_event("x-saved")
