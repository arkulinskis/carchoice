"""Read car data from CSV (the starter set and every admin upload) into the cars table.

    preview(text, mode)                          what an import would do, without changing anything
    run(text, filename, source, kind, who, mode) do it; returns the same summary plus the import's id

The format: one row per model, a header row, comma, semicolon or tab separated (Excel's "CSV UTF-8" works).
`make` and `model` are required. Headers are matched to fields by key, label or a few common names ("Horsepower",
"MSRP", "Transmission" ...). Any other column becomes a NEW field (filter + column) automatically, so official data
with extra measurements can come in without code changes. Empty cells never overwrite existing values (merge mode).
Short codes from the starter set (fuel P/H/E..., features "std 360 roof") are expanded.
"""
import csv
import datetime as dt
import io
import re
import unicodedata

from anvil.tables import app_tables

from . import common as C

MODES = ("merge", "add")
ALIASES = {
    "manufacturer": "make", "brand": "make", "marque": "make", "model_name": "model", "name": "model",
    "horsepower": "hp", "power": "hp", "power_hp": "hp", "bhp": "hp", "msrp": "price", "price_usd": "price",
    "base_price": "price", "torque_nm": "torque", "0_100": "zero100", "0_100_km_h": "zero100", "acceleration": "zero100",
    "transmission": "trans", "gearbox": "trans", "drivetrain": "drive", "drive_type": "drive", "fuel_type": "fuel",
    "range": "ev_range", "range_km": "ev_range", "electric_range": "ev_range", "battery_kwh": "battery",
    "seating": "seats", "seating_capacity": "seats", "cargo_l": "cargo", "trunk": "cargo", "boot": "cargo",
    "curb_weight": "weight", "weight_kg": "weight", "towing_kg": "towing", "length_mm": "length", "width_mm": "width",
    "height_mm": "height", "wheelbase_mm": "wheelbase", "ground_clearance": "ground", "displacement": "engine_l",
    "engine": "engine_l", "cylinders": "cyl", "body_type": "body", "segment": "size", "country": "origin",
    "euro_ncap": "ncap", "ncap_stars": "ncap", "fuel_l_100km": "l100", "l_100km": "l100", "consumption": "l100",
    "dc_charging": "dc_kw", "dc_charge_kw": "dc_kw",
}
VALUE_ALIASES = {
    "fuel": {"p": "Petrol", "petrol": "Petrol", "gasoline": "Petrol", "gas": "Petrol", "d": "Diesel", "diesel": "Diesel",
             "h": "Hybrid", "hybrid": "Hybrid", "hev": "Hybrid", "ph": "Plug-in hybrid", "phev": "Plug-in hybrid",
             "plug-in hybrid": "Plug-in hybrid", "e": "Electric", "ev": "Electric", "bev": "Electric",
             "electric": "Electric"},
    "trans": {"a": "Automatic", "auto": "Automatic", "automatic": "Automatic", "m": "Manual", "manual": "Manual",
              "cvt": "CVT", "dct": "Dual-clutch", "dual-clutch": "Dual-clutch", "1": "Single-speed",
              "single-speed": "Single-speed"},
    "regions": {"na": "North America", "north america": "North America", "eu": "Europe", "europe": "Europe",
                "uk": "UK", "au": "Australia", "australia": "Australia", "as": "Asia", "asia": "Asia"},
    "status": {"": "On sale", "on sale": "On sale", "d": "Discontinued", "discontinued": "Discontinued"},
}
ALL_REGIONS = ["North America", "Europe", "UK", "Australia", "Asia"]
FEATURE_TOKENS = {"std": ["carplay", "acc", "aeb"], "cp": ["carplay"], "acc": ["acc"], "aeb": ["aeb"], "row3": ["row3"],
                  "heatpump": ["heatpump"], "hud": ["hud"], "360": ["cam360"], "cam360": ["cam360"], "roof": ["roof"],
                  "man": ["manual"], "manual": ["manual"], "carplay": ["carplay"]}
SPECIAL = {"make", "model", "features", "notes", "source"}
TRUE = {"y", "yes", "true", "1", "x", "✓", "oui", "ja"}
FALSE = {"n", "no", "false", "0", "-", "non", "nein"}
MAX_ROWS = 5000


def norm_key(s):
    s = unicodedata.normalize("NFKD", str(s or "")).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "_", s).strip("_")


def slug(make, model):
    return norm_key(make + " " + model).replace("_", "-")


def number(raw):
    """'27,500' / '$27 500' / '12,5' / '6.1 s' -> float; '' -> None; junk -> ValueError."""
    s = str(raw).strip()
    if not s:
        return None
    s = s.replace(" ", " ")
    if re.fullmatch(r"-?\d+,\d{1,2}", s):  # European decimal comma
        s = s.replace(",", ".")
    s = s.replace(",", "").replace(" ", "")
    m = re.search(r"-?\d+(\.\d+)?", s)
    if not m:
        raise ValueError(raw)
    v = float(m.group(0))
    return int(v) if v == int(v) else v


def _rows(text):
    text = (text or "").lstrip("﻿")
    sample = text[:4000]
    delim = ","
    if sample.count("\t") > sample.count(",") and sample.count("\t") > sample.count(";"):
        delim = "\t"
    elif sample.count(";") > sample.count(","):
        delim = ";"
    return [r for r in csv.reader(io.StringIO(text), delimiter=delim) if any(c.strip() for c in r)]


def _fields():
    return {r["key"]: r for r in app_tables.car_fields.search()}


def _brands():
    return {norm_key(r["name"]): r for r in app_tables.brands.search()}


def _guess_kind(values):
    vals = [str(v).strip() for v in values if str(v).strip()]
    if not vals:
        return "text"
    if all(v.lower() in TRUE | FALSE for v in vals):
        return "bool"
    try:
        for v in vals:
            number(v)
        return "number"
    except ValueError:
        pass
    distinct = set(v.lower() for v in vals)
    if len(distinct) <= 30 and len(distinct) <= max(3, len(vals) // 2):
        return "choice"
    return "text"


def _map_header(header, fields):
    """Header cells -> field keys. Unknown ones get a new key (created on import)."""
    by_label = {norm_key(f["label"]): k for k, f in fields.items()}
    out = []
    for h in header:
        k = norm_key(h)
        if k in fields or k in SPECIAL:
            out.append(k)
        elif k in ALIASES:
            out.append(ALIASES[k])
        elif k in by_label:
            out.append(by_label[k])
        else:
            out.append(k or None)
    return out


def _value(kind, key, raw):
    s = str(raw).strip()
    amap = VALUE_ALIASES.get(key, {})
    if kind == "number":
        return number(s)
    if kind == "bool":
        if not s:
            return None
        if s.lower() in TRUE:
            return True
        if s.lower() in FALSE:
            return False
        raise ValueError(raw)
    if kind == "multi":
        if not s:
            return None
        if key == "regions" and s.upper() == "ALL":
            return list(ALL_REGIONS)
        parts = [p.strip() for p in re.split(r"[/;|]", s) if p.strip()]
        out = []
        for p in parts:
            v = amap.get(p.lower(), p)
            if v not in out:
                out.append(v)
        return out
    if kind == "choice":
        if key in amap or s.lower() in amap:
            return amap.get(s.lower(), s) or None
        return s or None
    return s[:400] or None


def parse(text):
    """-> {cars: [{make, model, slug, specs, notes}], new_fields: {key: {label, kind}}, errors: [...], total}"""
    rows = _rows(text)
    if len(rows) < 2:
        return {"cars": [], "new_fields": {}, "errors": ["The file needs a header row and at least one car."], "total": 0}
    fields = _fields()
    header = rows[0]
    keys = _map_header(header, fields)
    if "make" not in keys or "model" not in keys:
        return {"cars": [], "new_fields": {}, "errors": ["Columns 'make' and 'model' are required (found: %s)."
                                                         % ", ".join(header[:12])], "total": len(rows) - 1}
    body = rows[1:MAX_ROWS + 1]
    errors = []
    if len(rows) - 1 > MAX_ROWS:
        errors.append("Only the first %d rows are read in one import." % MAX_ROWS)
    new_fields = {}
    for i, k in enumerate(keys):
        if k and k not in fields and k not in SPECIAL and k not in new_fields:
            new_fields[k] = {"label": C.text(header[i], 60) or k, "kind": _guess_kind(r[i] for r in body if i < len(r))}
    kinds = {k: f["kind"] for k, f in fields.items()}
    kinds.update({k: f["kind"] for k, f in new_fields.items()})
    brands = _brands()
    cars, seen = [], {}
    for n, r in enumerate(body, start=2):
        if len(r) > len(keys) and any(c.strip() for c in r[len(keys):]):
            errors.append("Row %d has more cells than the header (%d > %d): check for an unquoted comma." % (n, len(r), len(keys)))
            continue
        cell = {k: (r[i] if i < len(r) else "") for i, k in enumerate(keys) if k}
        make, model = C.text(cell.get("make"), 60), C.text(cell.get("model"), 80)
        if not make or not model:
            errors.append("Row %d: make and model are required." % n)
            continue
        brand = brands.get(norm_key(make))
        if brand is not None:
            make = brand["name"]
        specs: dict = {"make": make, "model": model}
        for k, raw in cell.items():
            if k in SPECIAL or not str(raw).strip():
                continue
            try:
                v = _value(kinds.get(k, "text"), k, raw)
            except ValueError:
                errors.append("Row %d: %s '%s' isn't a %s." % (n, k, C.text(raw, 30),
                                                              "number" if kinds.get(k) == "number" else "yes/no"))
                continue
            if v is not None and v != []:
                specs[k] = v
        for tok in re.split(r"[\s,;/]+", str(cell.get("features") or "").strip().lower()):
            for key in FEATURE_TOKENS.get(tok, []):
                specs[key] = True
            if tok and tok not in FEATURE_TOKENS:
                errors.append("Row %d: unknown feature code '%s'." % (n, C.text(tok, 20)))
        # facts that follow from others
        if "Manual" in (specs.get("trans") or []):
            specs["manual"] = True
        if isinstance(specs.get("seats"), (int, float)) and specs["seats"] >= 7:
            specs["row3"] = True
        if "status" in kinds and "status" not in specs and "status" in cell:
            specs["status"] = "On sale"
        if brand is not None:
            if brand["country"] and "origin" not in specs:
                specs["origin"] = brand["country"]
            if brand["warranty"] and "warranty" not in specs:
                specs["warranty"] = brand["warranty"]
            if brand["pt_warranty"] and "pt_warranty" not in specs:
                specs["pt_warranty"] = brand["pt_warranty"]
        s = slug(make, model)
        if s in seen:
            errors.append("Row %d: %s %s appears twice in the file (row %d is used)." % (n, make, model, seen[s]))
            continue
        seen[s] = n
        cars.append({"make": make, "model": model, "slug": s, "specs": specs,
                     "notes": C.text(cell.get("notes"), 400), "source": C.text(cell.get("source"), 200)})
    return {"cars": cars, "new_fields": new_fields, "errors": errors[:60] + (["... and %d more problems" % (len(errors) - 60)]
                                                                          if len(errors) > 60 else []),
            "total": len(body)}


def preview(text, mode="merge"):
    p = parse(text)
    existing = {r["slug"] for r in app_tables.cars.search()}
    new = [c for c in p["cars"] if c["slug"] not in existing]
    upd = [c for c in p["cars"] if c["slug"] in existing]
    makes = sorted({c["make"] for c in new})
    known = _brands()
    return {"rows": p["total"], "readable": len(p["cars"]), "new": len(new), "updates": len(upd) if mode == "merge" else 0,
            "skipped": len(upd) if mode == "add" else 0, "new_makes": [m for m in makes if norm_key(m) not in known],
            "new_fields": [{"key": k, "label": f["label"], "kind": f["kind"]} for k, f in p["new_fields"].items()],
            "errors": p["errors"], "sample": ["%s %s" % (c["make"], c["model"]) for c in p["cars"][:6]]}


def run(text, filename="", source="", kind="csv", who=None, mode="merge"):
    mode = mode if mode in MODES else "merge"
    p = parse(text)
    summary = preview(text, mode)
    if not p["cars"]:
        return dict(summary, ok=False)
    stamp = C.now()
    imp = app_tables.imports.add_row(who=who, created=stamp, filename=C.text(filename, 120) or "Pasted data",
                                     kind=kind, source=C.text(source, 200), added=0, updated=0,
                                     notes="; ".join(summary["errors"][:5]), status="active")
    fields = _fields()
    order = max([f["sort"] or 0 for f in fields.values()] + [0])
    for k, f in p["new_fields"].items():
        order += 10
        app_tables.car_fields.add_row(key=k, label=f["label"], grp="Imported", kind=f["kind"], unit="", decimals=1 if f["kind"] == "number" else 0,
                                      filter=True, show=False, sort=order, help="Added by the import of %s." % (filename or "pasted data"),
                                      better="")
    known = _brands()
    for c in p["cars"]:
        if norm_key(c["make"]) not in known:
            known[norm_key(c["make"])] = app_tables.brands.add_row(name=c["make"], country="", group_name="", founded=None,
                                                                    website="", warranty=None, pt_warranty=None,
                                                                    notes="Added by an import")
    existing = {r["slug"]: r for r in app_tables.cars.search()}
    added = updated = 0
    for c in p["cars"]:
        row = existing.get(c["slug"])
        src = c["source"] or C.text(source, 200)
        if row is None:
            app_tables.cars.add_row(make=c["make"], model=c["model"], slug=c["slug"], specs=c["specs"], notes=c["notes"],
                                    source=src, import_ref=imp, status="published", created=stamp, updated=stamp)
            added += 1
        elif mode == "merge":
            specs = dict(row["specs"] or {})
            specs.update(c["specs"])
            row.update(specs=specs, notes=c["notes"] or row["notes"], source=src or row["source"], updated=stamp)
            updated += 1
    imp.update(added=added, updated=updated)
    bump()
    return dict(summary, ok=True, id=imp.get_id(), added=added, updated=updated)


def bump():
    """A new catalogue version: browsers that cached the old one fetch it again."""
    C.set_setting("catalog_v", dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d%H%M%S%f"))
