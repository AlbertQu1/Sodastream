# sodastream-analytics

Cost and ROI tracking for home sparkling water carbonation: cost per liter, savings vs. market reference price, and equipment payback period, with support for flavor syrups.

## Project status

✅ First working version complete. Run `python source/main.py` for a full report: total savings, ROI per equipment (previous vs. current), yearly breakdown, and flavor breakdown.

Requires a `.env` with your credentials (see `.env.example`).

## Data model

The project reads from the shared `casa` Postgres database, `soda_stream` schema — the same one [Soda Stream Logger](https://github.com/AlbertQu1/Loggers/tree/master/Soda%20Stream%20Logger) (the capture PWA) writes to. `data_loader.py` connects via SQLAlchemy with `search_path=soda_stream`, so every unqualified table name below resolves there:

- **`soda_preparations`** — one row per pour: shots per intensity (light/medium/strong), bottles prepared, flavor + ml used, cylinder
- **`soda_legacy_consumption`** — one-time migration artifact: manual-era pours from before real shot-intensity tracking existed (date/cylinder/flavor/bottle-count only, no shots)
- **`soda_cylinders`** — CO2 tank purchase → open → close lifecycle, `price` per refill (includes cylinders with $0 cost, the ones bundled with the equipment)
- **`soda_flavors`** — syrup catalog + purchase history (name, brand, cost, ml, purchase date), includes an `always_available` flag for flavors with no real cost to track (e.g. fresh-squeezed lemon)
- **`soda_market_benchmarks`** — external market reference price by segment, updated yearly

Equipment cost, purchase dates, and resale value are tracked in `source/params.py`, not in a spreadsheet — they change rarely enough that a full table would be overkill.

## Structure

```
source/
├── config.py         # loads .env variables
├── data_loader.py     # reads from casa.soda_stream (Postgres)
├── cleaning.py          # normalizes types, parses intensity
├── params.py             # equipment cost/dates
├── calculations.py         # cylinder cost, syrup cost, savings, ROI
├── report.py                 # prints formatted results
└── main.py                    # runs the full pipeline
```

## Business logic notes

- **Cylinder cost across years**: when a cylinder's usage spans two calendar years, its refill cost is allocated proportionally to liters consumed in each year (not charged fully to one year).
- **Syrup cost**: calculated from the most recent purchase price per flavor (`soda_flavors`), so repurchasing a flavor doesn't duplicate rows.
- **Flavors without purchase history** (e.g. natural lemon) automatically cost $0 — they simply don't match anything in `soda_flavors`' purchase history, no special-case code needed.
- **Intensity** (light/medium/strong) is captured as a comma-separated string (e.g. `S,S` or `S,L`) to support the new equipment's multi-shot mode. `-` marks events where intensity wasn't tracked (old manual equipment). Parsing is case-insensitive.
- **Equipment ROI** is tracked separately per equipment (previous vs. current), based on purchase/end dates in `params.py`.
- **Equipment resale**: when the previous equipment is sold, update `PREVIOUS_EQUIPMENT_SALE_MXN` in `params.py`. If a charged CO2 cylinder is sold along with it, its value should also be counted as recovered — otherwise that gas cost gets counted twice (once as your own operating cost, once given away for free in the sale). Use `PREVIOUS_EQUIPMENT_SALE_CYLINDER_VALUE_MXN` for that case.

## Migration status

Done — this used to run against Google Sheets, then migrated to a self-hosted Postgres database, and finally got its own dedicated capture PWA ([Soda Stream Logger](https://github.com/AlbertQu1/Loggers/tree/master/Soda%20Stream%20Logger), same architecture as Coffee Logger: mobile-first, direct capture of flavor/ml/cylinder/intensity, no manual spreadsheet entry). All three phases of the original roadmap are complete.

Because `data_loader.py` was always the only module aware of the data source, each migration only required changing that one file — `cleaning.py`, `calculations.py`, and `report.py` never needed to change.

This repo (`sodastream-analytics`, aka "Gasificador") stays the **read-only analytics side** — cost/ROI/savings reporting — separate from the Logger app, which owns writes.