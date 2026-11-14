# Yöntemler ve varsayımlar

Bu belge jürinin "bu sayı nereden geliyor?" sorusuna cevap vermek için yazıldı.
Her katsayının yeri: `tables/` (agronomi, ekonomi, kurallar) veya ilgili modülün
başındaki sabitler.

## 1. Veri → hesap akışı

```
NASA POWER günlük iklim (1981–) ──► FAO-56 Penman-Monteith ET0
                                   │
SMAP kök bölgesi nemi (2015–) ─────┤► ekimde başlangıç toprak suyu
                                   │
ürün takvimi + Kc (FAO-56) ────────┴► günlük kök bölgesi su dengesi (her ürün × her yıl)
                                       │   ETc, kuru tarım ETa, tam sulama ihtiyacı, kullanılan yağış
                                       ▼
                     ürün-yıl tablosu (C × Y) + iklim stresi (sıcak/don/yağışlı hasat)
                                       ▼
4 yıllık plan × geçmişin her 4 yıllık penceresi ──► verim (FAO-33) → gelir, su, destek
                                       ▼
          kurallar (rules-as-code) + toprak skorları ──► Pareto ──► 3 kart + mevcut plan
```

## 2. Su (FAO-56)

* **ET0:** Penman-Monteith, günlük; radyasyon yoksa (POWER'da 1984 öncesi) Hargreaves
  radyasyon tahmini. Doğrulama: FAO-56 Örnek 18 → 3,88 mm/gün (kitap: 3,9).
* **Kc eğrisi:** dört dönem, doğrusal geçişler (FAO-56 Tablo 11–12). Havzaya göre
  sezon uzunluğu ölçeği (`basin_economics.csv → season_scale`).
* **Kök bölgesi kapasitesi:** TAW = toprak kullanılabilir suyu (mm/m) × kök derinliği.
* **Günlük denge:** S ← min(TAW, S + yağış − yüzey akışı) ; ETa = Ks·ETc ;
  Ks = 1 ya da S / RAW sınırı (p = 0,5; patates 0,35).
* **Tam sulama:** S, RAW sınırının altına inince TAW'a kadar doldurulur → net ihtiyaç.
* **Sınırlı su:** ETa, kuru tarım ETa'sı ile ETc arasında uygulanan suyla doğrusal.
* **Brüt su:** net / randıman (damla 0,90, yağmurlama 0,75, salma 0,60). 1 mm = 1 m³/da.
* **Nadas:** nadas yılı yağışının %20'si sonraki ürüne kalır (varsayım).
* **Örtü bitkisi:** sonraki ürünün başlangıç suyundan 60 mm alır (varsayım).

## 3. Verim ve gelir (FAO-33)

* 1 − Ya/Ym = Ky · (1 − ETa/ETc)
* Ya = Ym · su oranı · iklim stresi çarpanı · önceki ürün çarpanı
* İklim stresi (varsayım): hassas dönemde Tmax hem ürün eşiğini hem yerel gün-yıl
  90. yüzdeliğini aşarsa günde −%1,5; don −%3/gün; hasatta > 25 mm yağış −%2/gün;
  toplam en fazla −%50. Yerel 90. yüzdelik kuralı, bölgenin olağan sıcağına uyumlu
  çeşitlerin "stres" sayılmasını önler.
* Önceki ürün etkisi (`rotation_effects.csv`): baklagil → tahıl +%10 verim ve
  %6 maliyet tasarrufu; pancar → pancar −%25 (nematod) vb. Literatür aralıklarının
  ortası; **varsayım** etiketli.
* Brüt kâr = Ya · fiyat − değişken maliyet · (1 − azot tasarrufu) − su m³ · su maliyeti + destek.
* Fiyat ve maliyetler 2026 varsayımıdır (`basin_economics.csv`).

## 4. Stres testi ve risk

* Plan, geçmişin her ardışık 4 yıllık penceresinde oynatılır (1982–85, 1983–86, …);
  böylece kurak yılların art arda gelmesi gibi gerçek diziler korunur.
* **Ortalama brüt kâr:** tüm pencere × yılların ortalaması.
* **Kötü dönem geliri (CVaR %5):** en kötü %5 dönemin yıllık ortalama kârı. Yıl yerine
  dönem kullanılır; planlı nadas yılı "kötü yıl" sayılmaz.
* **Gelecek:** NEX-GDDP-CMIP6 aylık değişim katsayıları (sıcaklığa ekle, yağışı çarp)
  geçmiş günlük seriye uygulanır; kaydırıcılar aynı yöntemle çalışır.

## 5. Kurallar (rules-as-code)

* `tables/rules/*.yaml`; motor: `basinshift/knowledge/rules.py`.
* Konya 2026: mısır/patates/pancar 4 yılda ≤ 2 ve art arda değil; havza ürün deseni.
  İlk ihlal yılı **sarı**, ertesi yıl da sürerse **kırmızı**. Kırmızıdan itibaren tüm destek kesilir (İl Müdürlüğü
  açıklaması). Sarı yılda o yılın desteğinin sıfır sayılması bizim yorumumuzdur (destek "münavebeye uygun üretene"
  ödenir). Kural, tebliğ haberleri ve Bakanlık belgesiyle 14.11.2026'da kontrol edildi; kaynaklar ve hâlâ varsayım
  olan destek kalemleri: docs/VERIFICATION_LOG.md.
* Tavsiye kuralları (hastalık ara verme süreleri, aynı aile art arda) kartları
  filtreler (ayarlanabilir) ve toprak "zararlı döngüsü" skorunu düşürür.

## 6. Toprak sağlığı (uydudan ölçülmez)

| Alt skor | Hesap |
|---|---|
| Azot bağlama | 100 · min(1, baklagil yılı / 2) |
| Organik madde | 100 · ortalama ürün katkısı (+ örtü bitkisi bonusu) |
| Erozyon / çıplak toprak | 100 · (1 − ortalama çıplak ay / 12); eğim > 2° ise ceza artar |
| Zararlı döngüsü | 100 − 25 · ara verme ihlali − 10 · aynı aile art arda |

## 7. Optimizasyon

* Havzanın ürünleriyle tüm 4 yıllık sıralamalar taranır. Konya'da 13 ürün var; çok yıllık yonca öneri dışında
  tutulduğu için taranan plan sayısı 12⁴ = **20.736**'dır (ekrandaki sayı da budur).
* Kısıtlar: kuru tarıma uygunluk, ekipman, sözleşme, alıcı, istenmeyen ürün, yem alt sınırı.
  Çok yıllık bitkiler (yonca) tek yıl modellendiği için öneri kartlarına girmez; mevcut planda seçilebilir.
* Yalnızca yasal olarak **yeşil** planlar kartlara aday.
* Pareto: ortalama kâr ↑, kötü dönem geliri ↑, su ↓, toprak ↑ (yem ağırlığı > 0 ise yem ↑).
* Kartlar: Kâr (en yüksek ortalama), Akifer (en iyi kârın ≥ %50'si, kötü dönemde zarar
  yok, ≤ %30 zararlı yıl → en az su; kuru tarımda en yüksek kötü dönem geliri),
  Denge (öncelik ağırlıklı skor; tek planlar ve %30/50/70 tarla bölme karışımları yarışır).

## 8. Havza modeli

* Temsili çiftlik tipleri (`farm_types.csv`, **sentetik**).
* Talep: p = p_ref · (Q/Q_ref)^(1/ε); sınır [0,5; 1,2] (yerel arz azalınca ulusal pazar
  fiyat artışını sınırlar).
* **Koordinasyonsuz:** her tip geçen yılın fiyatına göre kendi LP'sini çözer; her yıl
  alanının %30'unu yeni desene kaydırır (Nerlove kısmi uyum). 12 yıl; ilk 2 yıl atılır.
* **Koordineli:** SciPy `linprog` (HiGHS). Kısıtlar: sürdürülebilir su bütçesi, yasal
  rotasyon (kararlı durumda grup payı ≤ max/pencere), pazar sınırı (fiyat %15'ten fazla
  düşmeden emilebilen miktar), yem ihtiyacı (bugünkünün %90'ı), tek ürüne en fazla pay.
* **Gölge fiyat:** su kısıtının dual değeri (para/m³).
* **Koordinasyonsuzluğun bedeli:** koordineli − koordinasyonsuz (gelir ve su).
* Not: Planlama dokümanı PuLP diyordu; PuLP 4 sürümünde API değiştiği ve hazır çözücü
  kaldırıldığı için aynı HiGHS çözücüsünü kullanan SciPy tercih edildi.

## 9. Uydudan ürün geçmişi

HLS NDVI: ilkbahar (Nis–May) ve yaz sonu (15 Tem–Ağu) tepe değerleri → kışlık/erken,
yazlık ya da nadas. Yalnızca ürün grubunu ayırt eder; tür ayrımı için Prithvi (yol haritası).

## 10. Bilinen sınırlar

* Yılda tek ana ürün (Pencap'taki çeltik-buğday çift ürünü yol haritasında).
* Yonca çok yıllıktır ama yıl yıl modellenir.
* Fiyat oynaklığı stres testinde yok (yalnızca havza katmanında fiyat tepkisi var).
* Tarla içi toprak/eğim farkları yok; iklim verisi 0,5° (bölge ölçeği).
