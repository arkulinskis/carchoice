"""Admin tools for the car data: preview and run CSV imports, undo an import, download everything as CSV, hide or
delete single cars, edit the field list (labels, groups, which are filters/columns), and the data-source wishlist."""
import csv
import io

import anvil.server
from anvil.tables import app_tables

from . import common as C
from . import Cars, Importer, Seed

KINDS = ["number", "choice", "multi", "bool", "text"]
SOURCE_KINDS = ["Dataset", "Book", "Manual", "Brochure", "Magazine", "Website", "Other"]
SOURCE_STATUSES = ["Wishlist", "Requested", "Have it", "Imported"]


def _text_of(file_or_text):
    if isinstance(file_or_text, str):
        return file_or_text
    data = file_or_text.get_bytes() if hasattr(file_or_text, "get_bytes") else b""
    for enc in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            return data.decode(enc)
        except UnicodeDecodeError:
            continue
    return ""


@anvil.server.callable(require_user=True)
def admin_import_preview(file_or_text, mode="merge"):
    C.require_admin()
    Seed.ensure_seeded()
    text = _text_of(file_or_text)
    if not text.strip():
        return C.fail("The file is empty (or not a text/CSV file).")
    return C.ok(preview=Importer.preview(text, mode))


@anvil.server.callable(require_user=True)
def admin_import(file_or_text, filename="", source="", mode="merge"):
    me = C.require_admin()
    Seed.ensure_seeded()
    text = _text_of(file_or_text)
    if not text.strip():
        return C.fail("The file is empty (or not a text/CSV file).")
    r = Importer.run(text, filename=filename or getattr(file_or_text, "name", "") or "Pasted data",
                     source=source, kind="csv", who=me, mode=mode)
    if not r.get("ok"):
        return C.fail((r.get("errors") or ["No cars could be read from that file."])[0])
    return C.ok(result=r)


def _imp(r):
    return {"id": r.get_id(), "created": C.iso(r["created"]), "filename": r["filename"] or "", "kind": r["kind"] or "",
            "source": r["source"] or "", "added": r["added"] or 0, "updated": r["updated"] or 0, "notes": r["notes"] or "",
            "status": r["status"] or "active", "who": C.name_of(r["who"]) if r["who"] is not None else "CarChoice",
            "still_here": len(app_tables.cars.search(import_ref=r))}


@anvil.server.callable(require_user=True)
def admin_imports():
    C.require_admin()
    rows = sorted(app_tables.imports.search(), key=lambda r: C.iso(r["created"]) or "", reverse=True)
    return C.ok(imports=[_imp(r) for r in rows])


def _drop_car(car):
    for p in app_tables.picks.search(car=car):
        p.delete()
    for li in app_tables.listings.search(car=car):
        li["car"] = None  # the member keeps their link
    car.delete()


@anvil.server.callable(require_user=True)
def admin_undo_import(import_id):
    """Remove the cars this import ADDED (changes it made to existing cars stay)."""
    C.require_admin()
    imp = C.row_by_id(app_tables.imports, import_id)
    if imp is None:
        return C.fail("That import no longer exists.")
    n = 0
    for car in app_tables.cars.search(import_ref=imp):
        _drop_car(car)
        n += 1
    imp.update(status="undone")
    Importer.bump()
    return C.ok(removed=n)


@anvil.server.callable(require_user=True)
def admin_export_csv(template=False):
    """All cars as CSV text (same format as the importer reads), or just the header row."""
    C.require_admin()
    Seed.ensure_seeded()
    flds = [f for f in Cars.fields() if f["key"] not in ("make", "model")]
    out = io.StringIO()
    w = csv.writer(out, lineterminator="\n")
    w.writerow(["make", "model"] + [f["key"] for f in flds] + ["notes", "source"])
    if not template:
        for r in sorted(app_tables.cars.search(), key=lambda r: (r["make"], r["model"])):
            s = r["specs"] or {}
            row = [r["make"], r["model"]]
            for f in flds:
                v = s.get(f["key"])
                if isinstance(v, list):
                    v = "/".join(str(x) for x in v)
                elif v is True:
                    v = "yes"
                elif v is False:
                    v = "no"
                row.append("" if v is None else v)
            w.writerow(row + [r["notes"] or "", r["source"] or ""])
    return C.ok(csv=out.getvalue(), filename="carchoice-template.csv" if template else "carchoice-cars.csv")


@anvil.server.callable(require_user=True)
def admin_cars(query=""):
    C.require_admin()
    q = C.text(query, 60).lower()
    rows = sorted(app_tables.cars.search(), key=lambda r: (r["make"], r["model"]))
    if q:
        rows = [r for r in rows if q in ("%s %s %s" % (r["make"], r["model"], r["source"] or "")).lower()]
    return C.ok(cars=[{"id": r.get_id(), "name": "%s %s" % (r["make"], r["model"]), "source": r["source"] or "",
                       "status": r["status"] or "published", "updated": C.iso(r["updated"]),
                       "fields": len(r["specs"] or {})} for r in rows[:150]], total=len(rows))


@anvil.server.callable(require_user=True)
def admin_car_status(car_id, status):
    C.require_admin()
    r = C.row_by_id(app_tables.cars, car_id)
    if r is None:
        return C.fail("That car no longer exists.")
    if status not in ("published", "hidden"):
        return C.fail("Unknown status.")
    r.update(status=status, updated=C.now())
    Importer.bump()
    return C.ok()


@anvil.server.callable(require_user=True)
def admin_delete_car(car_id):
    C.require_admin()
    r = C.row_by_id(app_tables.cars, car_id)
    if r is not None:
        _drop_car(r)
        Importer.bump()
    return C.ok()


@anvil.server.callable(require_user=True)
def admin_fields():
    C.require_admin()
    Seed.ensure_seeded()
    counts: dict = {}
    for r in app_tables.cars.search():
        for k, v in (r["specs"] or {}).items():
            if v not in (None, "", []):
                counts[k] = counts.get(k, 0) + 1
    out = [dict(f, cars=counts.get(f["key"], 0)) for f in Cars.fields()]
    return C.ok(fields=out, kinds=KINDS, groups=sorted({f["group"] for f in out}))


@anvil.server.callable(require_user=True)
def admin_save_field(key, data):
    C.require_admin()
    if not isinstance(data, dict):
        return C.fail("That didn't make sense.")
    key = Importer.norm_key(key)
    if not key:
        return C.fail("A field needs a key (letters and digits).")
    label = C.text(data.get("label"), 60)
    if len(label) < 1:
        return C.fail("Give the field a label.")
    kind = data.get("kind") if data.get("kind") in KINDS else "text"
    values: dict = dict(label=label, grp=C.text(data.get("group"), 40) or "Other", unit=C.text(data.get("unit"), 16),
                  filter=bool(data.get("filter")), show=bool(data.get("show")), help=C.text(data.get("help"), 300),
                  better=data.get("better") if data.get("better") in ("high", "low") else "")
    row = app_tables.car_fields.get(key=key)
    if row is None:
        order = max([r["sort"] or 0 for r in app_tables.car_fields.search()] + [0]) + 10
        row = app_tables.car_fields.add_row(key=key, kind=kind, decimals=1 if kind == "number" else 0, sort=order, **values)
    else:
        if key in ("make", "model"):
            values["filter"], values["show"] = row["filter"], True
        row.update(**values)
    Importer.bump()
    return C.ok()


def _src(r):
    return {"id": r.get_id(), "title": r["title"], "kind": r["kind"] or "", "publisher": r["publisher"] or "",
            "year": r["year"], "url": r["url"] or "", "status": r["status"] or "Wishlist", "notes": r["notes"] or ""}


@anvil.server.callable(require_user=True)
def admin_sources():
    C.require_admin()
    Seed.ensure_seeded()
    order = {s: i for i, s in enumerate(SOURCE_STATUSES)}
    rows = sorted(app_tables.sources.search(), key=lambda r: (order.get(r["status"] or "", 9), r["title"].lower()))
    return C.ok(sources=[_src(r) for r in rows], kinds=SOURCE_KINDS, statuses=SOURCE_STATUSES)


@anvil.server.callable(require_user=True)
def admin_save_source(data):
    C.require_admin()
    if not isinstance(data, dict):
        return C.fail("That didn't make sense.")
    title = C.text(data.get("title"), 160)
    if len(title) < 2:
        return C.fail("Give the source a title.")
    url = C.text(data.get("url"), 400)
    if url and not url.startswith(("http://", "https://")):
        return C.fail("Links need a full address starting with https://.")
    year = data.get("year")
    try:
        year = int(year) if year not in (None, "") else None
    except (TypeError, ValueError):
        return C.fail("The year needs to be a number.")
    values: dict = dict(title=title, url=url, year=year, publisher=C.text(data.get("publisher"), 120),
                  notes=C.text(data.get("notes"), 1000, multiline=True),
                  kind=data.get("kind") if data.get("kind") in SOURCE_KINDS else "Other",
                  status=data.get("status") if data.get("status") in SOURCE_STATUSES else "Wishlist")
    row = C.row_by_id(app_tables.sources, data.get("id")) if data.get("id") else None
    if row is None:
        row = app_tables.sources.add_row(created=C.now(), **values)
    else:
        row.update(**values)
    return C.ok(source=_src(row))


@anvil.server.callable(require_user=True)
def admin_delete_source(source_id):
    C.require_admin()
    row = C.row_by_id(app_tables.sources, source_id)
    if row is not None:
        row.delete()
    return C.ok()
