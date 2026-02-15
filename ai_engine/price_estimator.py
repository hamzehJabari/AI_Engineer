"""
Price Estimator — crisp (rule-based) logic for the Jordanian car market.

Categories:
  - Luxury   : Mercedes S-Class, BMW 7-Series, Audi A8, Porsche, Range Rover, Lexus LS, etc.
  - Premium  : Mercedes C/E, BMW 3/5, Audi A4/A6, Volvo, Lexus IS/ES, Infiniti, etc.
  - Economic : Toyota, Hyundai, Kia, Nissan Sunny/Sentra, Honda Civic, Suzuki, etc.

Depreciation model (per year):
  - Luxury   : 12% per year
  - Premium  : 10% per year
  - Economic :  7% per year

Additional mileage penalty:
  - > 100 000 km  → extra 5% off
  - > 200 000 km  → extra 10% off

The original (new) prices are rough averages for the Jordanian market in JOD.
"""
import datetime
from typing import Dict, Optional

# ---------------------------------------------------------------
# Car database: make → { models: {model: category}, base_price }
# base_price is a rough NEW-car price in JOD for the Jordanian market
# ---------------------------------------------------------------
CAR_DATABASE: Dict[str, dict] = {
    # ---- LUXURY ----
    "mercedes": {
        "s-class":   {"category": "luxury",  "base_price": 85_000},
        "gle":       {"category": "luxury",  "base_price": 72_000},
        "gls":       {"category": "luxury",  "base_price": 90_000},
        "g-class":   {"category": "luxury",  "base_price": 120_000},
        "e-class":   {"category": "premium", "base_price": 52_000},
        "c-class":   {"category": "premium", "base_price": 38_000},
        "a-class":   {"category": "premium", "base_price": 30_000},
        "cla":       {"category": "premium", "base_price": 33_000},
        "glc":       {"category": "premium", "base_price": 48_000},
    },
    "bmw": {
        "7-series":  {"category": "luxury",  "base_price": 82_000},
        "x7":        {"category": "luxury",  "base_price": 88_000},
        "x5":        {"category": "premium", "base_price": 60_000},
        "5-series":  {"category": "premium", "base_price": 48_000},
        "3-series":  {"category": "premium", "base_price": 36_000},
        "x3":        {"category": "premium", "base_price": 42_000},
        "x1":        {"category": "premium", "base_price": 32_000},
    },
    "audi": {
        "a8":        {"category": "luxury",  "base_price": 78_000},
        "q8":        {"category": "luxury",  "base_price": 75_000},
        "a6":        {"category": "premium", "base_price": 46_000},
        "a4":        {"category": "premium", "base_price": 35_000},
        "q5":        {"category": "premium", "base_price": 45_000},
        "q3":        {"category": "premium", "base_price": 33_000},
    },
    "porsche": {
        "cayenne":   {"category": "luxury",  "base_price": 95_000},
        "panamera":  {"category": "luxury",  "base_price": 100_000},
        "macan":     {"category": "luxury",  "base_price": 70_000},
    },
    "range rover": {
        "range rover":       {"category": "luxury",  "base_price": 110_000},
        "sport":             {"category": "luxury",  "base_price": 85_000},
        "velar":             {"category": "premium", "base_price": 55_000},
        "evoque":            {"category": "premium", "base_price": 42_000},
    },
    "lexus": {
        "ls":        {"category": "luxury",  "base_price": 75_000},
        "lx":        {"category": "luxury",  "base_price": 90_000},
        "es":        {"category": "premium", "base_price": 40_000},
        "is":        {"category": "premium", "base_price": 35_000},
        "nx":        {"category": "premium", "base_price": 38_000},
    },
    # ---- ECONOMIC ----
    "toyota": {
        "camry":     {"category": "economic", "base_price": 25_000},
        "corolla":   {"category": "economic", "base_price": 19_000},
        "yaris":     {"category": "economic", "base_price": 14_000},
        "rav4":      {"category": "economic", "base_price": 28_000},
        "land cruiser": {"category": "luxury", "base_price": 80_000},
        "prado":     {"category": "premium",  "base_price": 52_000},
        "hilux":     {"category": "economic", "base_price": 26_000},
        "fortuner":  {"category": "economic", "base_price": 32_000},
    },
    "hyundai": {
        "elantra":   {"category": "economic", "base_price": 17_000},
        "sonata":    {"category": "economic", "base_price": 22_000},
        "tucson":    {"category": "economic", "base_price": 25_000},
        "accent":    {"category": "economic", "base_price": 13_000},
        "creta":     {"category": "economic", "base_price": 18_000},
        "santa fe":  {"category": "economic", "base_price": 30_000},
    },
    "kia": {
        "cerato":    {"category": "economic", "base_price": 16_500},
        "sportage":  {"category": "economic", "base_price": 24_000},
        "sorento":   {"category": "economic", "base_price": 29_000},
        "picanto":   {"category": "economic", "base_price": 11_000},
        "rio":       {"category": "economic", "base_price": 13_000},
        "k5":        {"category": "economic", "base_price": 23_000},
    },
    "nissan": {
        "sunny":     {"category": "economic", "base_price": 13_500},
        "sentra":    {"category": "economic", "base_price": 16_000},
        "x-trail":   {"category": "economic", "base_price": 26_000},
        "kicks":     {"category": "economic", "base_price": 18_000},
        "patrol":    {"category": "luxury",   "base_price": 70_000},
    },
    "honda": {
        "civic":     {"category": "economic", "base_price": 20_000},
        "accord":    {"category": "economic", "base_price": 25_000},
        "cr-v":      {"category": "economic", "base_price": 27_000},
        "hr-v":      {"category": "economic", "base_price": 21_000},
    },
    "suzuki": {
        "swift":     {"category": "economic", "base_price": 12_000},
        "vitara":    {"category": "economic", "base_price": 18_000},
        "dzire":     {"category": "economic", "base_price": 11_500},
    },
    "volkswagen": {
        "golf":      {"category": "economic", "base_price": 22_000},
        "tiguan":    {"category": "premium",  "base_price": 32_000},
        "passat":    {"category": "premium",  "base_price": 30_000},
    },
    "chevrolet": {
        "cruze":     {"category": "economic", "base_price": 15_000},
        "malibu":    {"category": "economic", "base_price": 20_000},
    },
    "ford": {
        "focus":     {"category": "economic", "base_price": 17_000},
        "explorer":  {"category": "premium",  "base_price": 40_000},
    },
}

# Depreciation rates per year by category
DEPRECIATION_RATES = {
    "luxury":   0.12,
    "premium":  0.10,
    "economic": 0.07,
}

# Mileage penalty thresholds
MILEAGE_PENALTIES = [
    (200_000, 0.10),
    (100_000, 0.05),
]


def _lookup_car(make: str, model: str) -> Optional[dict]:
    """Look up a car in the database (case-insensitive)."""
    make_key = make.strip().lower()
    model_key = model.strip().lower()

    make_data = CAR_DATABASE.get(make_key)
    if not make_data:
        return None

    info = make_data.get(model_key)
    return info


def classify_car(make: str, model: str) -> str:
    """Return the category of a car: luxury / premium / economic."""
    info = _lookup_car(make, model)
    if info:
        return info["category"]
    # Default: economic (unknown cars treated as economic)
    return "economic"


def estimate_price(
    make: str,
    model: str,
    year: int,
    mileage_km: int = 0,
    custom_base_price: float = None,
) -> Dict:
    """
    Estimate the current market value of a car in JOD using crisp logic.

    Returns a dict with all computation details.
    """
    info = _lookup_car(make, model)
    current_year = datetime.date.today().year

    if info:
        category = info["category"]
        base_price = custom_base_price or info["base_price"]
    else:
        category = "economic"
        base_price = custom_base_price or 18_000  # default fallback

    age = max(0, current_year - year)
    rate = DEPRECIATION_RATES[category]

    # Compound depreciation: value = base * (1 - rate)^age
    depreciation_factor = (1 - rate) ** age
    depreciated_value = round(base_price * depreciation_factor, 2)

    # Mileage penalty
    mileage_penalty_pct = 0.0
    for threshold, penalty in MILEAGE_PENALTIES:
        if mileage_km >= threshold:
            mileage_penalty_pct = penalty
            break

    mileage_deduction = round(depreciated_value * mileage_penalty_pct, 2)
    final_price = round(depreciated_value - mileage_deduction, 2)

    # Never go below 5% of base price
    floor_price = round(base_price * 0.05, 2)
    if final_price < floor_price:
        final_price = floor_price

    total_depreciation_pct = round((1 - final_price / base_price) * 100, 2)

    return {
        "make": make.strip().title(),
        "model": model.strip().title(),
        "year": year,
        "mileage_km": mileage_km,
        "category": category,
        "original_price_jod": base_price,
        "depreciated_price_jod": final_price,
        "depreciation_pct": total_depreciation_pct,
        "breakdown": {
            "car_age_years": age,
            "annual_depreciation_rate": f"{rate*100:.0f}%",
            "age_depreciation_factor": round(depreciation_factor, 4),
            "value_after_age": depreciated_value,
            "mileage_penalty_pct": f"{mileage_penalty_pct*100:.0f}%",
            "mileage_deduction_jod": mileage_deduction,
            "floor_price_jod": floor_price,
        },
    }


def get_all_makes() -> list:
    """Return a sorted list of all known car makes."""
    return sorted(CAR_DATABASE.keys())


def get_models_for_make(make: str) -> list:
    """Return a sorted list of known models for a given make."""
    make_key = make.strip().lower()
    data = CAR_DATABASE.get(make_key, {})
    return sorted(data.keys())
