"""The car catalogue for everyone (no sign-in needed): the whole table for the Explore engine, one car's spec sheet,
side-by-side comparison, brands.

get_catalog sends the whole catalogue as ONE JSON string (the browser caches it by version and hands it straight to the
JavaScript engine, so the browser's Python never has to unpack hundreds of rows).
"""
import json

import anvil.server
from anvil.tables import app_tables

from . import common as C
from . import DemoData, Seed

SUMMARY = ["price", "hp", "body", "fuel", "drive", "l100", "ev_range", "seats", "cargo", "zero100"]


def fields():
    rows = sorted(app_tables.car_fields.search(), key=lambda r: (r["sort"] or 0))
    return [{"key": r["key"], "label": r["label"], "group": r["grp"] or "Other", "kind": r["kind"], "unit": r["unit"] or "",
             "dec": r["decimals"] or 0, "filter": bool(r["filter"]), "show": bool(r["show"]), "help": r["help"] or "",
             "better": r["better"] or ""} for r in rows]


def published():
    return [r for r in app_tables.cars.search() if (r["status"] or "published") == "published"]


def version():
    return C.get_setting("catalog_v") or "0"


def summary(r):
    s = r["specs"] or {}
    d = {"id": r.get_id(), "make": r["make"], "model": r["model"], "name": "%s %s" % (r["make"], r["model"])}
    for k in SUMMARY:
        d[k] = s.get(k)
    return d


def ready():
    Seed.ensure_seeded()
    DemoData.ensure_loaded()


@anvil.server.callable
def get_catalog(have=None):
    """{"v", "json"} or {"v", "same": True} when the browser already has this version."""
    ready()
    v = version()
    if have and have == v:
        return {"v": v, "same": True}
    cars = [{"id": r.get_id(), "s": r["specs"] or {}} for r in published()]
    cars.sort(key=lambda c: (c["s"].get("make", ""), c["s"].get("model", "")))
    return {"v": v, "json": json.dumps({"v": v, "fields": fields(), "cars": cars}, separators=(",", ":"))}


def _pct(values, v):
    """Share of models with a lower value (0-100)."""
    if not values:
        return None
    lower = sum(1 for x in values if x < v)
    same = sum(1 for x in values if x == v)
    return int(round(100.0 * (lower + same / 2.0) / len(values)))


def _similar(row, rows, n=6):
    s = row["specs"] or {}
    keys = ["price", "hp", "length", "seats", "cargo", "weight"]
    spans = {}
    for k in keys:
        vals = [(r["specs"] or {}).get(k) for r in rows]
        vals = [x for x in vals if isinstance(x, (int, float))]
        spans[k] = (max(vals) - min(vals)) if len(vals) > 1 else 1
    scored = []
    for r in rows:
        if r == row:
            continue
        o = r["specs"] or {}
        d, used = 0.0, 0
        for k in keys:
            a, b = s.get(k), o.get(k)
            if isinstance(a, (int, float)) and isinstance(b, (int, float)) and spans[k]:
                d += ((a - b) / float(spans[k])) ** 2
                used += 1
        if not used:
            continue
        d = d / used
        if o.get("body") != s.get("body"):
            d += 0.05
        if set(o.get("fuel") or []) & set(s.get("fuel") or []):
            d -= 0.01
        scored.append((d, r))
    scored.sort(key=lambda t: t[0])
    return [summary(r) for _, r in scored[:n]]


def _brand(make):
    b = app_tables.brands.get(name=make)
    if b is None:
        return None
    return {"name": b["name"], "country": b["country"] or "", "group": b["group_name"] or "", "founded": b["founded"],
            "website": b["website"] or "", "warranty": b["warranty"], "pt_warranty": b["pt_warranty"]}


def _picked(row):
    me = C.me()
    return bool(me is not None and app_tables.picks.get(user=me, car=row))


@anvil.server.callable
def get_car(car_id):
    ready()
    row = C.row_by_id(app_tables.cars, car_id)
    if row is None or (row["status"] or "published") != "published":
        return C.fail("That car isn't in the catalogue (any more).")
    rows = published()
    s = row["specs"] or {}
    groups, cur = [], None
    for f in fields():
        k = f["key"]
        if k in ("make", "model") or s.get(k) in (None, "", []):
            continue
        if cur is None or cur["group"] != f["group"]:
            cur = {"group": f["group"], "rows": []}
            groups.append(cur)
        item = {"key": k, "label": f["label"], "kind": f["kind"], "unit": f["unit"], "dec": f["dec"], "value": s[k],
                "help": f["help"], "pct": None}
        if f["kind"] == "number" and isinstance(s[k], (int, float)):
            vals = [(r["specs"] or {}).get(k) for r in rows]
            item["pct"] = _pct([x for x in vals if isinstance(x, (int, float))], s[k])
        cur["rows"].append(item)
    return C.ok(car=dict(summary(row), notes=row["notes"] or "", source=row["source"] or "",
                         updated=C.iso(row["updated"]), groups=groups, specs=s),
                brand=_brand(row["make"]), similar=_similar(row, rows), picked=_picked(row),
                pickers=len(app_tables.picks.search(car=row)))


@anvil.server.callable
def cars_summary(ids):
    """Short facts for a list of car ids (a visitor's shortlist kept in the browser)."""
    out = []
    for i in (ids or [])[:10]:
        r = C.row_by_id(app_tables.cars, i)
        if r is not None:
            out.append(summary(r))
    return out


@anvil.server.callable
def compare_cars(ids):
    """Rows for the side-by-side table: [{label, unit, kind, dec, values: [...], best: [indexes], group}]"""
    ready()
    cars = [r for r in (C.row_by_id(app_tables.cars, i) for i in (ids or [])[:5]) if r is not None]
    rows = []
    for f in fields():
        k = f["key"]
        if k in ("make", "model"):
            continue
        vals = [(c["specs"] or {}).get(k) for c in cars]
        if all(v in (None, "", []) for v in vals):
            continue
        best = []
        nums = [v for v in vals if isinstance(v, (int, float))]
        if f["kind"] == "number" and f["better"] in ("high", "low") and len(nums) > 1 and len(set(nums)) > 1:
            target = max(nums) if f["better"] == "high" else min(nums)
            best = [i for i, v in enumerate(vals) if v == target]
        if f["kind"] == "bool" and len(cars) > 1 and any(vals) and not all(vals):
            best = [i for i, v in enumerate(vals) if v]
        rows.append({"key": k, "label": f["label"], "group": f["group"], "unit": f["unit"], "kind": f["kind"],
                     "dec": f["dec"], "values": vals, "best": best})
    return {"cars": [summary(c) for c in cars], "rows": rows}


@anvil.server.callable
def list_brands():
    ready()
    counts = {}
    for r in published():
        counts[r["make"]] = counts.get(r["make"], 0) + 1
    out = [{"id": b.get_id(), "name": b["name"], "country": b["country"] or "", "group": b["group_name"] or "",
            "founded": b["founded"], "website": b["website"] or "", "models": counts.get(b["name"], 0),
            "warranty": b["warranty"], "pt_warranty": b["pt_warranty"]} for b in app_tables.brands.search()]
    out.sort(key=lambda b: str(b["name"]).lower())
    return {"brands": out, "countries": sorted({b["country"] for b in out if b["country"]}),
            "total_models": sum(counts.values())}


@anvil.server.callable
def popular_picks(n=8):
    """The cars most often in people's five (names and counts only, never who)."""
    ready()
    counts: dict = {}
    rows: dict = {}
    for p in app_tables.picks.search():
        car = p["car"]
        if car is not None and (car["status"] or "published") == "published":
            cid = car.get_id()
            rows[cid] = car
            counts[cid] = counts.get(cid, 0) + 1
    top = sorted(counts.items(), key=lambda t: (-t[1], rows[t[0]]["make"]))[:max(1, min(int(n or 8), 20))]
    return [dict(summary(rows[cid]), count=c) for cid, c in top]
