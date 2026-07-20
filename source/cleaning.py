import pandas as pd
from collections import Counter

def parse_intensity(text:str) -> dict:
    if not text or pd.isna(text) or str(text).strip() =="-":
        return {"light": 0, "medium": 0, "strong": 0}
    
    labels = {"L": "light", "M": "medium", "S": "strong"}
    shots = [s.strip().upper() for s in str(text).split(",")]
    counts = Counter(shots)

    return {labels[k]: counts.get(k,0) for k in labels}

def clean_consumption(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [c.strip().lower() for c in df.columns]

    df["fecha"] = pd.to_datetime(df["fecha"], format="%d/%m/%y", errors="coerce")
    df["anio"] = df["fecha"].dt.year

    df["consumo"] = pd.to_numeric(df["consumo"], errors="coerce").fillna(0)
    df["cilindro_id"] = df["cilindro_id"].str.strip().str.upper()

    df["sabor_id"] = pd.to_numeric(df["sabor_id"], errors="coerce").fillna(0).astype(int)
    df["ml"] = pd.to_numeric(df["ml"], errors="coerce").fillna(0)

    intensity_parsed = df["intensidad"].apply(parse_intensity)
    df["shots_light"] = intensity_parsed.apply(lambda x: x["light"])
    df["shots_medium"] = intensity_parsed.apply(lambda x: x["medium"])
    df["shots_strong"] = intensity_parsed.apply(lambda x: x["strong"])

    if "#" in df.columns:
        duplicates = df["#"].duplicated().sum()
        if duplicates > 0:
            print (f"⚠️  Warning: {duplicates} duplicate event IDs found in '#' column")
    return df

def clean_refills(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [c.strip().lower() for c in df.columns]
    df["tanque"] = df["tanque"].str.strip().str.upper()
    df["costo"] = pd.to_numeric(df["costo"], errors="coerce").fillna(0)
    return df

def clean_flavors(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [c.strip().lower() for c in df.columns]
    df.rename(columns={"id": "sabor_id"}, inplace=True)
    df["sabor"] = df["sabor"].str.strip().str.lower()
    return df

def clean_market(df: pd.DataFrame) -> pd.DataFrame:
    df= df.copy()
    df.columns = [c.strip().lower() for c in df.columns]
    df["segmento"] =df["segmento"].str.strip().str.lower()
    df["marca"] = df["marca"].str.strip().str.lower()
    return df

def clean_flavor_history(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns =[c.strip().lower() for c in df.columns]
    df["id"] = pd.to_numeric(df["id"], errors="coerce")
    df["costo"] = pd.to_numeric(df["costo"], errors="coerce")
    df["ml"] = pd.to_numeric(df["ml"], errors="coerce")
    df["fecha"] = pd.to_datetime(df["fecha"], dayfirst=True, errors="coerce")
    df = df.sort_values("fecha")
    df["costo_por_ml"] = df["costo"] / df["ml"]
    return df

def clean_all (raw: dict) -> dict:
    return{
        "consumption": clean_consumption(raw["consumption"]),
        "refills": clean_refills(raw["refills"]),
        "flavors": clean_flavors(raw["flavors"]),
        "market": clean_market(raw["market"]),
        "flavor_history": clean_flavor_history(raw["flavor_history"])
    }