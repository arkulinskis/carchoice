from anvil import *

from ._anvil_designer import MarketRowTemplate
from ... import state

KIND_ROLE = {"Price guide": "badge-good", "Auction": "badge-warn", "Online dealer": "badge-brand", "Dealer": "badge-brand"}


class MarketRow(MarketRowTemplate):
    """A marketplace, dealer, auction or price guide on #markets. item = from list_marketplaces."""

    def __init__(self, **properties):
        super().__init__(**properties)
        it = self.item
        url = it.get("url") or ""
        self.host.text = url.split("//")[-1].rstrip("/")
        self.kind.role = ["badge", KIND_ROLE.get(it.get("kind"), "")]
        state.set_attr(self.site_link, "rel", "noopener")
        state.set_attr(self.site_link, "aria-label", "%s (opens a new tab)" % it["name"])
