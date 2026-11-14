# Sentetik veriden gerçek NASA verisine geçiş

BasinShift'in hesap çekirdeği yalnızca **veri şemasını** (`basinshift/data/schema.py`)
bilir; verinin nereden geldiğini bilmez. Bu yüzden kaynak değiştirmek tek bir
ayardır ve kodda değişiklik gerektirmez.

## 0. Kısa yol (yarışma günü, Windows)

1. `kur.bat` (bir kez) → 2. `veri_indir.bat` → 3. `calistir.bat`.

`veri_indir.bat` dört havzanın bütün pilot noktaları için NASA POWER iklimini ve SoilGrids toprak verisini indirir,
birim/ölçek kontrolünden geçirir (yıllık yağış, radyasyon birimi, eksik veri, Tmax < Tmin…), sentetikle yan yana
karşılaştırır ve **yalnızca tümü başarılı olan** veri setleri için `config.yaml`'daki kaynağı `nasa` yapar. Rapor:
`data/veri_raporu.txt`. İndirilen veri `data/cache/nasa/` altında kalır; sonrasında internet gerekmez.

### Kaynak beyanı: `data/external/KAYNAK.yaml`

`data/external/` klasöründe bir dosyanın durması onun gerçek veri olduğu anlamına gelmez. Her veri seti için
`origin` yazılır: `nasa` (NASA ürünü), `external` (NASA dışı açık veri, ör. SoilGrids), `synthetic` (yer tutucu),
`assumed` (elle girilmiş değer). Kökeni yazılmayan dosya arayüzde **doğrulanmamış** görünür ve gerçek sayılmaz.
Gerçek SMAP/HLS dosyası koyduğunuzda ilgili satırı `origin: nasa` yapın.

Earthdata gerektirenler (SMAP, HLS/MODIS, SRTM, GRACE): `.env.example` dosyasını `.env` adıyla kopyalayıp doldurun,
`nasa_ek_paketler.bat` çalıştırın, sonra `veri_indir.bat --earthdata`. CMIP6: `veri_indir.bat --datasets climate_deltas`.

Aşağıdaki `BASINSHIFT_DATA=... streamlit run app.py` biçimi Linux/macOS içindir. Windows PowerShell'de:
`$env:BASINSHIFT_DATA_CLIMATE_DAILY="nasa"; streamlit run app.py`

## 1. Üç kaynak

| Kaynak | Ne zaman | Nasıl çalışır |
|---|---|---|
| `synthetic` | Varsayılan; NASA verisi bağlanmadan önce | Gerçek şemayla aynı, fiziksel olarak tutarlı uydurma veri. Arayüzde sarı "Demo modu" uyarısı ve PDF karnede uyarı çıkar. |
| `nasa` | İnternet varken | Canlı API: NASA POWER, AppEEARS (SMAP/HLS/MODIS/SRTM), CMR/PO.DAAC (GRACE), NCCS THREDDS (NEX-GDDP-CMIP6), SoilGrids. İndirilen her şey `data/cache/nasa/` altına yazılır. |
| `files` | Yarışmada NASA dosya paylaşırsa ya da veriyi web arayüzünden elle indirirseniz | `data/external/` altındaki CSV'ler okunur. Ham NASA biçimleri (POWER CSV, AppEEARS CSV) olduğu gibi kabul edilir. |

## 2. Geçiş yöntemleri

**Hepsini birden** (en hızlı):
```bash
BASINSHIFT_DATA=nasa streamlit run app.py
```

**Yalnızca bir veri seti** (ör. iklim gerçek, diğerleri sentetik):
```bash
BASINSHIFT_DATA_CLIMATE_DAILY=nasa streamlit run app.py
```

**Kalıcı olarak** `config.yaml`:
```yaml
data:
  default_source: nasa
  sources:
    precip_satellite: files     # IMERG'i dosyadan oku
```

Veri seti adları: `climate_daily`, `soil_moisture`, `ndvi`, `precip_satellite`,
`water_storage`, `climate_deltas`, `terrain`, `soil_properties`.

## 3. Önerilen akış (yarışma öncesi / sırası)

1. **NASA POWER (anahtar gerekmez)** — iklim, projenin omurgası:
   ```bash
   python scripts/fetch_data.py --basin konya --datasets climate_daily
   ```
   Başarılıysa `BASINSHIFT_DATA_CLIMATE_DAILY=nasa` ile uygulamayı açın. Önbellek
   sayesinde demo sırasında internet gerekmez.
2. **Earthdata hesabı** (https://urs.earthdata.nasa.gov) açın ve ortam değişkenlerini verin:
   ```bash
   export EARTHDATA_USERNAME=...   EARTHDATA_PASSWORD=...
   # ya da
   export EARTHDATA_TOKEN=...
   python scripts/fetch_data.py --basin konya --datasets soil_moisture,ndvi,terrain
   ```
   AppEEARS görevleri kuyruğa girer; birkaç dakikadan yarım saate kadar sürebilir.
3. **GRACE ve CMIP6** için ek paketler: `pip install -r requirements-nasa.txt`
   ```bash
   python scripts/fetch_data.py --basin konya --datasets water_storage,climate_deltas
   ```
4. Kimlik bilgileri **asla** `config.yaml`'a yazılmaz; yalnızca ortam değişkeni.

## 4. Bir API çalışmazsa

* `config.yaml → data.fallback_to_synthetic: true` (varsayılan) ise uygulama
  çökmez; o veri seti için sentetiğe düşer ve arayüzde **turuncu uyarı** gösterir
  ("istenen kaynak çalışmadı, sentetik veriye geçildi"). Kenar çubuğundaki
  "Veri kaynakları" bölümünde hata mesajı görünür.
* Kesin sonuç istiyorsanız `fallback_to_synthetic: false` yapın; hata olursa
  uygulama durur ve nedenini söyler.
* Her zaman çalışan yedek yol: veriyi NASA'nın web arayüzünden indirip
  `files` kaynağını kullanmak (aşağıda).

## 5. `files` kaynağı — dosya biçimleri

```
data/external/climate_daily/<nokta_id>.csv
```
* NASA POWER Data Access Viewer'dan (https://power.larc.nasa.gov/data-access-viewer/)
  "Agroclimatology → Daily → CSV" ile indirilen dosya **olduğu gibi** konabilir.
  Başlık bloğu (`-BEGIN HEADER-`…`-END HEADER-`) atlanır; `YEAR, MO, DY`,
  `T2M_MAX, T2M_MIN, T2M, RH2M, WS2M, ALLSKY_SFC_SW_DWN, PRECTOTCORR` adları tanınır.
* Nokta kimlikleri: `cumra`, `karapinar`, `cihanbeyli`, `fresno`, `ludhiana`, `griffith`
  (bkz. `tables/basins.yaml`).

Diğer veri setleri ve sütunlar için `data/external/README.md`. Biçimi görmek için:
```bash
python scripts/export_synthetic.py --out data/external_example
```

## 6. Yarışmada paylaşılan yeni bir API'yi bağlamak

1. `basinshift/data/providers/` altında `DataProvider`'dan türeyen bir sınıf yazın
   (yalnızca ihtiyaç duyulan metodlar; ör. `climate_daily`).
2. Dönen tabloyu `schema.py`'deki sütun adlarına çevirin.
3. `basinshift/data/hub.py → PROVIDERS` sözlüğüne bir ad ile ekleyin ve
   `config.py → VALID_SOURCES`'a aynı adı ekleyin.
4. `config.yaml`'da o veri setinin kaynağını bu ada çevirin.

DataHub doğrulama, önbellek, geri düşme ve kaynak kaydını otomatik yapar.

## 7. Test durumu (dürüst not)

| İstemci | Durum |
|---|---|
| NASA POWER | JSON/CSV ayrıştırıcıları birim testli (`tests/fixtures/`); canlı uç nokta geliştirme ortamından erişilemediği için canlı test edilmedi. |
| AppEEARS, CMR/GRACE, NCCS/CMIP6, SoilGrids | Resmi belgelere göre yazıldı; canlı test edilmedi. İlk denemeyi küçük bir aralıkla yapın. |
| GPM IMERG | Canlı istemci yok; GES DISC'ten CSV indirip `files` kaynağıyla kullanın. |
