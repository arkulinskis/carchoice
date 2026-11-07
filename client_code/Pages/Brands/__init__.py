import anvil.server
from anvil import *

from ._anvil_designer import BrandsTemplate
from ... import state


class Brands(BrandsTemplate):
    """#brands: every brand CarChoice knows (with or without models in the table yet): country, group, founded,
    warranty, website, and a link to its models on Explore."""

    def __init__(self, args=(), **properties):
        super().__init__(**properties)
        state.heading(self.title, 1)
        d = anvil.server.call("list_brands")
        self.all = d["brands"]
        groups = sorted({b["group"] for b in self.all if b["group"]})
        self.country_dd.items = [("All countries", "")] + [(c, c) for c in d["countries"]]
        self.group_dd.items = [("All groups", "")] + [(g, g) for g in groups]
        state.set_control_attr(self.country_dd, "aria-label", "Country")
        state.set_control_attr(self.group_dd, "aria-label", "Group")
        with_models = len([b for b in self.all if b["models"]])
        self.sub.text = "%d brands from %d countries; %d have models in the table (%s)." % (
            len(self.all), len(d["countries"]), with_models, state.plural(d["total_models"], "model"))
        self._draw()

    def _draw(self, **event_args):
        q = (self.search_box.text or "").strip().lower()
        c, g = self.country_dd.selected_value, self.group_dd.selected_value
        items = [b for b in self.all if (not q or q in (b["name"] + " " + b["group"]).lower())
                 and (not c or b["country"] == c) and (not g or b["group"] == g) and (b["models"] or not self.has_box.checked)]
        self.brands_panel.items = items
        self.none.visible = not items

    @handle("search_box", "change")
    def search_box_change(self, **event_args):
        self._draw()

    @handle("country_dd", "change")
    def country_dd_change(self, **event_args):
        self._draw()

    @handle("group_dd", "change")
    def group_dd_change(self, **event_args):
        self._draw()

    @handle("has_box", "change")
    def has_box_change(self, **event_args):
        self._draw()
