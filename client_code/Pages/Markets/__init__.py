import anvil.server
from anvil import *

from ._anvil_designer import MarketsTemplate
from ... import prefs, queries, state


class Markets(MarketsTemplate):
    """#markets: marketplaces, classifieds, dealers, auctions and price guides by region, plus a short
    "before you pay" checklist. Admins edit the list in Admin -> Marketplaces."""

    def __init__(self, args=(), **properties):
        super().__init__(**properties)
        state.heading(self.title, 1)
        state.heading(self.tips_title, 2)
        self.markets = anvil.server.call("list_marketplaces")["markets"]
        self.buttons = {"": self.r_all, "US": self.r_us, "Canada": self.r_ca, "UK": self.r_uk, "Europe": self.r_eu,
                        "Baltics": self.r_bt, "Australia": self.r_au}
        for region, b in self.buttons.items():
            b.tag.region = region
            b.add_event_handler("click", self._region_click)
        self.region = args[0] if args and args[0] in self.buttons else queries.default_region(prefs.get())
        self.sub.text = "%d places to buy or price a car, in %d regions. Pick yours." % (len(self.markets), len(self.buttons) - 1)
        self._draw()

    def _draw(self):
        items = [m for m in self.markets if not self.region or m["region"] == self.region]
        if not self.region:
            items = sorted(items, key=lambda m: (queries.REGIONS.index(m["region"]) if m["region"] in queries.REGIONS else 9))
        self.markets_panel.items = items
        for region, b in self.buttons.items():
            b.role = ["seg", "on"] if region == self.region else ["seg"]
            state.set_control_attr(b, "aria-pressed", "true" if region == self.region else "false")

    def _region_click(self, sender, **event_args):
        self.region = sender.tag.region
        self._draw()
