from anvil import *

from ._anvil_designer import MiniCarTemplate
from ... import fmt, router, state


class MiniCar(MiniCarTemplate):
    """A small link to a car's page: name + one detail. item = a car summary (Cars.summary), optionally with
    count (how many people have it in their five)."""

    def __init__(self, **properties):
        super().__init__(**properties)
        it = self.item
        self.name.text = it["name"]
        if it.get("count"):
            self.detail.text = "in %s" % state.plural(it["count"], "person's five", "people's fives")
        else:
            self.detail.text = fmt.facts(it)
        state.set_attr(self.link, "href", router.href("car", it["id"]))
