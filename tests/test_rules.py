import numpy as np

from basinshift.knowledge.rules import check_plan, evaluate_plans, load_rule_pack, support_matrix, water_cap
from basinshift.knowledge.tables import basin_crops, load_crops

CROPS = load_crops()
IDS = basin_crops("konya")
KONYA = [load_rule_pack("tr_konya_water_2026"), load_rule_pack("advisory_agronomy")]
YEARS = [2027, 2028, 2029, 2030]


def idx(plan):
    return np.array([[IDS.index(c) for c in plan]])


def test_mehmet_plan_is_red_card():
    r = check_plan(["sugar_beet", "maize_grain", "sugar_beet", "maize_grain"], YEARS,
                   ["sugar_beet", "maize_grain"], IDS, CROPS, KONYA, True, True)
    assert r.status == "red"
    assert 0 in r.violation_positions


def test_single_violation_is_yellow():
    r = check_plan(["wheat", "sugar_beet", "chickpea", "barley"], YEARS,
                   ["sugar_beet", "maize_grain"], IDS, CROPS, KONYA, True, True)
    assert r.status == "yellow" and r.violation_positions == [1]


def test_compliant_plan_is_green():
    r = check_plan(["wheat", "chickpea", "safflower", "barley"], YEARS,
                   ["sugar_beet", "maize_grain"], IDS, CROPS, KONYA, True, True)
    assert r.status == "green" and not r.legal


def test_rules_do_not_apply_to_rainfed_or_unrestricted():
    plan = ["sugar_beet", "maize_grain", "sugar_beet", "maize_grain"]
    assert check_plan(plan, YEARS, [], IDS, CROPS, KONYA, False, True).status == "green"
    assert check_plan(plan, YEARS, [], IDS, CROPS, KONYA, True, False).status == "green"


def test_vectorized_matches_single():
    plans = [["sugar_beet", "maize_grain", "sugar_beet", "maize_grain"],
             ["wheat", "sugar_beet", "chickpea", "barley"],
             ["wheat", "chickpea", "safflower", "barley"]]
    hist = [IDS.index("sugar_beet"), IDS.index("maize_grain")]
    arr = np.vstack([idx(p) for p in plans])
    ev = evaluate_plans(arr, hist, IDS, CROPS, KONYA, True, True)
    single = [check_plan(p, YEARS, ["sugar_beet", "maize_grain"], IDS, CROPS, KONYA, True, True).status for p in plans]
    assert list(ev["status"]) == single


def test_beet_break_advisory():
    r = check_plan(["sugar_beet", "wheat", "sugar_beet", "wheat"], YEARS, [], IDS, CROPS, KONYA, True, True)
    assert any(v.rule_id == "crop_min_gap" for v in r.advisory)


def test_support_penalties():
    arr = np.vstack([idx(["sugar_beet", "maize_grain", "sugar_beet", "maize_grain"]),
                     idx(["wheat", "chickpea", "safflower", "barley"])])
    hist = [IDS.index("sugar_beet"), IDS.index("maize_grain")]
    ev = evaluate_plans(arr, hist, IDS, CROPS, KONYA, True, True)
    sup = support_matrix(arr, ev["legal_viol"], IDS, KONYA, True, True)
    assert sup[0].sum() == 0                         # kırmızı kart → destek yok
    assert sup[1, 0] == 954 + 514                    # buğday: temel+planlı + su kısıtı desteği
    assert sup[1, 1] == 734 + 294                    # nohut: 1. kategori su kısıtı katsayısı (0,8)


def test_water_restriction_bonus_only_when_restricted_and_irrigated():
    arr = idx(["wheat", "chickpea", "safflower", "barley"])
    no_viol = np.zeros_like(arr, dtype=bool)
    assert support_matrix(arr, no_viol, IDS, KONYA, True, False)[0, 0] == 954     # kısıt yok → bonus yok
    assert support_matrix(arr, no_viol, IDS, KONYA, False, True)[0, 0] == 954     # kuru tarım → bonus yok


def test_no_support_for_grain_maize_and_potato_in_restricted_basin():
    arr = idx(["maize_grain", "wheat", "potato", "wheat"])
    no_viol = np.zeros_like(arr, dtype=bool)
    sup = support_matrix(arr, no_viol, IDS, KONYA, True, True)
    assert sup[0, 0] == 0 and sup[0, 2] == 0


def test_water_caps():
    assert water_cap([load_rule_pack("us_ca_sgma")], True, False) == 750
    assert water_cap(KONYA, True, True) is None


def test_gaec7_max_consecutive():
    r = check_plan(["wheat", "wheat", "wheat", "wheat"], YEARS, [], IDS, CROPS, [load_rule_pack("eu_gaec7")], True, False)
    assert r.violation_positions == [3]
