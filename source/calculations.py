import pandas as pd
import params

def calculate_cylinder_cost_by_year(consumption: pd.DataFrame, refills: pd.DataFrame) -> pd.DataFrame:
    by_year = (
        consumption.groupby(["cilindro_id", "anio"])["consumo"]
        .sum()
        .reset_index()
        .rename(columns={"consumo": "litros_anio"})
    )

    by_cylinder_total = (
        consumption.groupby("cilindro_id")["consumo"]
        .sum()
        .reset_index()
        .rename(columns={"consumo": "litros_totales_cilindro"})
    )

    result = by_year.merge(by_cylinder_total, on="cilindro_id", how="left")

    result["proporcion"] = result["litros_anio"] / result["litros_totales_cilindro"]
    result = result.merge(
        refills[["tanque", "costo"]],
        left_on= "cilindro_id",
        right_on= "tanque",
        how= "left"
    )
    result = result.drop(columns=["tanque"])
    result["costo"] = result["costo"].fillna(0)

    result["costo_prorrateado"] = result["costo"] * result["proporcion"]
    result["costo_por_litro"] = result["costo_prorrateado"] / result["litros_anio"]

    return result

def calculate_cost_per_liter(consumption: pd.DataFrame, cylinder_cost: pd.DataFrame) -> pd.DataFrame:
    result = consumption.merge(
        cylinder_cost[["cilindro_id", "anio", "costo_por_litro"]],
        on= ["cilindro_id", "anio"],
        how= "left"
    )
    result["costo_por_litro"] = result["costo_por_litro"].fillna(0)
    result["costo_agua_evento"] = result["costo_por_litro"] * result["consumo"]

    result["#"] = result["#"].astype(int)
    result["anio"] = result["anio"].astype(int)
    result["consumo"] = result["consumo"].astype(int)

    return result

def calculate_syrup_cost(consumption_with_cost: pd.DataFrame, flavor_history: pd.DataFrame) -> pd.DataFrame:
    latest_cost = (
        flavor_history.sort_values("fecha")
        .groupby("id")["costo_por_ml"]
        .last()
        .reset_index()
        .rename(columns={"id": "sabor_id"})
    )

    result = consumption_with_cost.merge(latest_cost, on= "sabor_id", how= "left")
    result["costo_por_ml"] = result["costo_por_ml"].fillna(0)
    result["costo_jarabe_evento"] = result["ml"] * result["costo_por_ml"]

    return result

def calculate_total_cost_per_liter(full_cost: pd.DataFrame) -> pd.DataFrame:
    result = full_cost.copy()
    result["costo_total_evento"] = result["costo_agua_evento"] + result["costo_jarabe_evento"]
    result["costo_total_por_litro"] = result["costo_total_evento"] / result["consumo"]

    return result

def calculate_savings_vs_market(with_total_cost: pd.DataFrame, market: pd.DataFrame) -> pd.DataFrame:
    year_cols = [c for c in market.columns if str(c).strip().isdigit()]
    market_price_by_year = {int(y): market[y].mean() for y in year_cols}

    result = with_total_cost.copy()
    result["precio_mercado"] = result["anio"].map(market_price_by_year)

    result["ahorro_por_litro"] = result["precio_mercado"] - result["costo_total_por_litro"]
    result["ahorro_evento"] = result["ahorro_por_litro"] * result["consumo"]

    return result

def calculate_roi(with_savings: pd.DataFrame) -> dict:
    with_savings = with_savings.copy()
    with_savings["fecha"] = pd.to_datetime(with_savings["fecha"])

    previous_start = pd.to_datetime(params.PREVIOUS_EQUIPMENT_PURCHASE_DATE)
    previous_end = pd.to_datetime(params.PREVIOUS_EQUIPMENT_END_DATE)
    current_start = pd.to_datetime(params.CURRENT_EQUIPMENT_PURCHASE_DATE)

    previous_mask = (with_savings["fecha"] >= previous_start) & (with_savings["fecha"] < previous_end)
    previous_savings = with_savings.loc[previous_mask, "ahorro_evento"].sum()
    previous_investment =(
        params.PREVIOUS_EQUIPMENT 
        - params.PREVIOUS_EQUIPMENT_SALE
        - params.PREVIOUS_EQUIPMENT_CYLINDER_SALE
    )
    previous_roi = previous_savings - previous_investment

    current_mask = with_savings["fecha"] >= current_start
    current_savings = with_savings.loc[current_mask, "ahorro_evento"].sum()
    current_investment = params.CURRENT_EQUIPMENT
    current_roi = current_savings - current_investment

    return {
        "previous_equipment": {
            "investment": previous_investment,
            "savings_generated": previous_savings,
            "roi": previous_roi,
            "roi_achieved": previous_roi >= 0,
        },
        "current_equipment": {
            "investment": current_investment,
            "savings_generated": current_savings,
            "roi": current_roi,
            "roi_achieved": current_roi >= 0,
        },
    }