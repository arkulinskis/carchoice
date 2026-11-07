from anvil import *

from ._anvil_designer import AdminTemplate
from ... import state

TABS = ["overview", "data", "cars", "fields", "markets", "sources", "feedback", "users", "demo"]
HOSTED = {"data", "cars", "fields", "markets", "sources"}  # tabs that are their own Form (AdminTabs/)


class Admin(AdminTemplate):
    """#admin/<tab>: overview numbers, the car data (import, undo, export), single cars, the field list,
    marketplaces, the data-source wishlist, the old feedback inbox, users and the demo data.
    Each tab is its own address, so the browser's back button works."""

    def __init__(self, args=(), **properties):
        super().__init__(**properties)
        self.tab = args[0] if args and args[0] in TABS else "overview"
        self._filter = "new"
        parts = {"overview": self.overview_part, "feedback": self.feedback_part, "users": self.users_part,
                 "demo": self.demo_part}
        tabs = {"overview": self.tab_overview, "data": self.tab_data, "cars": self.tab_cars, "fields": self.tab_fields,
                "markets": self.tab_markets, "sources": self.tab_sources, "feedback": self.tab_feedback,
                "users": self.tab_users, "demo": self.tab_demo}
        for name, part in parts.items():
            part.visible = name == self.tab
        for name, t in tabs.items():
            t.classes["on"] = name == self.tab
            state.set_attr(t, "aria-current", "page" if name == self.tab else None)
        self.tab_host.visible = self.tab in HOSTED
        self.feedback_panel.add_event_handler("x-changed", self._feedback_changed)
        if self.tab in HOSTED:
            self.tab_host.add_component(self._tab_form())
        else:
            getattr(self, "_" + self.tab)()

    def _tab_form(self):
        if self.tab == "data":
            from ...AdminTabs.DataTab import DataTab
            return DataTab()
        if self.tab == "cars":
            from ...AdminTabs.CarsTab import CarsTab
            return CarsTab()
        if self.tab == "fields":
            from ...AdminTabs.FieldsTab import FieldsTab
            return FieldsTab()
        if self.tab == "markets":
            from ...AdminTabs.MarketsTab import MarketsTab
            return MarketsTab()
        from ...AdminTabs.SourcesTab import SourcesTab
        return SourcesTab()

    # ---- overview
    def _overview(self):
        d = state.call("admin_overview")
        self.s_cars.text = str(d["cars"]) + ((" (%d hidden)" % d["hidden"]) if d["hidden"] else "")
        self.s_fields.text, self.s_imports.text = str(d["fields"]), str(d["imports"])
        self.s_sources.text, self.s_users.text = str(d["sources_wanted"]), str(d["users"])
        self.s_picks.text, self.s_searches.text, self.s_listings.text = str(d["picks"]), str(d["searches"]), str(d["listings"])
        self.demo_line.text = "Demo data is %s (%d demo people). New feedback: %d (it arrives in Prepsto)." % (
            d["demo"]["state"], d["demo"]["counts"].get("users", 0), d["feedback_new"])

    # ---- feedback
    def _feedback(self):
        d = state.call("list_feedback", None)
        self._fb = d
        items = [i for i in d["items"] if self._filter == "all" or i["status"] == self._filter]
        self.feedback_panel.items = items
        self.no_feedback.visible = not items
        labels = {"new": "New", "read": "Read", "done": "Done", "all": "All"}
        for key, el in (("new", self.f_new), ("read", self.f_read), ("done", self.f_done), ("all", self.f_all)):
            n = len(d["items"]) if key == "all" else d["counts"].get(key, 0)
            el.text = "%s (%d)" % (labels[key], n)
            el.role = ["seg", "on"] if key == self._filter else ["seg"]

    def _set_filter(self, value):
        self._filter = value
        self._feedback()

    @handle("f_new", "click")
    def f_new_click(self, **event_args):
        self._set_filter("new")

    @handle("f_read", "click")
    def f_read_click(self, **event_args):
        self._set_filter("read")

    @handle("f_done", "click")
    def f_done_click(self, **event_args):
        self._set_filter("done")

    @handle("f_all", "click")
    def f_all_click(self, **event_args):
        self._set_filter("all")

    def _feedback_changed(self, **event_args):
        self._feedback()

    # ---- users
    def _users(self, query=None):
        d = state.call("list_users", query or None)
        self.users_panel.items = d["users"]
        self.users_count.text = state.plural(d["total"], "person", "people")

    @handle("search_box", "pressed_enter")
    def search_box_pressed_enter(self, **event_args):
        self._users(self.search_box.text)

    @handle("search_button", "click")
    def search_button_click(self, **event_args):
        self._users(self.search_box.text)

    # ---- demo data
    def _demo(self):
        d = state.call("admin_overview")["demo"]
        counts = ", ".join("%s %s" % (v, k) for k, v in d["counts"].items())
        self.demo_status.text = "Status: %s · %s" % (d["state"], counts)
        self.demo_load_button.text = "Reload demo data" if d["state"] == "loaded" else "Load demo data"

    @handle("demo_load_button", "click")
    def demo_load_button_click(self, **event_args):
        if confirm("Demo people and their fives are added (any old demo rows are replaced).", title="Load the demo data?",
                   buttons=[("Cancel", False), ("Load", True)], role="app-dialog"):
            if state.call("demo_load"):
                state.toast("Done", "ok")
                self._demo()

    @handle("demo_remove_button", "click")
    def demo_remove_button_click(self, **event_args):
        if confirm("Every demo row is deleted. Real data stays.", title="Remove the demo data?",
                   buttons=[("Cancel", False), ("Remove", True)], role="app-dialog"):
            if state.call("demo_remove"):
                state.toast("Done", "ok")
                self._demo()
