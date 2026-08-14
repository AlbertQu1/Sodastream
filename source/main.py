from data_loader import load_all
from cleaning import clean_all
from calculations import (
    calculate_cylinder_cost_by_year,
    calculate_cost_per_liter,
    calculate_syrup_cost,
    calculate_total_cost_per_liter,
    calculate_savings_vs_market,
    calculate_roi, add_season_columns
)
from report import print_summary, print_yearly_breakdown, print_flavor_breakdown, print_seasonal_breakdown


def main():
    raw = load_all()
    clean = clean_all(raw)
    clean["consumption"] = add_season_columns(clean["consumption"])

    cylinder_cost = calculate_cylinder_cost_by_year(clean["consumption"], clean["refills"])
    consumption_with_cost = calculate_cost_per_liter(clean["consumption"], cylinder_cost)
    full_cost = calculate_syrup_cost(consumption_with_cost, clean["flavor_history"])
    with_total = calculate_total_cost_per_liter(full_cost)
    with_savings = calculate_savings_vs_market(with_total, clean["market"])
    roi = calculate_roi(with_savings)

    print_summary(with_savings, roi)
    print_yearly_breakdown(with_savings)
    print_flavor_breakdown(with_savings, clean["flavors"])
    print_seasonal_breakdown(with_savings) 


if __name__ == "__main__":
    main()