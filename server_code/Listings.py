"""Listings a member found on marketplaces (their links, kept here instead of in bookmarks), with a simple price check:
for each model, listings in the same currency are put on the same footing (age and mileage) and compared with each
other, so the member can see which one is priced well.

The price check assumes a car loses about 12% of its value per year of age and 3% per 10,000 km. It only compares a
member's own listings with each other; it is a guide, not a valuation.
"""
import statistics
from urllib.parse import urlparse

import anvil.server
from anvil.tables import app_tables

from . import common as C
from . import Cars

STATUSES = ["Watching", "Contacted", "Seen it", "Not for me", "Bought"]
CURRENCIES = ["USD", "CAD", "EUR", "GBP", "AUD"]
YEAR_RATE = 0.88   # value kept per year of age
KM_RATE = 0.03     # value lost per 10,000 km
MAX_LISTINGS = 500


def host(url):
    try:
        h = urlparse(url).netloc.lower()
    except ValueError:
        return ""
    return h[4:] if h.startswith("www.") else h


def _num(v, lo, hi, name):
    if v in (None, ""):
        return None, None
    try:
        f = float(str(v).replace(",", "").replace(" ", ""))
    except ValueError:
        return None, "%s needs to be a number." % name
    if f < lo or f > hi:
        return None, "%s looks wrong (%s)." % (name, v)
    return (int(f) if f == int(f) else f), None


def score(rows):
    """{listing id: {"ratio", "verdict", "rank", "of", "fair"}} for listings with a price and a year, grouped by model
    and currency (groups of two or more)."""
    groups: dict = {}
    for r in rows:
        if r["car"] is None or not r["price"] or not r["year"] or r["status"] == "Not for me":
            continue
        groups.setdefault((r["car"].get_id(), r["currency"] or "USD"), []).append(r)
    out = {}
    for items in groups.values():
        if len(items) < 2:
            continue
        ref_year = statistics.median([r["year"] for r in items])
        kms = [r["km"] for r in items if r["km"] is not None]
        ref_km = statistics.median(kms) if kms else 0
        eq = []
        for r in items:
            km = r["km"] if r["km"] is not None else ref_km
            v = r["price"] * (YEAR_RATE ** (r["year"] - ref_year)) * (1 + KM_RATE * (km - ref_km) / 10000.0)
            eq.append((v, r))
        mid = statistics.median([v for v, _ in eq])
        ranked = sorted(eq, key=lambda t: t[0])
        for rank, (v, r) in enumerate(ranked, start=1):
            ratio = v / mid if mid else 1
            verdict = "Good price" if ratio <= 0.93 else ("Pricey" if ratio >= 1.07 else "Fair price")
            fair = mid / ((YEAR_RATE ** (r["year"] - ref_year)) * (1 + KM_RATE * ((r["km"] if r["km"] is not None else ref_km) - ref_km) / 10000.0))
            out[r.get_id()] = {"ratio": round(ratio, 3), "verdict": verdict, "rank": rank, "of": len(items),
                               "fair": int(round(fair, -2))}
    return out


def _out(r, scores):
    car = r["car"]
    return {"id": r.get_id(), "url": r["url"], "host": host(r["url"]), "title": r["title"] or host(r["url"]),
            "price": r["price"], "currency": r["currency"] or "USD", "km": r["km"], "year": r["year"],
            "location": r["location"] or "", "seller": r["seller"] or "", "notes": r["notes"] or "",
            "status": r["status"] or "Watching", "created": C.iso(r["created"]),
            "car_id": car.get_id() if car is not None else None,
            "car_name": "%s %s" % (car["make"], car["model"]) if car is not None else "",
            "score": scores.get(r.get_id())}


def stats_by_car(me):
    rows = list(app_tables.listings.search(user=me))
    scores = score(rows)
    out: dict = {}
    for r in rows:
        if r["car"] is None:
            continue
        d = out.setdefault(r["car"].get_id(), {"count": 0, "best": None})
        d["count"] += 1
        sc = scores.get(r.get_id())
        if sc and sc["rank"] == 1:
            d["best"] = {"id": r.get_id(), "price": r["price"], "currency": r["currency"] or "USD",
                         "verdict": sc["verdict"], "title": r["title"] or host(r["url"])}
    return out


@anvil.server.callable(require_user=True)
def list_listings(car_id=None):
    me = C.require_user()
    rows = list(app_tables.listings.search(user=me))
    scores = score(rows)
    items = [_out(r, scores) for r in rows]
    if car_id:
        items = [i for i in items if i["car_id"] == car_id]
    items.sort(key=lambda i: i["created"] or "", reverse=True)
    cars: dict = {}
    for r in rows:
        if r["car"] is not None:
            cars[r["car"].get_id()] = "%s %s" % (r["car"]["make"], r["car"]["model"])
    return C.ok(listings=items, total=len(rows), cars=sorted(cars.items(), key=lambda t: t[1]),
                statuses=STATUSES, currencies=CURRENCIES)


@anvil.server.callable(require_user=True)
def save_listing(data):
    """Add (no id) or change (with id) one of the member's listings."""
    me = C.require_user()
    if not isinstance(data, dict):
        return C.fail("That listing didn't make sense.")
    url = C.text(data.get("url"), 1000)
    if not url.lower().startswith(("http://", "https://")) or not host(url):
        return C.fail("Paste the full link to the listing (starting with https://).")
    row = None
    if data.get("id"):
        row = C.row_by_id(app_tables.listings, data["id"])
        if row is None or row["user"] != me:
            return C.fail("That listing isn't yours or no longer exists.")
    elif len(app_tables.listings.search(user=me)) >= MAX_LISTINGS:
        return C.fail("You have %d saved listings: delete a few old ones first." % MAX_LISTINGS)
    price, e1 = _num(data.get("price"), 0, 10 ** 8, "Price")
    km, e2 = _num(data.get("km"), 0, 3 * 10 ** 6, "Mileage")
    year, e3 = _num(data.get("year"), 1900, C.now().year + 2, "Year")
    err = e1 or e2 or e3
    if err:
        return C.fail(err)
    car = None
    if data.get("car_id"):
        car = C.row_by_id(app_tables.cars, data["car_id"])
        if car is None:
            return C.fail("That car isn't in the catalogue.")
    currency = data.get("currency") if data.get("currency") in CURRENCIES else "USD"
    status = data.get("status") if data.get("status") in STATUSES else "Watching"
    values: dict = dict(url=url, title=C.text(data.get("title"), 160) or host(url), price=price, currency=currency, km=km,
                  year=int(year) if year is not None else None, location=C.text(data.get("location"), 120),
                  seller=C.text(data.get("seller"), 120), notes=C.text(data.get("notes"), 2000, multiline=True),
                  status=status, car=car, updated=C.now())
    if row is None:
        if C.rate_limited("save_listing", 60, 3600):
            return C.fail("That's a lot of listings in one hour. Try again a little later.")
        row = app_tables.listings.add_row(user=me, created=C.now(), is_demo=False, **values)
    else:
        row.update(**values)
    rows = list(app_tables.listings.search(user=me))
    return C.ok(listing=_out(row, score(rows)))


@anvil.server.callable(require_user=True)
def set_listing_status(listing_id, status):
    me = C.require_user()
    row = C.row_by_id(app_tables.listings, listing_id)
    if row is None or row["user"] != me:
        return C.fail("That listing isn't yours or no longer exists.")
    if status not in STATUSES:
        return C.fail("Unknown status.")
    row.update(status=status, updated=C.now())
    return C.ok()


@anvil.server.callable(require_user=True)
def delete_listing(listing_id):
    me = C.require_user()
    row = C.row_by_id(app_tables.listings, listing_id)
    if row is None:
        return C.ok()
    if row["user"] != me:
        return C.fail("That listing isn't yours.")
    row.delete()
    return C.ok()


@anvil.server.callable(require_user=True)
def pick_choices():
    """Cars a listing can belong to: the member's five first, then every other model."""
    me = C.require_user()
    mine = [p["car"] for p in sorted(app_tables.picks.search(user=me), key=lambda p: p["rank"] or 0) if p["car"] is not None]
    ids = {c.get_id() for c in mine}
    rest = sorted((r for r in Cars.published() if r.get_id() not in ids), key=lambda r: (r["make"], r["model"]))
    return {"mine": [(c["make"] + " " + c["model"], c.get_id()) for c in mine],
            "all": [(r["make"] + " " + r["model"], r.get_id()) for r in rest]}
