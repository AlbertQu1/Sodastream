import pandas as pd

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