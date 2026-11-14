# Kılavuz (Sürüm 3.0) üretimi

HTML + CSS kaynaktan Chrome ile A4 PDF üretir (kapak + gövde, içindekiler sayfa numaraları otomatik).

Gerekenler: Python, `playwright` + Google Chrome, `pypdf`, `Pillow`, poppler (`pdfinfo`, `pdftotext`), Inter yazı tipi.

```bash
# 1) uygulamayı açın (calistir.bat) ve ekran görüntülerini alın (scripts/capture_all.py ya da kendi aracınız)
# 2) kılavuzu üretin:
python scripts/kilavuz_v3/build.py docs/ekran_goruntuleri/tr  BasinShift_Kilavuz.pdf
```

Ekran görüntüsü dosya adları: `00_field_top, 01_field, 03_plans, 04_plans_why, 05_status, 06_futures, 07_basin,
08_report, 09_method, 10_pareto` (.png, 1600 px genişlik). Kırpma koordinatları `build.py → CROPS`.
Metin `part1-3.html` içinde; rakamlar uygulama çıktısıdır (14.11.2026) — model değişirse güncelleyin.
`docs/ekran_goruntuleri/` altındaki JPEG'ler aynı görüntülerin sıkıştırılmış kopyasıdır (TR ve EN).
