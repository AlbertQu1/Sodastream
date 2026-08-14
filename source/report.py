"""
Presents calculation results in a readable format.
No calculations happen here — just formatting and printing.
"""


def print_summary(with_savings, roi):
    total_litros = with_savings["consumo"].sum()
    total_ahorro = with_savings["ahorro_evento"].sum()

    print("\n" + "=" * 40)
    print("RESUMEN GENERAL")
    print("=" * 40)
    print(f"Litros totales consumidos: {total_litros:,.0f} L")
    print(f"Ahorro total generado:     ${total_ahorro:,.2f} MXN")

    print("\n" + "-" * 40)
    print("EQUIPO ANTERIOR")
    print("-" * 40)
    prev = roi["previous_equipment"]
    print(f"Inversión neta:    ${prev['investment']:,.2f} MXN")
    print(f"Ahorro generado:   ${prev['savings_generated']:,.2f} MXN")
    print(f"ROI:               ${prev['roi']:,.2f} MXN")
    print(f"ROI alcanzado:     {'✅ Sí' if prev['roi_achieved'] else '❌ No'}")

    print("\n" + "-" * 40)
    print("EQUIPO ACTUAL")
    print("-" * 40)
    curr = roi["current_equipment"]
    print(f"Inversión:         ${curr['investment']:,.2f} MXN")
    print(f"Ahorro generado:   ${curr['savings_generated']:,.2f} MXN")
    print(f"ROI:               ${curr['roi']:,.2f} MXN")
    print(f"ROI alcanzado:     {'✅ Sí' if curr['roi_achieved'] else '❌ No'}")


def print_yearly_breakdown(with_savings):
    yearly = with_savings.groupby("anio").agg(
        litros=("consumo", "sum"),
        ahorro=("ahorro_evento", "sum"),
        precio_mercado=("precio_mercado", "mean"),
    )

    print("\n" + "=" * 40)
    print("DESGLOSE POR AÑO")
    print("=" * 40)
    for anio, row in yearly.iterrows():
        print(f"\nAño {anio} | Mercado: ${row['precio_mercado']:.2f} MXN/L")
        print(f"  Litros consumidos: {row['litros']:.0f} L")
        print(f"  Ahorro generado:   ${row['ahorro']:.2f} MXN")
        
def print_flavor_breakdown(with_savings, flavors):
    
    by_flavor = with_savings.groupby("sabor_id").agg(
        litros=("consumo", "sum"),
        ml_totales=("ml", "sum"),
        costo_jarabe=("costo_jarabe_evento", "sum"),
        eventos=("#", "count"),
    ).reset_index()

    by_flavor = by_flavor.merge(flavors[["sabor_id", "sabor"]], on="sabor_id", how="left")

    print("\n" + "=" * 40)
    print("DESGLOSE POR SABOR")
    print("=" * 40)
    for _, row in by_flavor.iterrows():
        print(f"\n{row['sabor'].title()} (id={row['sabor_id']})")
        print(f"  Eventos:            {row['eventos']:.0f}")
        print(f"  Litros:             {row['litros']:.0f} L")
        print(f"  ml de jarabe usado: {row['ml_totales']:.0f} ml")
        print(f"  Costo de jarabe:    ${row['costo_jarabe']:.2f} MXN")
        
def print_seasonal_breakdown(with_savings):
    print("\n" + "=" * 40)
    print("DESGLOSE POR TEMPORADA")
    print("=" * 40)
    por_temporada = with_savings.groupby("temporada").agg(
        litros=("consumo", "sum"), ahorro=("ahorro_evento", "sum")
    )
    for temporada, row in por_temporada.iterrows():
        print(f"{temporada:<12} Litros: {row['litros']:.0f}")

    print("\n" + "-" * 40)
    print("LLUVIAS VS SECA")
    print("-" * 40)
    por_clima = with_savings.groupby("temporada_clima").agg(
        litros=("consumo", "sum"), ahorro=("ahorro_evento", "sum")
    )
    for temporada, row in por_clima.iterrows():
        print(f"{temporada:<12} Litros: {row['litros']:.0f}")

    print("\n" + "-" * 40)
    print("POR DIA DE LA SEMANA")
    print("-" * 40)
    por_dia = with_savings.groupby("dia_semana").agg(
        litros=("consumo", "sum"), ahorro=("ahorro_evento", "sum")
    )
    for dia, row in por_dia.iterrows():
        print(f"{dia:<12} Litros: {row['litros']:.0f}")