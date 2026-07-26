# sodastream-analytics

Cost and ROI tracking for home sparkling water carbonation: cost per liter, savings vs. market reference price, and equipment payback period, with support for flavor syrups.

## Project status

✅ First working version complete. Run `python source/main.py` for a full report: total savings, ROI per equipment (previous vs. current), yearly breakdown, and flavor breakdown.

Requires a `.env` with your credentials (see `.env.example`).

## Data model

The project pulls from a Google Sheets database with these tables:

- **Consumption** — daily log: date, amount, flavor_id, ml, cylinder_id, intensity (light/medium/strong, comma-separated)
- **Refills** — cost of each cylinder refill (includes cylinders with $0 cost, the ones bundled with the equipment)
- **Flavor_id** — flavor catalog, includes `0 = plain water` as the base category
- **Flavor_history** — syrup purchases: date, cost, size
- **Prices** — external market benchmark by segment, updated yearly

Equipment cost, purchase dates, and resale value are tracked in `source/params.py`, not in a spreadsheet — they change rarely enough that a full table would be overkill.

## Structure

```
source/
├── config.py         # loads .env variables
├── data_loader.py     # reads raw data from Google Sheets
├── cleaning.py          # normalizes types, parses intensity
├── params.py             # equipment cost/dates
├── calculations.py         # cylinder cost, syrup cost, savings, ROI
├── report.py                 # prints formatted results
└── main.py                    # runs the full pipeline
```

## Business logic notes

- **Cylinder cost across years**: when a cylinder's usage spans two calendar years, its refill cost is allocated proportionally to liters consumed in each year (not charged fully to one year).
- **Syrup cost**: calculated from the most recent purchase price per flavor (`flavor_history`), so repurchasing a flavor doesn't duplicate rows.
- **Flavors without purchase history** (e.g. natural lemon) automatically cost $0 — they simply don't match anything in `flavor_history`, no special-case code needed.
- **Intensity** (light/medium/strong) is captured as a comma-separated string (e.g. `S,S` or `S,L`) to support the new equipment's multi-shot mode. `-` marks events where intensity wasn't tracked (old manual equipment). Parsing is case-insensitive.
- **Equipment ROI** is tracked separately per equipment (previous vs. current), based on purchase/end dates in `params.py`.
- **Equipment resale**: when the previous equipment is sold, update `PREVIOUS_EQUIPMENT_SALE_MXN` in `params.py`. If a charged CO2 cylinder is sold along with it, its value should also be counted as recovered — otherwise that gas cost gets counted twice (once as your own operating cost, once given away for free in the sale). Use `PREVIOUS_EQUIPMENT_SALE_CYLINDER_VALUE_MXN` for that case.

## Future direction

The long-term goal is to replace manual Google Sheets capture with a PWA (installable web app), following the same pattern built for Coffee Analytics:

1. **Now** — Google Sheets as the data source, manual capture
2. **Next** — migrate to a self-hosted Postgres database (`data_loader.py` is the only file that changes)
3. **Final** — a PWA for direct capture (flavor, ml, cylinder, intensity as light/medium/strong), offline-first via Service Worker + IndexedDB, syncing to Postgres through an n8n webhook when back online

Because `data_loader.py` is the only module aware of the data source, each phase only requires changing that one file — `cleaning.py`, `calculations.py`, and `report.py` stay untouched.