from anvil import *

from ._anvil_designer import SpecRowTemplate
from ... import fmt


class SpecRow(SpecRowTemplate):
    """One spec on #car: label, value, and for numbers where the car sits among every model in the catalogue.
    item = {key, label, kind, unit, dec, value, help, pct}."""

    def __init__(self, **properties):
        super().__init__(**properties)
        it = self.item
        self.value.text = fmt.value(it["kind"], it["unit"], it["dec"], it["value"])
        pct = it.get("pct")
        self.rank_box.visible = pct is not None
        if pct is not None:
            self.dot.style["left"] = "%d%%" % max(0, min(100, pct))
            self.rank.text = ("higher than %d%% of models" % pct) if pct >= 50 else ("lower than %d%% of models" % (100 - pct))
