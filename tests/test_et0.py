import numpy as np
import pandas as pd

from basinshift.engine.et0 import et0_from_climate, penman_monteith
from basinshift.engine.solar import extraterrestrial_radiation


def test_fao56_example18_uccle():
    """FAO-56 Örnek 18: Uccle (Brüksel), 6 Temmuz → ET0 ≈ 3.9 mm/gün."""
    et0 = penman_monteith(21.5, 12.3, 22.07, 2.078, 50.8, 100, 187, ea=1.409)
    assert abs(float(et0) - 3.9) < 0.1


def test_fao56_example8_ra():
    """FAO-56 Örnek 8: 20°G, 3 Eylül (gün 246) → Ra = 32.2 MJ/m²/gün."""
    ra = extraterrestrial_radiation(-20.0, np.array([246]))
    assert abs(float(ra[0]) - 32.2) < 0.2


def test_missing_radiation_is_filled_with_hargreaves():
    idx = pd.date_range("1982-07-01", periods=5, freq="D")
    df = pd.DataFrame({"tmax": 32.0, "tmin": 15.0, "tmean": 23.5, "rh": 40.0, "wind2m": 2.0,
                       "rs": [np.nan, np.nan, 25.0, 25.0, np.nan], "precip": 0.0}, index=idx)
    et0 = et0_from_climate(df, 37.6, 1000)
    assert et0.notna().all()
    assert (et0 > 3).all() and (et0 < 10).all()
