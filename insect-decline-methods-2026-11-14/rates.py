"""rates.py: put the reported declines on one scale, percent per year, as if each decline had been even over its period.

rate = 1 - (1 - total_decline) ** (1 / years). This is a conversion for comparison, not a result of any of the papers: the
papers fit different models, and a decline need not be even. The inputs are the figures quoted in claims.json; where a paper
states its own annual rate it is printed beside the conversion. Prints JSON."""
import json

ROWS = [
    # label, total decline as a fraction, years, what was measured, the paper's own annual figure where it states one
    ("Hallmann et al. 2017, protected areas, western Germany", 0.767, 27, "flying insect biomass, Malaise traps", "5.2% (plot-specific models)"),
    ("Seibold et al. 2019, grassland", 0.67, 9, "biomass, standardized inventories 2008 to 2017", None),
    ("Seibold et al. 2019, grassland", 0.78, 9, "abundance", None),
    ("Seibold et al. 2019, grassland", 0.34, 9, "number of species", None),
    ("Seibold et al. 2019, forest, 30 sites with annual inventories", 0.41, 9, "biomass", None),
    ("Seibold et al. 2019, forest, 30 sites with annual inventories", 0.36, 9, "number of species", None),
    ("van Klink et al. 2020, terrestrial, worldwide", 0.09, 10, "abundance, meta-analysis of 166 surveys", None),
]


def annual(total, years): return 1 - (1 - total) ** (1.0 / years)


def table():
    out = [{"study": s, "measured": m, "total_decline_percent": round(100 * t, 1), "years": y, "percent_per_year": round(100 * annual(t, y), 1), "papers_own_annual_figure": own} for s, t, y, m, own in ROWS]
    out.append({"study": "Hallmann et al. 2020, two Dutch sites", "measured": "macro-moths, beetles, caddisflies at light; ground beetles in pitfall traps", "percent_per_year": [3.8, 5.0, 9.2, 4.3], "note": "annual rates as stated in the abstract; no conversion"})
    out.append({"study": "Neff et al. 2022, Switzerland", "measured": "occupancy of 390 species, 1980 to 2020", "percent_per_year": 0, "note": "the abstract reports no overall decline; strong increases and decreases by species"})
    return out


if __name__ == "__main__":
    print(json.dumps(table(), indent=1, ensure_ascii=False))
