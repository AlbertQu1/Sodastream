import pandas as pd
from config import SHEET_URL, GID_CONSUMPTION, GID_REFILLS, GID_FLAVORS, GID_MARKET, GID_FLAVOR_HISTORY

def _load_gid(gid:str) -> pd.DataFrame:
    return pd.read_csv(f"{SHEET_URL}&gid={gid}")

def load_consumption() -> pd.DataFrame:
    return _load_gid(GID_CONSUMPTION)

def load_refills() -> pd.DataFrame:
    return _load_gid(GID_REFILLS)

def load_flavors() -> pd.DataFrame:
    return _load_gid(GID_FLAVORS)

def load_market() -> pd.DataFrame:
    return _load_gid(GID_MARKET)

def load_flavor_history() -> pd.DataFrame:
    return _load_gid(GID_FLAVOR_HISTORY)

def load_all() -> dict:
    return {
        "consumption": load_consumption(),
        "refills": load_refills(),
        "flavors": load_flavors(),
        "market": load_market(),
        "flavor_history": load_flavor_history()
    }