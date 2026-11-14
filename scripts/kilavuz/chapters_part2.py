"""
BasinShift Kılavuzu - Kısım 2: Bölüm 4, 5, 6, 7
"""
import os
from fpdf.enums import XPos, YPos
from pdf_builder import (
    NAVY, CADET, BLUE, YELLOW, RED, GREEN, AMBER,
    SLATE_DARK, SLATE_MED, SLATE_LIGHT, BG_LIGHT, BG_CARD, BORDER_COLOR
)

IMG_DIR = r"c:\Users\yunus\Desktop\spaceapps\pdf_extracted_images"
IMG_1MM = os.path.join(IMG_DIR, "page_11_1_X57.png")
IMG_BUCKET = os.path.join(IMG_DIR, "page_12_1_X66.png")
IMG_EFF = os.path.join(IMG_DIR, "page_13_1_X69.png")
IMG_KY = os.path.join(IMG_DIR, "page_14_1_X73.png")
IMG_RISK = os.path.join(IMG_DIR, "page_18_1_X95.png")
IMG_PARETO = os.path.join(IMG_DIR, "page_18_2_X96.png")


def build_chapter_04(pdf):
    pdf.chapter_header(
        "04",
        "Temel Kavramlar: Sıfırdan Zirveye",
        "Uygulamayı ve algoritmaları anlamak için tarım, hidroloji, ekonomi ve uydu kavramları sıfırdan, adım adım anlatılmıştır."
    )
    
    # 4.1 Tarla ve Ekim
    pdf.section_header("4.1 Tarla ve Ekim Nöbeti (Rotasyon)")
    pdf.body_p(
        "Dekar (da) Türkiye tarımında standart arazi birimidir: 1 da = 1.000 m² (yaklaşık 31,6 m × 31,6 m). Uluslararası "
        "literatürde hektar (ha) kullanılır: 1 ha = 10 da = 10.000 m². Kılavuzdaki tüm tarla hesapları dekar (da) bazındadır."
    )
    pdf.body_p(
        "Ekim nöbeti (münavebe / rotasyon), aynı parselde her yıl aynı ürünü ekmek yerine, farklı kök derinliklerine, su tüketimlerine "
        "ve besin ihtiyaçlarına sahip bitkilerin belirli bir sırayla ardışık olarak ekilmesidir. Monokültür (sürekli aynı ürünü ekmek), "
        "topraktaki belirli mikro besin elementlerini tüketir, aynı kök zararlılarının (nematod, mısır kurdu, mantari kök çürüklükleri) "
        "çoğalmasına neden olur ve toprağın biyolojik canlılığını öldürür."
    )
    pdf.body_p(
        "Ön bitki etkisi (preceding crop effect): Kendisinden sonra ekilecek ürüne bırakılan biyolojik ve kimyasal mirastır. "
        "Örneğin nohut, mercimek veya fiğ gibi baklagiller, havadaki serbest azotu köklerindeki Rhizobium bakterileri vasıtasıyla "
        "toprağa bağlar ve dekara 4–6 kg saf organik azot bırakır. Ertesi yıl ekilen ekmeklik buğday bu azottan faydalanarak "
        "%10–15 daha yüksek verim verir ve gübre maliyeti %20 düşer."
    )
    
    # 4.2 Su ve Hidroloji
    pdf.section_header("4.2 Su ve Hidroloji Dengesi")
    pdf.body_p(
        "1 mm yağış veya sulama, 1 m² alana 1 litre su düşmesi demektir. 1 dekar 1.000 m² olduğundan, 1 mm = 1 m³/da = 1 ton su/da anlamına gelir. "
        "Örneğin bir tarlaya '500 mm su verildi' denildiğinde, dekara 500 m³ (500 ton) su çekildiği anlaşılır."
    )
    
    if os.path.exists(IMG_1MM):
        pdf.figure(IMG_1MM, "1 mm Yağışın Fiziksel Anlamı: 1 m²'ye 1 Litre = 1 Dekara (1.000 m²) 1 m³ (1 Ton) Su", max_h=35, max_w=140)
        
    pdf.subsection_header("Referans Evapotranspirasyon (ET0) ve Bitki Su Tüketimi (ETc)")
    pdf.body_p(
        "Bitkiler suyu iki yolla atmosfere geri verir: topraktan buharlaşma (evaporation) ve yapraklardan terleme (transpiration). "
        "İkisinin toplamına Evapotranspirasyon (ET) denir. FAO-56 standardı gereğince sistem, her gün için referans çim yüzey buharlaşmasını "
        "(ET0) Penman-Monteith denklemi ile hesaplar:"
    )
    
    pdf.callout(
        "FAO-56 PENMAN-MONTEITH REFERANS BUHARLAŞMA DENKLEMİ",
        "ET0 = [ 0.408 * Δ * (Rn - G) + γ * (900 / (T + 273)) * u2 * (es - ea) ] / [ Δ + γ * (1 + 0.34 * u2) ]\n"
        "Burada: Rn net güneş radyasyonu (MJ/m²/gün), G toprak ısı akısı, T ortalama sıcaklık (°C), u2 2 metredeki rüzgar hızı (m/s), "
        "(es - ea) doymuş buhar basıncı açığı (kPa), Δ buhar basıncı eğrisi eğimi ve γ psikrometrik sabittir. "
        "BasinShift bu denklemi NASA POWER'dan çektiği günlük 7 meteorolojik değişkenle her gün için tam fiziksel olarak çözer.",
        "info"
    )
    
    pdf.body_p(
        "Gerçek bitki su ihtiyacı (ETc) ise bitki katsayısı (Kc) ile hesaplanır: ETc = Kc * ET0. Bitkinin Kc katsayısı fide döneminde "
        "düşük (0.3–0.4), en hızlı büyüdüğü ve dane bağladığı dönemde tepe noktasına (1.05–1.20) ulaşır, hasada doğru tekrar geriler."
    )
    
    pdf.subsection_header("Toprak Su Deposu: TAW ve RAW (Kova Modeli)")
    pdf.body_p(
        "Toprak, bitkinin kök bölgesinde su tutan gözenekli bir sünger veya 'kova' gibidir:"
    )
    pdf.bullet("Tarla Kapasitesi (FC):", "Şiddetli bir yağıştan veya sulamadan 1-2 gün sonra yerçekimiyle süzülemeyen, toprakta asılı kalan maksimum su miktarıdır.")
    pdf.bullet("Sürekli Solma Noktası (WP):", "Toprağın suyu o kadar sıkı tuttuğu noktadır ki kökler artık ememez; bitki geri dönüşsüz solar.")
    pdf.bullet("Toplam Kullanılabilir Su (TAW):", "FC ile WP arasındaki farktır. TAW = 1.000 * (FC - WP) * Zr (mm). Zr kök derinliğidir.")
    pdf.bullet("Kolayca Alınabilir Su (RAW):", "TAW'ın belli bir kesridir: RAW = p * TAW (genellikle p = 0.4 - 0.6). Topraktaki su RAW seviyesinin "
               "altına indiğinde bitki kuraklık stresine girer ve verim kaybı başlar.")

    if os.path.exists(IMG_BUCKET):
        pdf.figure(IMG_BUCKET, "Toprak Su Deposu Kova Prensibi: Doygunluk, Tarla Kapasitesi (FC), Stres Eşiği (RAW) ve Solma Noktası (WP)", max_h=45, max_w=150)
        
    pdf.subsection_header("Sulama Yöntemi ve Randıman")
    pdf.body_p(
        "Kuyudan çekilen elektrik ve suyun tamamı bitkinin köküne ulaşmaz. Kanallarda buharlaşma, rüzgarla savrulma ve derin sızma kayıpları "
        "olur. Kök bölgesine ulaşan net suyun kuyudan pompalanan brüt suya oranına sulama randımanı (η) denir:"
    )
    pdf.bullet("Damla Sulama (η = %90):", "Suyu doğrudan kök boğazına verir. Buharlaşma minimumdur, rüzgardan etkilenmez.")
    pdf.bullet("Yağmurlama (η = %75):", "Havaya püskürtülür. Rüzgarda ve sıcak saatlerde buharlaşma kaybı %25'e çıkar.")
    pdf.bullet("Salma / Vahşi Sulama (η = %50):", "Tarla yüzeyinden akıtılır. Suyun yarısı buharlaşır veya derine kaçarak ziyan olur.")
    
    if os.path.exists(IMG_EFF):
        pdf.figure(IMG_EFF, "Sulama Yöntemlerinin Randıman Karşılaştırması: Damla (%90), Yağmurlama (%75), Salma (%50)", max_h=35, max_w=140)

    # 4.3 Verim ve Ekonomi
    pdf.section_header("4.3 Verim Fonksiyonu, Maliyetler ve Brüt Kâr")
    pdf.body_p(
        "Su yetersiz kaldığında bitkinin yaşayacağı verim kaybı, dünyaca kabul görmüş FAO-33 / FAO-56 Stewart su-verim azalış denklemiyle hesaplanır:"
    )
    pdf.callout(
        "FAO STEWART SU-VERİM AZALIŞ MODELİ",
        "(1 - Ya / Ym) = Ky * (1 - ETa / ETc)\n"
        "Burada Ym o tarlanın potansiyel maksimum verimi, Ya elde edilen gerçek verim, ETc potansiyel su ihtiyacı, ETa karşılanabilen fiili su "
        "tüketimidir. Ky bitkinin su stresine duyarlılık katsayısıdır. Ky ne kadar büyükse (ör. Dane Mısır Ky=1.25), su kısıtında verim o kadar "
        "feci düşer. Kuraklığa dayanıklı aspir veya nohutta ise Ky düşüktür (0.6–0.8), su azalsa da verim büyük çöküş yaşamaz.",
        "info"
    )
    
    if os.path.exists(IMG_KY):
        pdf.figure(IMG_KY, "FAO-56 Su-Verim Azalış İlişkisi (Ky Eğrisi) ve Aşırı Sıcaklık Stres Katsayıları", max_h=40, max_w=145)
        
    pdf.subsection_header("Fiyatlandırma, Maliyetler ve Brüt Kâr")
    pdf.body_p(
        "Tarımsal kâr hesabı tek bir brüt satış tutarı değildir. Sistemde Brüt Kâr şu formülle hesaplanır:"
    )
    pdf.body_p(
        "Brüt Kâr (₺/da) = [ Verim (kg/da) * Satış Fiyatı (₺/kg) ] + Tarımsal Destekler (₺/da) - Değişken Maliyetler (₺/da)\n"
        "Değişken Maliyetler; tohum, kimyasal ve organik gübre, bitki koruma ilaçları, traktör mazotu, işçilik ve en önemlisi "
        "kuyu derinliğine bağlı elektrik pompa enerjisi maliyetidir. Kuyu ne kadar derindeyse (ör. 150 m), çekilen her metreküp suyun "
        "elektrik faturası o kadar kabarır."
    )
    
    # 4.4 Kurallar: Sarı ve Kırmızı Kart (Eylül 2026 Mevzuatı)
    pdf.section_header("4.4 Yeni 2026 Tarımsal Destekleri ve Su Kısıtı Kuralları (Sarı ve Kırmızı Kart)")
    pdf.body_p(
        "Resmi Gazete'de yayımlanan Eylül 2026 Tarımsal Destekleme Kararnamesi ile Türkiye'de tarımsal destekleme sistemi kökten değişmiş, "
        "katsayı modeli yürürlüğe girmiştir. Yeni modelde temel destek birim katsayısı 367 ₺/da olarak belirlenmiştir."
    )
    
    pdf.callout(
        "EYLÜL 2026 RESMİ DESTEKLEME MODELİ VE SU KISITI İLÇELERİ",
        "Yeraltı sularının kritik seviyeye indiği Konya Kapalı Havzası ilçelerinde (Çumra, Karapınar, Cihanbeyli, vb.) "
        "çiftçileri su tasarruflu ürünlere yönlendirmek için devrim niteliğinde iki kural yürürlüktedir:\n"
        "1. Su Kısıtı İlave Desteği: Su istemeyen veya az isteyen buğday, arpa, ayçiçeği ve baklagillere temel desteğin üzerine "
        "ekstra su kısıtı hibesi verilmektedir.\n"
        "2. Dane Mısır ve Patatese Sıfır Destek: Su kısıtı ilçelerindeki sulu arazilerde ekilen dane mısır ve patatese su kısıtı desteği "
        "tamamen SIFIRLANMIŞTIR (0 ₺/da). Ayrıca üst üste iki yıl ekilirse kırmızı kart uygulanır.",
        "warning"
    )
    
    headers = ["Ürün Adı", "Temel Katsayı", "Temel Destek (₺/da)", "Su Kısıtı İlavesi (₺/da)", "Toplam Destek (₺/da)", "2026 Fiyatı (₺/kg)", "2026 Alıcı / Borsa"]
    rows = [
        ["Ekmeklik Buğday", "2.6", "954 ₺", "+514 ₺", "1.468 ₺/da", "16,50 ₺", "TMO Taban Fiyat"],
        ["Yemlik Arpa", "2.6", "954 ₺", "+514 ₺", "1.468 ₺/da", "12,75 ₺", "TMO Taban Fiyat"],
        ["Yağlık Ayçiçeği", "3.0", "1.101 ₺", "+440 ₺", "1.541 ₺/da", "34,00 ₺", "Karadenizbirlik / Trakya B."],
        ["Nohut / Fasulye", "2.0", "734 ₺", "+294 ₺", "1.028 ₺/da", "42,00 ₺", "Serbest Piyasa / Borsa"],
        ["Aspir (Yağlık)", "2.0", "734 ₺", "+294 ₺", "1.028 ₺/da", "26,00 ₺", "Sözleşmeli Sanayi"],
        ["Şeker Pancarı", "1.8", "660 ₺", "0 ₺ (Kota Primi)", "660 ₺/da", "3,72 ₺", "TÜRKŞEKER Kota Alımı"],
        ["Dane Mısır", "0.0*", "0 ₺", "0 ₺ (Kısıt)", "0 ₺/da", "11,50 ₺", "TMO Taban Fiyat"],
        ["Patates", "0.0*", "0 ₺", "0 ₺ (Kısıt)", "0 ₺/da", "9,50 ₺", "Tüccar / Hal Fiyatı"],
    ]
    pdf.table(headers, rows, [28, 20, 26, 28, 28, 24, 24], ["L", "C", "C", "C", "C", "C", "L"])
    
    pdf.subsection_header("Sarı ve Kırmızı Kart Ceza Mekanizması")
    pdf.bullet("Sarı Kart:", "4 yıllık plan döneminde aşırı su tüketen ürünlerin (mısır, patates, şeker pancarı) rotasyon sınırını aşması "
               "(4 yılda en fazla 2 kez ekilebilir). İlk ihlalde o yılın tüm temel ve mazot/gübre destekleri iptal edilir.")
    pdf.bullet("Kırmızı Kart:", "Aşırı su tüketen ürünlerin art arda iki yıl ekilmesi veya su kısıtı bölgesinde izinsiz su kuyusu açılması. "
               "Kırmızı kart gören üretici ÇKS (Çiftçi Kayıt Sistemi) havza planlama mevzuatı gereği 5 YIL BOYUNCA HİÇBİR DEVLET DESTEĞİ ALAMAZ.")

    # 4.5 Uydu ve İklim Verisi
    pdf.section_header("4.5 Uydu ve İklim Verisi Kavramları: Çözünürlük Piramidi")
    pdf.body_p(
        "Tek bir tarla meteoroloji istasyonu sadece birkaç yüz metrelik mikro alandan bilgi verir ve sensör arızalarına açıktır. "
        "Buna karşılık NASA uydu filosu, Dünya'yı farklı spektral ve mekansal çözünürlüklerde sürekli tarar. BasinShift, "
        "çözünürlük piramidini doğru basamaklarda birleştirir:"
    )
    pdf.bullet("30 Metre (Parsel Ölçeği):", "SRTM Sayısal Yükseklik Modeli (eğim ve topoğrafya) ve Harmonized Landsat-Sentinel (HLS) 30m NDVI.")
    pdf.bullet("250 Metre (Toprak Ölçeği):", "ISRIC SoilGrids toprak katmanları (kum, kil, silt, organik karbon, hacim ağırlığı).")
    pdf.bullet("10 Kilometre (Yağış Ölçeği):", "NASA GPM IMERG 0.1° x 0.1° uydu yağış radarı.")
    pdf.bullet("30-50 Kilometre (Atmosferik İklim):", "NASA POWER Agroclimatology 0.5° x 0.625° günlük güneş radyasyonu ve sıcaklık verisi.")
    pdf.bullet("300 Kilometre (Akifer Kütlesi):", "NASA GRACE / GRACE-FO Tellus Mascon yeraltı suyu gravitasyonel anomali ölçümü.")

    # 4.6 Risk ve Karar
    pdf.section_header("4.6 Risk ve Çok Boyutlu Karar: CVaR, Pareto ve Gölge Fiyat")
    pdf.body_p(
        "Geleneksel tarım modellerinin en büyük hatası sadece 'ortalama bir yılın kârını' hesaplamaktır. Tarımda çiftçiyi zengin eden "
        "ortalamalar değil, kurak yıllardaki batış riski belirler. BasinShift iki modern finansal ve matematiksel optimizasyon metriği kullanır:"
    )
    pdf.bullet("Kötü Dönem Geliri (CVaR - Conditional Value at Risk):", "Bir planın 44 yıllık geçmişteki en kötü %5'lik döneminde (yani "
               "en şiddetli 2 kuraklık döneminde) getirdiği ortalama yıllık gelirdir. Çiftçinin borçlarını ödeyebilme ve tarlasını kaybetmeme sigortasıdır.")
    pdf.bullet("3 Boyutlu Pareto Etkinlik Sınırı:", "Bir planın hem Brüt Kârını maksimize eden, hem Su Tüketimini minimize eden, hem de "
               "CVaR Riskini düşüren çözümler kümesidir. 20.736 plan taranır; başka bir plana göre hem daha az kazandıran hem daha çok su tüketen "
               "tüm 'baskılanmış' (dominated) planlar elenir. Geriye kalan optimal sınır Pareto Sınırı'dır.")
    pdf.bullet("Suyun Gölge Fiyatı (Shadow Price of Water):", "Doğrusal programlama (LP) modellerinde kısıt olan bir birim ilave kaynağın "
               "(1 m³ suyun) çiftçiye veya havzaya yaratacağı marjinal ekonomik değerdir. Örneğin gölge fiyat 8,39 ₺/m³ ise, damla sulama ile "
               "kurtarılan her metreküp suyun sisteme net kazancı 8,39 ₺'dir.")

    if os.path.exists(IMG_RISK) and os.path.exists(IMG_PARETO):
        pdf.figure(IMG_RISK, "Risk Dağılımı (CVaR): Alışılmış Planın Sol Kuyruk Çöküşü vs BasinShift Denge Planının Güvenli Getirisi", max_h=40, max_w=145)
        pdf.figure(IMG_PARETO, "Çok Boyutlu Pareto Sınırı: Kâr, Su Tüketimi ve Kötü Dönem Geliri Arasındaki Denge", max_h=40, max_w=145)


def build_chapter_05(pdf):
    pdf.chapter_header(
        "05",
        "Çözüm: BasinShift'in Dört Temel İlkesi",
        "Kavramlar yerine oturduktan sonra BasinShift'in çözümü dört sarsılmaz bilimsel ilkeye dayanır."
    )
    
    pdf.section_header("İlke 1 · Planı 40 Yılın Gerçek Havasıyla Sına")
    pdf.body_p(
        "Mevcut tarım danışmanlığı araçları 'varsayımsal ortalama bir yıl' için tavsiye verir. Oysa Konya'da ortalama bir yıl diye bir şey yoktur; "
        "bir yıl aşırı kurak, ertesi yıl donlu, üçüncü yıl ise aşırı yağışlı geçer. BasinShift, çiftçinin aklındaki 4 yıllık planı "
        "1981–2025 arasındaki 44 yıllık gerçek meteorolojik koşullarda kayan pencerelerle (1982–1985, 1983–1986, ..., 2022–2025 olmak üzere "
        "tam 41 bağımsız dönemde) sınar. Plan, geçmişin en zorlu kuraklıklarında batmışsa elenir."
    )
    
    pdf.section_header("İlke 2 · Kurallara ve Çiftçi Kısıtlarına Uyan En İyilerini Bul")
    pdf.body_p(
        "12 ürünün 4 yıllık kombinasyonu olan 20.736 olası plan arasından önce çiftçinin tarlaya özel kısıtları (su kotası, kuyu debisi, "
        "makine parkuru, yem ihtiyacı, sözleşmeli ekim kotası) ve 2026 Tarımsal Destekleme Kararnamesi kuralları (su kısıtı ve rotasyon "
        "yasakları) filtrelenir. Sarı veya kırmızı kart alan tüm planlar çöpe atılır. Kalan binlerce geçerli plan arasından Pareto Sınırı "
        "çizilerek çiftçiye üç net alternatif sunulur: Denge, Kâr ve Akifer."
    )
    
    pdf.section_header("İlke 3 · Nedenini ve Gerekçesini Şeffafça Açıkla")
    pdf.body_p(
        "Çiftçiye 'Git şunu ek' demek ikna edici değildir. Çiftçi neden o ürünün seçildiğini, bir önceki yılın toprağa etkisini, "
        "hangi ayda ne kadar su harcayacağını ve ne kadar devlet desteği alacağını bilmek ister. BasinShift, kara kutu bir yapay zekâ "
        "modeli (halüsinasyon riski olan LLM'ler) kullanmaz. Tüm açıklamalar, FAO-56 su dengesi ve resmi destek katsayılarından doğrudan "
        "türetilen deterministik agronomik şablonlarla üretilir. Verilen hiçbir rakam uydurma olamaz."
    )
    
    pdf.section_header("İlke 4 · Tarladan Havzaya ve Küresel Pazara Bağla")
    pdf.body_p(
        "Tek bir tarla kendi başına sürdürülebilir görünse bile, havzadaki 100.000 çiftçi aynı anda aşırı su çekerse akifer çöker; ya da herkes "
        "aynı ürünü ekerse ürün arz fazlasından tarlada kalır ve fiyatlar taban yapar. BasinShift, tarladaki her kararı havza hidrolojisiyle "
        "(GRACE su kütlesi kaybı ve obruk riski) ve küresel emtia dengesiyle (CBOT/Euronext fiyatları ve sanal su ihracatı) ilişkilendirir."
    )


def build_chapter_06(pdf):
    pdf.chapter_header(
        "06",
        "Veriler: Ne, Nereden, Nerede?",
        "Jürinin ve bilim insanlarının ilk sorusu: 'Hangi NASA verisini nereden çektiniz, nasıl işlediniz?'. Cevabın tamamı bu tablodur."
    )
    
    pdf.callout(
        "🟢 %100 GERÇEK VE DOĞRULANMIŞ VERİ SETLERİ (SENTETİK VERİ DÖNEMİ BİTTİ)",
        "Projenin ilk taslaklarında kullanılan geçici sentetik veriler tamamen kaldırılmıştır. Canlı uygulamadaki tüm hesaplamalar "
        "resmi NASA API'lerinden ve küresel toprak veritabanlarından çekilen doğrulanmış 8/8 gerçek veri seti ile çalışmaktadır. "
        "Uygulamanın 'Yöntem ve Veriler' sayfasındaki doğrulama panelinde 8 veri setinin tamamı yeşil onaylı (🟢) olarak belgelenmiştir.",
        "verified"
    )
    
    headers = ["Veri Seti Kodu", "Uydu / Görev / Sağlayıcı", "Çözünürlük & Kapsam", "Hesapta Nerede Kullanılıyor?", "Erişim Metodu & Doğrulama"]
    rows = [
        ["climate_daily", "NASA POWER (Agroclimatology API)", "0,5° x 0,625°; 1981–2025 (44 Yıl)", "FAO-56 ET0, günlük su dengesi, don/aşırı sıcaklık iklim stresi, risk takvimi", "🟢 Canlı REST API / NetCDF (Doğrulandı)"],
        ["precipitation", "NASA GPM IMERG v07 (GPM_3IMERGM)", "0,1° x 0,1°; Aylık & Günlük", "Yağış doğrulaması, kuraklık indeksleri, efektif yağış fraksiyonu hesabı", "🟢 NASA GES DISC API / HDF5 (Doğrulandı)"],
        ["groundwater", "NASA/DLR GRACE & GRACE-FO Tellus", "1° Mascon (JPL / CSR); 2002–2024", "Havza yeraltı suyu kütle anomalisi, akifer düşüş eğilimi (-1,3 cm/yıl), obruk riski", "🟢 NASA PO.DAAC / NetCDF (Doğrulandı)"],
        ["soil_moisture", "NASA SMAP L3/L4 Radyometre", "9 km / 36 km; 2015–2025", "Kök bölgesi toprak nemi, su dengesi başlangıç koşulları ve doygunluk kontrolü", "🟢 NASA NSIDC DAAC (Doğrulandı)"],
        ["terrain_elevation", "NASA SRTM v3 (Shuttle Radar Topography)", "30 m (1 arc-sec); Küresel", "Parsel eğimi, yüzey akışı katsayısı, erozyon riski, topoğrafik drenaj", "🟢 USGS EarthExplorer / GeoTIFF (Doğrulandı)"],
        ["vegetation_ndvi", "NASA/USGS HLS (Harmonized Landsat-Sentinel)", "30 m; 5 Günlük Sıklık", "Bitki örtüsü dinamikleri, geçmiş fenoloji doğrulama, gerçek Kc eğrisi", "🟢 NASA LP DAAC AppEEARS (Doğrulandı)"],
        ["climate_projections", "NASA NEX-GDDP-CMIP6", "0,25° x 0,25°; 2030–2050 (SSP2-4.5/5-8.5)", "'İki Gelecek' ve '2040 İklim Senaryoları' stres testi, kuraklık simülasyonu", "🟢 NASA Center for Climate Simulation (Doğrulandı)"],
        ["soil_profile", "ISRIC SoilGrids 250m (Global Soil Profile)", "250 m; 6 Derinlik Katmanı (0-200 cm)", "Toprak bünyesi (kil, kum, silt), TAW, RAW, tarla kapasitesi (FC) ve solma noktası (WP)", "🟢 ISRIC WCS / REST API (Doğrulandı)"]
    ]
    pdf.table(headers, rows, [28, 42, 32, 44, 32], ["L", "L", "L", "L", "L"])
    
    pdf.section_header("Veri Kalitesi Güvencesi ve QA/QC Protokolü")
    pdf.body_p(
        "Uydu ve meteoroloji verilerinde yaşanabilecek sensör hataları ve eksik günlere karşı sistem katı bir QA/QC filtresinden geçer:"
    )
    pdf.bullet("Eksik Gün Tamamlama (Gap-Filling):", "NASA POWER günlük serisinde herhangi bir yılda eksik gün oranı %5'in altındaysa "
               "yakındaki komşu günlerin lineer interpolasyonu ile tamamlanır; eksik gün %5'i aşıyorsa o yıl hesaptan tamamen çıkartılır.")
    pdf.bullet("Rüzgar Hızı Yükseklik Düzeltmesi:", "Farklı sensörlerin 10 metrede ölçtüğü rüzgar hızları, FAO-56 logaritmik rüzgar profili "
               "denklemiyle [u2 = u10 * 4.87 / ln(67.8 * 10 - 5.42)] standart 2 metre yüksekliğine dönüştürülür.")
    pdf.bullet("Yağış Kalibrasyonu:", "GPM IMERG uydu yağış verileri, yerel meteoroloji istasyonu doğrulamalarıyla çarpraz kontrol edilir; "
               "aşırı yağış anomalileri yüzey akış katsayısıyla filtrelenir.")


def build_chapter_07(pdf):
    pdf.chapter_header(
        "07",
        "Hesap Nasıl Yapılıyor?",
        "Ham NASA uydusundan tarladaki karar kartına giden yol: 11 adımlı matematiksel modelleme hattı."
    )
    
    steps = [
        ("Adım 1 · Coğrafi Konum ve Toprak", "Parselin enlem-boylam koordinatı alınır. SoilGrids 250m'den 6 katmanlı toprak analizi "
         "(kil, kum, organik madde) ve SRTM'den 30m eğim çekilir. Toprağın TAW ve RAW su kapasitesi parsel bazında hesaplanır."),
         
        ("Adım 2 · Günlük FAO-56 Penman-Monteith ET0", "NASA POWER'dan 1981–2025 arasındaki 16.000+ gün için sıcaklık, radyasyon, nem ve "
         "rüzgar çekilerek her bir günün referans buharlaşması (ET0, mm/gün) fiziksel olarak hesaplanır."),
         
        ("Adım 3 · Günlük Toprak Su Dengesi Simülasyonu", "Her ürün için fenolojik takvime göre günlük Kc belirlenir. Topraktaki su bütçesi "
         "gün gün işletilir: Giriş = Yağış + Sulama; Çıkış = ETc + Derine Sızma + Yüzey Akışı. RAW'ın altına inilen günler 'su stresi' olarak kaydedilir."),
         
        ("Adım 4 · 12 Ürün x 44 Yıl Ürün-Yıl Matrisi", "Konya havzasındaki 12 ürün, 1982–2025 arasındaki 44 hasat yılının her birinde tek tek "
         "ekilmiş gibi simüle edilir (12 x 44 = 528 durum). Her durum için verim, gereken sulama suyu, kuraklık/don kaybı, maliyet ve brüt gelir hesaplanır."),
         
        ("Adım 5 · 4 Yıllık Rotasyon Penceresi Stres Testi", "12 ürünün tüm 4 yıllık kombinasyonları (12^4 = 20.736 plan), tarihteki 41 adet "
         "4 yıllık pencerede (1982-1985, 1983-1986...) geriye dönük oynatılır. Her plan için 41 farklı 4 yıllık ekonomik ve hidrolojik sonuç üretilir."),
         
        ("Adım 6 · Yasal ve Çiftçi Kısıt Süzgeci", "20.736 plan içinden; kuyu kapasitesini aşan, çiftçinin 'ekmem' dediği ürünleri içeren ve "
         "Eylül 2026 su kısıtı kurallarını ihlal eden (sarı/kırmızı kart) tüm planlar otomatik olarak elenir."),
         
        ("Adım 7 · 3 Boyutlu Pareto Optimizasyonu", "Kalan geçerli planlar 3 boyutlu uzayda sıralanır: 1) Ortalama Yıllık Brüt Kâr (Maksimum), "
         "2) Yıllık Çekilen Sulama Suyu (Minimum), 3) Kötü Dönem Geliri CVaR (Maksimum dayanıklılık). Baskın olmayan optimal Pareto Sınırı çıkarılır."),
         
        ("Adım 8 · Üç Stratejik Kartın Belirlenmesi", "Pareto sınırındaki planlardan üç özel kart seçilir:\n"
         "• Denge Kartı: Kâr / Risk oranını (Sharpe oranı) maksimize eden en dengeli plan.\n"
         "• Kâr Kartı: Kural ihlali yapmadan en yüksek parayı kazandıran plan.\n"
         "• Akifer Kartı: En az su harcayan ve yeraltı suyunu koruyan sürdürülebilir plan."),
         
        ("Adım 9 · Deterministik Gerekçe ve Neden Açıklaması", "Seçilen kartlar için doğal dilde şablon motoru çalışır. 'Neden bu plan?' sorusuna; "
         "kurtarılan su miktarı, ön bitkinin azot katkısı, kazanılan devlet desteği ve kuraklık dayanıklılığı rakamlarla tek tek yazılır."),
         
        ("Adım 10 · Çıktıların Üretilmesi ve Raporlama", "Streamlit UI ekranları dinamik olarak güncellenir; karşılaştırma tabloları, interaktif "
         "Plotly saçılım grafikleri çizilir ve tek tıklamayla resmi 'Risk ve Su Karnesi' PDF belgesi oluşturulur."),
         
        ("Adım 11 · Havza Ölçeği Entegrasyonu (LP & Nash Dengesi)", "Tarladaki kararlar havza geneline ölçeklenir. GRACE yeraltı suyu kaybı, "
         "havza koordinasyon kazancı (Price of Anarchy), suyun gölge fiyatı (Shadow Price) ve küresel emtia paritesi raporlanır.")
    ]
    
    for title, desc in steps:
        pdf.bullet(title + ":", desc, space_after=2.2)
