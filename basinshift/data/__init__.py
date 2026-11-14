"""Veri katmanı.

Kullanım:
    from basinshift.data import DataHub
    hub = DataHub()                       # config.yaml'a göre kaynak seçer
    climate = hub.climate_daily(site, basin)
    hub.provenance["climate_daily"]       # hangi kaynaktan geldi, uyarılar
"""
from .hub import DataHub  # noqa: F401
