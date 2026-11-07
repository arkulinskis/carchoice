"""Demo content, so the app never looks empty: a few clearly fictional people whose shortlists feed "Most shortlisted"
on Explore (only names of cars and counts are ever shown, never who picked them).

Loaded automatically the first time anyone opens the app (ensure_loaded), removed or reloaded from Admin -> Demo data.
Removing it is remembered. Demo users have is_demo=True and @example.com emails; they can't sign in (no password).
The car catalogue itself is NOT demo data (it's the starter import; see Seed.py).
"""
import datetime as dt

from anvil.tables import app_tables

from . import common as C

DEMO_USERS = [
    ("Maya Chen", "maya.demo@example.com", ["toyota-rav4", "honda-cr-v", "mazda-cx-5", "hyundai-tucson", "kia-sportage"]),
    ("Theo Martin", "theo.demo@example.com", ["tesla-model-y", "hyundai-ioniq-5", "kia-ev6", "skoda-enyaq", "toyota-rav4"]),
    ("Ines Ozola", "ines.demo@example.com", ["skoda-octavia", "toyota-corolla", "volkswagen-golf", "mazda-mazda3"]),
    ("Sam Okafor", "sam.demo@example.com", ["kia-telluride", "toyota-sienna", "honda-odyssey", "hyundai-palisade", "kia-carnival"]),
    ("Lea Novak", "lea.demo@example.com", ["toyota-rav4", "subaru-forester", "honda-cr-v", "mazda-cx-50"]),
    ("Ravi Patel", "ravi.demo@example.com", ["ford-maverick", "toyota-tacoma", "hyundai-santa-cruz"]),
    ("Ana Lopes", "ana.demo@example.com", ["tesla-model-3", "hyundai-ioniq-6", "toyota-rav4", "bmw-i4", "polestar-2"]),
]
DEMO_TABLES = ["picks"]  # tables holding demo rows (each has is_demo). Children before parents.


def state():
    return C.get_setting("demo", "never")  # "never" | "loaded" | "removed"


def ensure_loaded():
    if state() == "never":
        load()


def load():
    from . import Seed
    Seed.ensure_seeded()
    remove(remember=False)
    cars = {r["slug"]: r for r in app_tables.cars.search()}
    for name, email, slugs in DEMO_USERS:
        u = app_tables.users.get(email=email) or app_tables.users.add_row(email=email, enabled=False)
        u.update(display_name=name, is_demo=True, signed_up=C.now() - dt.timedelta(days=30))
        rank = 0
        for s in slugs:
            if s in cars:
                rank += 1
                app_tables.picks.add_row(user=u, car=cars[s], rank=rank, note="", is_demo=True,
                                         created=C.now() - dt.timedelta(days=rank))
    C.set_setting("demo", "loaded")
    return counts()


def remove(remember=True):
    for name in DEMO_TABLES:
        for r in getattr(app_tables, name).search(is_demo=True):
            r.delete()
    for u in app_tables.users.search(is_demo=True):
        u.delete()
    if remember:
        C.set_setting("demo", "removed")
    return counts()


def counts():
    out = {"users": len(app_tables.users.search(is_demo=True))}
    for name in DEMO_TABLES:
        out[name] = len(getattr(app_tables, name).search(is_demo=True))
    return out
