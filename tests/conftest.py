import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
# Testler daima sentetik veriyle ve önbelleksiz çalışır (ağ erişimi gerekmez)
os.environ.setdefault("BASINSHIFT_DATA", "synthetic")


@pytest.fixture(scope="session")
def hub():
    from basinshift.data import DataHub
    return DataHub()


@pytest.fixture(scope="session")
def konya():
    from basinshift.data.basins import load_basins
    return load_basins()["konya"]


@pytest.fixture(scope="session")
def cumra_ctx(hub, konya):
    from basinshift.engine.field import FieldSettings
    from basinshift.engine.pipeline import build_context
    st = FieldSettings(True, "sprinkler", True, None, konya.water_cost_per_m3, ["sugar_beet", "maize_grain"], 2027)
    return build_context(hub, konya.site("cumra"), konya, st)
