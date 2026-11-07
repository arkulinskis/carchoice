from anvil import *

from ._anvil_designer import FieldsTabTemplate
from ... import catalog, state

KIND_LABELS = [("Number (range slider)", "number"), ("One choice", "choice"), ("Several choices", "multi"),
               ("Yes / no", "bool"), ("Text", "text")]


class FieldsTab(FieldsTabTemplate):
    """Admin -> Fields: the field list (labels, groups, units, better-when, filter / column), and adding a field."""

    def __init__(self, **properties):
        super().__init__(**properties)
        self.new_kind.items = KIND_LABELS
        self.new_kind.selected_value = "number"
        state.set_control_attr(self.new_kind, "aria-label", "Kind")
        self.fields_panel.add_event_handler("x-saved", self._saved)
        self._load()

    def _load(self):
        self.fields_panel.items = state.call("admin_fields")["fields"]

    def _saved(self, **event_args):
        catalog.forget()

    @handle("add_button", "click")
    def add_button_click(self, **event_args):
        label = (self.new_label.text or "").strip()
        if len(label) < 2:
            state.toast("Give the new field a label.", "error")
            return
        data = {"label": label, "kind": self.new_kind.selected_value, "group": self.new_group.text or "Other",
                "unit": self.new_unit.text or "", "filter": True, "show": False}
        if state.call("admin_save_field", label, data) is not None:
            state.toast("Field added. Fill it with an import.", "ok")
            catalog.forget()
            self.new_label.text = self.new_group.text = self.new_unit.text = ""
            self._load()
