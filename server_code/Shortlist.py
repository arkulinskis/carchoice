"""A member's five: the cars they are deciding between (ranked, with a note each), and their search preferences
(budget, mileage, region...) used to build marketplace searches. Visitors keep their five in the browser; it moves
into the account with picks_merge when they sign up."""
import anvil.server
from anvil.tables import app_tables

from . import common as C
from . import Cars, Listings

MAX_PICKS = 5
PREF_KEYS = {"budget": "number", "max_km": "number", "year_from": "number", "place": "text", "region": "text",
             "currency": "text", "units": "text"}


def _rows(me):
    return sorted(app_tables.picks.search(user=me), key=lambda p: (p["rank"] or 0, C.iso(p["created"]) or ""))


def _renumber(rows):
    for i, p in enumerate(rows):
        if p["rank"] != i + 1:
            p["rank"] = i + 1


def _out(me):
    rows = [p for p in _rows(me) if p["car"] is not None]
    stats = Listings.stats_by_car(me)
    picks = []
    for i, p in enumerate(rows):
        d = dict(Cars.summary(p["car"]), rank=i + 1, note=p["note"] or "")
        d["listings"] = stats.get(p["car"].get_id(), {"count": 0})
        picks.append(d)
    return {"picks": picks, "max": MAX_PICKS, "prefs": prefs_of(me)}


@anvil.server.callable(require_user=True)
def get_picks():
    return C.ok(**_out(C.require_user()))


@anvil.server.callable(require_user=True)
def pick_add(car_id):
    me = C.require_user()
    car = C.row_by_id(app_tables.cars, car_id)
    if car is None:
        return C.fail("That car isn't in the catalogue.")
    if app_tables.picks.get(user=me, car=car) is None:
        rows = _rows(me)
        if len(rows) >= MAX_PICKS:
            return dict(C.fail("Your five is full. Take one out first."), full=True)
        app_tables.picks.add_row(user=me, car=car, rank=len(rows) + 1, note="", created=C.now(), is_demo=False)
    return C.ok(**_out(me))


@anvil.server.callable(require_user=True)
def pick_replace(old_id, new_id):
    """Swap one of the five for another car (keeps its place in the order)."""
    me = C.require_user()
    old = C.row_by_id(app_tables.cars, old_id)
    new = C.row_by_id(app_tables.cars, new_id)
    if new is None:
        return C.fail("That car isn't in the catalogue.")
    p = app_tables.picks.get(user=me, car=old) if old is not None else None
    if p is None:
        return C.fail("That car isn't in your five any more.")
    if app_tables.picks.get(user=me, car=new) is None:
        p.update(car=new, note="", created=C.now())
    return C.ok(**_out(me))


@anvil.server.callable(require_user=True)
def pick_remove(car_id):
    me = C.require_user()
    car = C.row_by_id(app_tables.cars, car_id)
    p = app_tables.picks.get(user=me, car=car) if car is not None else None
    if p is not None:
        p.delete()
    _renumber(_rows(me))
    return C.ok(**_out(me))


@anvil.server.callable(require_user=True)
def pick_move(car_id, delta):
    me = C.require_user()
    rows = _rows(me)
    ids = [p["car"].get_id() if p["car"] is not None else None for p in rows]
    if car_id not in ids:
        return C.fail("That car isn't in your five.")
    i = ids.index(car_id)
    j = max(0, min(len(rows) - 1, i + (1 if (delta or 0) > 0 else -1)))
    rows[i], rows[j] = rows[j], rows[i]
    _renumber(rows)
    return C.ok(**_out(me))


@anvil.server.callable(require_user=True)
def pick_note(car_id, note):
    me = C.require_user()
    car = C.row_by_id(app_tables.cars, car_id)
    p = app_tables.picks.get(user=me, car=car) if car is not None else None
    if p is None:
        return C.fail("That car isn't in your five.")
    p["note"] = C.text(note, 1000, multiline=True)
    return C.ok()


@anvil.server.callable(require_user=True)
def picks_merge(ids):
    """A visitor's five (kept in the browser) joins the account after sign-up, up to five in all."""
    me = C.require_user()
    for i in (ids or [])[:MAX_PICKS]:
        if len(_rows(me)) >= MAX_PICKS:
            break
        car = C.row_by_id(app_tables.cars, i)
        if car is not None and app_tables.picks.get(user=me, car=car) is None:
            app_tables.picks.add_row(user=me, car=car, rank=len(_rows(me)) + 1, note="", created=C.now(), is_demo=False)
    return C.ok(**_out(me))


def prefs_of(user):
    p = user["prefs"] if user is not None else None
    return dict(p) if isinstance(p, dict) else {}


@anvil.server.callable(require_user=True)
def save_prefs(prefs):
    me = C.require_user()
    if not isinstance(prefs, dict):
        return C.fail("Those preferences didn't make sense.")
    clean: dict = {}
    for k, kind in PREF_KEYS.items():
        v = prefs.get(k)
        if v in (None, ""):
            continue
        if kind == "number":
            try:
                v = float(v)
            except (TypeError, ValueError):
                return C.fail("%s needs to be a number." % k.replace("_", " ").capitalize())
            if v < 0 or v > 10 ** 8:
                return C.fail("%s is out of range." % k.replace("_", " ").capitalize())
            clean[k] = int(v) if v == int(v) else v
        else:
            clean[k] = C.text(v, 80)
    me["prefs"] = clean
    return C.ok(prefs=clean)
