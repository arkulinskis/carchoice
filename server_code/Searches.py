"""Saved searches: a member's Explore filters under a name, to open again or share."""
import json

import anvil.server
from anvil.tables import app_tables

from . import common as C

MAX_SEARCHES = 100


def _out(r):
    return {"id": r.get_id(), "name": r["name"], "filters": r["filters"] or {}, "summary": r["summary"] or "",
            "count": r["count"], "created": C.iso(r["created"]), "updated": C.iso(r["updated"])}


def _mine(search_id):
    me = C.require_user()
    r = C.row_by_id(app_tables.searches, search_id)
    if r is None or r["user"] != me:
        return me, None
    return me, r


@anvil.server.callable(require_user=True)
def list_searches():
    me = C.require_user()
    rows = sorted(app_tables.searches.search(user=me), key=lambda r: C.iso(r["updated"]) or "", reverse=True)
    return C.ok(searches=[_out(r) for r in rows])


@anvil.server.callable(require_user=True)
def save_search(name, filters, summary="", count=None):
    me = C.require_user()
    name = C.text(name, 80)
    if len(name) < 2:
        return C.fail("Give the search a name (at least 2 characters).")
    if not isinstance(filters, dict):
        return C.fail("Those filters didn't make sense.")
    if len(json.dumps(filters)) > 12000:
        return C.fail("That search is too big to save.")
    if len(app_tables.searches.search(user=me)) >= MAX_SEARCHES:
        return C.fail("You have %d saved searches: delete a few first." % MAX_SEARCHES)
    count = int(count) if isinstance(count, (int, float)) else None
    r = app_tables.searches.add_row(user=me, name=name, filters=filters, summary=C.text(summary, 400), count=count,
                                    created=C.now(), updated=C.now(), is_demo=False)
    return C.ok(search=_out(r))


@anvil.server.callable(require_user=True)
def rename_search(search_id, name):
    me, r = _mine(search_id)
    if r is None:
        return C.fail("That search isn't yours or no longer exists.")
    name = C.text(name, 80)
    if len(name) < 2:
        return C.fail("Give the search a name (at least 2 characters).")
    r.update(name=name, updated=C.now())
    return C.ok(search=_out(r))


@anvil.server.callable(require_user=True)
def delete_search(search_id):
    me, r = _mine(search_id)
    if r is not None:
        r.delete()
    return C.ok()
