import os 
from dotenv import load_dotenv

load_dotenv()

def _get_required(key: str) -> str:
    value = os.environ.get(key)
    if value is None:
        raise ValueError(f"Missing required environment variable: {key}")
    return value

SHEET_URL = _get_required("SODASTREAM_SHEET_URL")
GID_CONSUMPTION = _get_required("GID_CONSUMPTION")
GID_REFILLS = _get_required("GID_REFILLS")
GID_FLAVORS = _get_required("GID_FLAVORS")
GID_MARKET = _get_required("GID_MARKET")
GID_FLAVOR_HISTORY = _get_required("GID_FLAVOR_HISTORY")