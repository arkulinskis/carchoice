from anvil import *

from ._anvil_designer import QueryLinkTemplate
from ... import state


class QueryLink(QueryLinkTemplate):
    """A marketplace search, ready to open in a new tab. item = {name, kind, notes, open_url, how} from queries.links."""

    def __init__(self, **properties):
        super().__init__(**properties)
        state.set_attr(self.open_link, "rel", "noopener")
        state.set_attr(self.open_link, "title", "%s (%s, opens a new tab)" % (self.item["name"], self.item["how"].lower()))
