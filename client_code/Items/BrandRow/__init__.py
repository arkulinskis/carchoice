from anvil import *
from anvil.js import window

from ._anvil_designer import BrandRowTemplate
from ... import router, state


class BrandRow(BrandRowTemplate):
    """One brand on #brands. item = from list_brands. "12 models" opens Explore filtered to the make."""

    def __init__(self, **properties):
        super().__init__(**properties)
        it = self.item
        self.founded.text = str(it["founded"]) if it.get("founded") else "–"
        n = it.get("models") or 0
        self.models_link.visible = bool(n)
        self.no_models.visible = not n
        if n:
            self.models.text = state.plural(n, "model")
            enc = window.CC.encodeState(window.JSON.parse('{"f": {"make": [%s]}}' % window.JSON.stringify(it["name"])))
            state.set_attr(self.models_link, "href", router.href("explore", enc))
            state.set_attr(self.models_link, "aria-label", "See the %s %s models" % (n, it["name"]))
        w, pw = it.get("warranty"), it.get("pt_warranty")
        self.warranty.text = ("%s / %s yrs" % (w, pw)) if w else "–"
        self.site_link.visible = bool(it.get("website"))
        state.set_attr(self.site_link, "rel", "noopener")
        state.set_attr(self.site_link, "aria-label", "%s website (opens a new tab)" % it["name"])
