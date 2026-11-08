# CarChoice

A car research tool for people who love spec sheets: every model in one full-width table with 44 filters, a shortlist of
five, ready-made searches on the marketplaces of your region, and a place to keep the listings you find with a check of
which one is priced well. Built on [Anvil](https://anvil.works) as native Anvil Forms (Python + HTML templates, a layout,
custom components, RepeatingPanels) with one JavaScript engine for the filter table.

- **App repo:** github.com/arkulinskis/carchoice (branch `master`). Anvil pulls `master`.
- **Live:** https://carchoice.anvil.app

## What it does

**Explore (everyone, no account needed)**
- The whole catalogue (268 models from 52 brands in the starter data) in one sortable, full-width table: sticky header and
  name column, a median row for whatever is filtered, compact rows, choose your columns, metric or imperial.
- 44 filters in a rail grouped as Basics, Price & ownership, Performance, Efficiency & EV, Size & space, Capability,
  Features, Market, Safety: range sliders with a histogram of what the other filters leave (and min/max boxes), choice
  lists with live counts (makes searchable), yes/no features. Filters without data say "No data yet".
- Active filters as removable chips; text search; the address holds the filters (copy the link to share them).
- "Search for these": turns the current filters into search words (model names when 6 or fewer match, otherwise
  descriptive words), your budget / mileage / year / place, and links to each marketplace of your region (their own search
  when the address is known, a Google site: search otherwise). "Most shortlisted" (anonymous counts).
- Star up to five cars; the tray at the bottom shows them (visitors' picks live in the browser and move into the account
  at sign-up). When five are picked, a dialog asks which to swap.
- Phone: the rail becomes a full-screen sheet, the table scrolls sideways, the tray scrolls.

**Car page** `#car/<id>`: key figures, every spec grouped with where the car ranks among all models, brand facts
(country, group, founded, US warranty, website), six similar models, Add to your five, Find for sale (marketplace searches
for that model, then Save a listing).

**Compare** `#compare`: the five side by side, best value per row marked (text "(best)", not only colour), "only rows that
differ", units switch.

**Members (free account)**
- **Your five** `#picks`: ranked cards with notes (save on leaving the box), move up/down, remove, Find for sale, Add a
  listing, listing count and the best price so far; search preferences (budget, currency, max km, year from, near, region).
- **Saved listings** `#listings[/<car id>]`: the links you found instead of bookmarks (title, price, currency, year,
  mileage, place, seller, notes, status Watching / Contacted / Seen it / Not for me / Bought). Price check: listings of the
  same model and currency are put on the same footing (12% value a year, 3% per 10,000 km) and compared: Good price /
  Fair price / Pricey, rank and a fair price estimate. Filter by car, sort by value, price, mileage.
- **Saved searches** `#searches`: named Explore filters to open, copy as a link, rename, delete.

**Reference pages**: Brands `#brands` (76 brands incl. ones without models yet; country, group, founded, warranty,
website, link to their models), Where to buy `#markets` (44 marketplaces, dealers, auctions and price guides in the US,
Canada, UK, Europe, Baltics and Australia, plus a "before you pay" checklist).

**Admin** `#admin/<tab>`
- **Car data**: import a CSV (file or pasted), "Check it first" preview (new cars, updates, new brands, new fields,
  problems per row), merge or add-only, where-it's-from note; every import in a log with "Remove the cars it added";
  download all data as CSV (same format, round-trips) or an empty template.
- **Cars**: search, hide/show on Explore, delete. **Fields**: label, group, unit, better-when, filter / default column;
  add a field. **Marketplaces**: add/edit/hide/delete (search address with `{q}`). **Data sources**: the wishlist of
  books, manuals and datasets to get (status Wishlist / Requested / Have it / Imported). Plus overview numbers, old
  feedback, users, demo data (fictional people whose fives feed "Most shortlisted").

**Data honesty**: the starter set is approximate (typical trim, manufacturers' published figures as known, model years
2024-2026; Europe-only prices converted from euros, ranges WLTP there). The app says so on the car page, landing, footer
and in the Terms. Official data replaces it through imports.

## Setting it up in Anvil (once)

1. Anvil editor: **Create app → Clone from GitHub**, paste `https://github.com/arkulinskis/carchoice`.
2. Check the **Users** service (email + password, Continue with Google, sign-up on).
3. Accept the **Schema Mismatch** alert with **"The schema of the source code is correct"**.
4. Run it, sign up with the admin email first, then **Publish**. The first visit loads the starter data (a few seconds).

<!-- libraries:start -->
## Libraries and outside services

What this project uses besides its own code. Generated by `APP_MAKER/tools/libraries.py`; to change it, edit `APP_MAKER/libraries/catalog.py` and re-run the script.

| Name | How it gets in | Used here for |
|---|---|---|
| [Google Fonts](https://fonts.google.com) | Loaded from a CDN | Hanken Grotesk, Schibsted Grotesk |

**Built into the browser:** localStorage, Clipboard.

**Anvil platform:** Anvil, Anvil Data Tables, Anvil JS bridge (anvil.js), Anvil Users, Anvil Google service, Anvil Media.

**Build and test tools (not shipped):** axe-core, Node.js, Headless Chrome (DevTools Protocol), PyYAML.

<!-- libraries:end -->

## Working on it

See `.claude/skills/carchoice/SKILL.md`. In short:

```
python tools/check.py                    # Anvil's validator, JS syntax, asset hashes, server tests -> ALL CHECKS PASSED
python -I tools/ui_test.py               # the real app in the Anvil App Server (Docker) driven by headless Chrome
python -I tools/ui_test.py --shots DIR   # + screenshots of every page (desktop/phone, light/dark, guest/member)
git push origin master                   # deploy
```

## Project layout

```
client_code/    startup.py, router.py, state.py, auth.py, legal.py, catalog.py (catalogue cache), picks.py (the five),
                prefs.py, queries.py (marketplace searches), fmt.py (units/money)
                Layouts/Shell, Pages/* (Landing, Explore, Car, Compare, Picks, Listings, Searches, Brands, Markets, Auth,
                Profile, Admin), AdminTabs/* (Data, Cars, Fields, Markets, Sources), Components/Explorer + HeroDemo,
                Items/*, Dialogs/*
server_code/    Cars.py (catalogue, car, compare, brands), Shortlist.py, Searches.py, Listings.py (+ price check),
                Markets.py, CarAdmin.py, Importer.py (CSV), Seed.py (fields, brands, marketplaces, sources), SeedCars.py
                (starter CSV), DemoData.py, Admin.py, Accounts.py, Feedback.py, common.py, SchemaCheck.py, legal_server.py
theme/assets/   cc-explore.js (filter table engine), cc-hero.js (landing example), app.css, app-kit.js, theme.css, icons
tools/          check.py, assets.py, ui_test.py + ui/ (flow, phone, admin, a11y, design, seed), testing/test_server.py
```
