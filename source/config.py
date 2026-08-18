import os 
from dotenv import load_dotenv

load_dotenv()

def _get_required(key: str) -> str:
    value = os.environ.get(key)
    if value is None:
        raise ValueError(f"Missing required environment variable: {key}")
    return value

PG_HOST = _get_required("PGHOST")
PG_PORT = os.environ.get("PGPORT", "5432")
PG_DATABASE = _get_required("PGDATABASE")
PG_USER = _get_required("PGUSER")
PG_PASSWORD = _get_required("PGPASSWORD")
CASA_LUGAR_UUID = _get_required("CASA_LUGAR_UUID")