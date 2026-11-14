# data/external — kendi veri dosyalarınız

Bir veri setinin kaynağını `files` yaptığınızda (config.yaml veya
`BASINSHIFT_DATA_<VERİSETİ>=files`) uygulama dosyaları burada arar:

```
data/external/
  climate_daily/<nokta_id>.csv      # ör. cumra.csv — NASA POWER CSV'si olduğu gibi konabilir
  soil_moisture/<nokta_id>.csv      # AppEEARS SMAP CSV'si olduğu gibi konabilir
  ndvi/<nokta_id>.csv               # date, ndvi, source (HLS/MODIS)
  precip_satellite/<nokta_id>.csv   # date, precip (GPM IMERG)
  water_storage/<havza_id>.csv      # date, tws_anomaly_cm (GRACE)
  climate_deltas/<nokta_id>.csv     # month, scenario, dtmax, dtmin, precip_ratio
  terrain/<nokta_id>.csv            # elevation_m, slope_deg
  soil_properties/<nokta_id>.csv    # taw_mm_per_m, clay_pct, sand_pct, soc_g_kg, ph
  sinkholes.csv                     # lat, lon, year  (AFAD obruk konumları — havza haritası)
```

Örnek biçim için: `python scripts/export_synthetic.py --out data/external_example`

Sütun adları esnektir: `T2M_MAX`, `PRECTOTCORR`, `YEAR/MO/DY` gibi ham NASA
adları otomatik tanınır (basinshift/data/providers/files.py → ALIASES).
Ayrıntı: docs/DATA_SWAP.md
