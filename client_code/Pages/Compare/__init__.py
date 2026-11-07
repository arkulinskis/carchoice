import anvil.js
import anvil.server
from anvil import *

from ._anvil_designer import CompareTemplate
from ... import fmt, picks, state


class Compare(CompareTemplate):
    """#compare: the five side by side, one row per spec; the best value in each row is marked."""

    def __init__(self, args=(), **properties):
        super().__init__(**properties)
        state.heading(self.title, 1)
        ids = picks.ids()
        self.data: dict = {"cars": [], "rows": []}
        if len(ids) >= 2:
            self.data = anvil.server.call("compare_cars", ids)
        n = len(self.data["cars"])
        self.empty.visible = n < 2
        self.table_box.visible = n >= 2
        self.diff_box.visible = n >= 2
        self.sub.text = ("%d cars, %d specs. The best value in each row is marked; specs are approximate." % (n, len(self.data["rows"]))) if n >= 2 else ""
        anvil.js.get_dom_node(self.table).style.setProperty("--n", str(n))
        self._draw()

    def _draw(self):
        cars, n = self.data["cars"], len(self.data["cars"])
        if n < 2:
            return
        u = fmt.units()
        self.u_metric.classes["on"] = u == "metric"
        self.u_imperial.classes["on"] = u == "imperial"
        rows = [{"kind": "head", "label": "", "values": [c["name"] for c in cars], "n": n}]
        group = None
        for r in self.data["rows"]:
            vals = r["values"]
            if self.diff_box.checked and len(set(str(v) for v in vals)) == 1:
                continue
            if r["group"] != group:
                group = r["group"]
                rows.append({"kind": "group", "label": group, "n": n})
            unit = fmt.unit_label(r["unit"], u)
            label = r["label"] + ((" (%s)" % unit) if unit and r["unit"] != "USD" else "")
            rows.append({"kind": "row", "label": label, "values": vals, "best": r["best"], "n": n, "unit": r["unit"],
                         "dec": r["dec"], "vkind": r["kind"]})
        self.rows_panel.items = rows

    def units_click(self, event):
        fmt.set_units(str(event.currentTarget.getAttribute("data-u")))
        self._draw()

    @handle("diff_box", "change")
    def diff_box_change(self, **event_args):
        self._draw()
