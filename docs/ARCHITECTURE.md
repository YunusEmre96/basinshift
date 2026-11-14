# Mimari

```
app.py                         Streamlit giriş noktası (üst menü: 7 sayfa)
config.yaml                    veri kaynağı seçimi, API ayarları
tables/                        TÜM varsayımlar (kod bilmeden düzenlenir)
  basins.yaml                  havzalar, pilot noktalar, sentetik iklim normalleri
  crops.csv                    Kc, sezon, Ky, eşikler, toprak/yem özellikleri, yerel riskler
  basin_economics.csv          havza × ürün: ekim tarihi, verim, fiyat, maliyet, esneklik
  rotation_effects.csv         önceki ürün etkileri
  farm_types.csv               havza modeli için temsili çiftlik tipleri (SENTETİK)
  rules/*.yaml                 kural paketleri (Konya, AB GAEC 7, SGMA, MDB, Pencap, tavsiye)
  glossary.yaml                uygulama içi sözlük (TR/EN)
basinshift/
  config.py                    yapılandırma + ortam değişkeni geçersiz kılma
  data/
    schema.py                  VERİ SÖZLEŞMESİ — hesaplar yalnızca bunu bilir
    basins.py                  Havza / Site
    hub.py                     DataHub: yönlendirme, önbellek, doğrulama, geri düşme, provenance
    providers/
      base.py                  ortak arayüz
      synthetic.py             demo verisi (deterministik)
      nasa.py                  canlı NASA: POWER, AppEEARS, CMR/GRACE, NCCS/CMIP6, SoilGrids
      nasa_power.py            POWER istemcisi + ayrıştırıcı
      appeears.py              AppEEARS istemcisi + SMAP/HLS/MODIS dönüştürücüleri
      files.py                 data/external/ CSV okuyucu (ham NASA biçimleri dahil)
  knowledge/
    tables.py                  tablo yükleyicileri
    rules.py                   kural motoru (tekil + vektörel), destek/ceza
  engine/
    solar.py, et0.py           FAO-56 radyasyon ve Penman-Monteith
    calendar.py                ürün takvimi, Kc eğrisi
    water.py                   ürün-yıl tablosu (günlük su dengesi, iklim stresi)
    rotation.py                önceki ürün matrisleri
    soil.py                    toprak alt skorları, yem, örtü bitkisi
    field.py                   FieldContext: vektörel stres testi, özet, tek plan ayrıntısı
    pipeline.py                veri → senaryo → tablo → FieldContext
    scenarios.py               kaydırıcılar + CMIP6 değişim katsayıları
    risk.py                    risk takvimi, plan takvimi
    trends.py                  Mann-Kendall + Sen eğimi
    crop_detect.py             NDVI'dan ürün grubu
    metrics.py                 CVaR
  optimizer/
    pareto.py                  Pareto maskesi
    search.py                  tarama, kartlar, tarla bölme karışımları
  explain/
    why.py                     "Neden bu plan?" (5 başlık, şablon tabanlı)
    confidence.py              güven etiketleri
    fmt.py                     para/alan/plan biçimlendirme
  basin/model.py               havza LP (HiGHS), örümcek ağı, gölge fiyat
  report/scorecard.py          Risk ve Su Karnesi (PDF)
  ui/                          state (önbellekli hesaplar), components, pages, i18n
scripts/
  fetch_data.py                gerçek veriyi indir → önbellek
  export_synthetic.py          files kaynağı için şablon CSV'ler
tests/                         pytest (46 test)
```

## Tasarım ilkeleri

1. **Veri sözleşmesi:** kaynak ne olursa olsun veri `schema.py`'ye dönüştürülür.
   Sentetik → NASA geçişi hesaplara dokunmaz.
2. **Provenance her yerde:** her veri setinin gerçekte nereden geldiği kaydedilir;
   arayüz rozetleri, "Neden bu plan?" kanıt satırları, güven etiketleri ve PDF
   karnedeki uyarı bu kayıttan beslenir. Sentetik veri asla gerçek gibi sunulmaz.
3. **Varsayımlar kodda değil tablolarda:** ziraat mühendisi CSV/YAML düzenleyerek
   modeli güncelleyebilir.
4. **Kara kutu yok:** hesaplar FAO yöntemleri ve şeffaf optimizasyon; açıklama
   metinleri şablon tabanlı (dil modeli rakam üretmez).
5. **Vektörel hesap:** 28.561 plan × 41 dönem × 4 yıl, sıradan bir dizüstünde ~1 sn.

## Performans

| Adım | Süre (dizüstü) |
|---|---|
| Ürün-yıl tablosu (13 ürün × 44 yıl, günlük denge) | ~0,2 sn |
| 28.561 planın stres testi + kurallar + toprak | ~0,9 sn |
| Pareto + kartlar + karışımlar | ~0,3 sn |
| Havza modeli (LP + 12 yıllık örümcek ağı + bütçe eğrisi) | ~0,5–1 sn |
