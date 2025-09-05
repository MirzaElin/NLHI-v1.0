import math
import pytest
from nlhi_core import convert_to_years, compute_dstlya, compute_dsav, compute_nlhi

def test_unit_conversions():
    assert math.isclose(convert_to_years(365.25, "Day(s)"), 1.0, rel_tol=1e-6)
    assert math.isclose(convert_to_years(52.1429, "Week(s)"), 1.0, rel_tol=1e-6)
    assert math.isclose(convert_to_years(12, "Month(s)"), 1.0, rel_tol=1e-6)
    assert math.isclose(convert_to_years(1, "Year(s)"), 1.0, rel_tol=1e-6)

def test_dstlya_positive_mortality_term():
    # Example: TLIPHS = 730.5 days (~2 years), mortality=10, LE=80, age=40
    tliphs_years = convert_to_years(730.5, "Day(s)")
    dstlya = compute_dstlya(730.5, "Day(s)", 10, 80, 40)
    assert math.isclose(dstlya, tliphs_years + 10*(80-40), rel_tol=1e-9)

def test_dstlya_zero_or_negative_term():
    # LE <= age -> mortality contribution <= 0
    dstlya1 = compute_dstlya(365.25, "Day(s)", 5, 40, 40)  # zero term
    dstlya2 = compute_dstlya(365.25, "Day(s)", 5, 35, 40)  # negative term
    assert dstlya1 <= convert_to_years(365.25, "Day(s)") + 1e-12
    assert dstlya2 < convert_to_years(365.25, "Day(s)")

def test_dsav_and_nlhi_roundtrip():
    # Setup: population=1000, mean age=40, two domains with dstlya 100 and 200
    age, pop = 40, 1000
    d1 = compute_dsav(100, age, pop)
    d2 = compute_dsav(200, age, pop)
    nlhi = compute_nlhi([d1, d2])
    # Expected DSAVs: (100*100)/(40*1000)=0.25 and (200*100)/(40*1000)=0.5
    assert math.isclose(d1, 0.25, rel_tol=1e-9)
    assert math.isclose(d2, 0.5, rel_tol=1e-9)
    assert math.isclose(nlhi, (0.25+0.5)/2.0, rel_tol=1e-9)

def test_nlhi_empty_list():
    assert compute_nlhi([]) == 0.0
