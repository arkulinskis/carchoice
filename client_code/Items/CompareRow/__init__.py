from anvil import *

from ._anvil_designer import CompareRowTemplate
from ... import fmt


class CompareRow(CompareRowTemplate):
    """One row of the side-by-side table on #compare. item = {kind: "head" | "group" | "row", label, values: [...],
    best: [indexes], n, unit, dec, vkind}. The best value(s) in a row are marked (text, not only colour)."""

    def __init__(self, **properties):
        super().__init__(**properties)
        it = self.item
        kind = it.get("kind", "row")
        n = it.get("n", 0)
        self.row.classes["cm-head"] = kind == "head"
        self.row.classes["cm-group"] = kind == "group"
        self.label.text = it.get("label") or ""
        cells = [self.c0, self.c1, self.c2, self.c3, self.c4]
        boxes = [self.cell0, self.cell1, self.cell2, self.cell3, self.cell4]
        vals = it.get("values") or []
        best = it.get("best") or []
        for i in range(5):
            boxes[i].visible = i < n
            if i >= n:
                continue
            if kind == "group":
                cells[i].text = ""
                continue
            v = vals[i] if i < len(vals) else None
            if kind == "head":
                cells[i].text = v or ""
                continue
            text = fmt.value(it.get("vkind"), it.get("unit"), it.get("dec"), v)
            on = i in best
            cells[i].text = text + (" (best)" if on and it.get("vkind") == "number" else "")
            boxes[i].classes["best"] = on
            boxes[i].classes["nil"] = text == "–"
