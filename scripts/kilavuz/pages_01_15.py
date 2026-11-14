"""
BasinShift Kılavuzu: Sayfa 1 - 15
"""
import os
from fpdf.enums import XPos, YPos
from pdf_builder import (
    NAVY, CADET, BLUE, YELLOW, RED, GREEN, AMBER,
    SLATE_DARK, SLATE_MED, SLATE_LIGHT, BG_LIGHT, BG_CARD, BORDER_COLOR
)

LOGO_IMG = r"c:\Users\yunus\Desktop\spaceapps\theme\NASA Space Apps Logos - 2026\Space Apps Logo Color and Black.png"
IMG_DIR = r"c:\Users\yunus\Desktop\spaceapps\pdf_extracted_images"
DIAG_3TIER = os.path.join(IMG_DIR, "page_04_1_X25.png")
IMG_1MM = os.path.join(IMG_DIR, "page_11_1_X57.png")
IMG_BUCKET = os.path.join(IMG_DIR, "page_12_1_X66.png")
IMG_EFF = os.path.join(IMG_DIR, "page_13_1_X69.png")
IMG_KY = os.path.join(IMG_DIR, "page_14_1_X73.png")


def render_pages_01_15(pdf):
    # =========================================================================
    # SAYFA 1: KAPAK
    # =========================================================================
    pdf.add_exact_page("Kapak")
    pdf.set_fill_color(250, 252, 255)
    pdf.rect(0, 0, 210, 297, "F")
    
    # Üst dekoratif şerit
    pdf.set_fill_color(*NAVY)
    pdf.rect(0, 0, 210, 8, "F")
    pdf.set_fill_color(*BLUE)
    pdf.rect(0, 8, 210, 2, "F")
    pdf.set_fill_color(*YELLOW)
    pdf.rect(0, 10, 45, 1.5, "F")
    
    pdf.set_y(18)
    if os.path.exists(LOGO_IMG):
        pdf.image(LOGO_IMG, x=16, y=18, w=48)
        
    pdf.set_xy(70, 22)
    pdf.set_font("DejaVu", "B", 8.5)
    pdf.set_text_color(*BLUE)
    pdf.cell(0, 4, "NASA SPACE APPS CHALLENGE 2026 · KONYA & KÜRESEL ETKİNLİK", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    pdf.set_x(70)
    pdf.set_font("DejaVu", "", 8)
    pdf.set_text_color(*SLATE_MED)
    pdf.cell(0, 4, "Field Shift: Adapting Farms with NASA Data · Kapsamlı Başvuru ve Kullanım Kılavuzu", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    pdf.ln(16)
    pdf.set_font("DejaVu", "B", 34)
    pdf.set_text_color(*NAVY)
    pdf.cell(0, 14, "BasinShift", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    pdf.set_font("DejaVu", "B", 13.5)
    pdf.set_text_color(*BLUE)
    pdf.cell(0, 7, "Saha Dönüşümü Karar Destek Aracı ve Havza Su Dengesi Optimizasyonu", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    pdf.set_font("DejaVu", "I", 9.5)
    pdf.set_text_color(*SLATE_MED)
    pdf.cell(0, 6, "Öğretici Sunum, Bilimsel Metodoloji, Algoritmik Modelleme ve Kullanıcı Kılavuzu (v2.0 Güncellemesi)", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(4)
    
    pdf.callout(
        "YÖNETİCİ ÖZETİ VE SİSTEM MİSYONU",
        "BasinShift; çiftçinin önümüzdeki 4 yılını 40+ yıllık gerçek NASA iklim serileriyle (POWER, GPM, SMAP, GRACE, "
        "SRTM ve SoilGrids) sınayan, Resmi Gazete Eylül 2026 Tarımsal Destekleme Kararnamesi kurallarına tam uyum sağlayan, "
        "20.736 farklı rotasyon permütasyonunu Pareto etkinlik sınırında optimize ederek gerekçesiyle açıklayan ve "
        "küresel emtia piyasaları (CBOT / Euronext) ile sanal su ihracatını entegre eden bütünleşik karar destek platformudur.",
        "info"
    )
    pdf.ln(2)
    
    pdf.metrics([
        ("20.736", "Olası Rotasyon", "4 Yıllık Kombinasyon", NAVY),
        ("8 / 8", "Doğrulanmış Veri", "[OK] Canlı NASA & Global", GREEN),
        ("1.468 ₺/da", "2026 Destekleme", "Temel + Su Kısıtı (Buğday)", BLUE),
        ("739", "Konya Obruk Sayısı", "GRACE: −1,3 cm/yıl", RED)
    ])
    pdf.ln(2)
    
    pdf.set_font("DejaVu", "B", 8.8)
    pdf.set_text_color(*NAVY)
    pdf.cell(0, 5, "ÖRNEK DÖNÜŞÜM DÖNGÜSÜ (ÇUMRA HAVZASI SÜRDÜRÜLEBİLİR PLAN)", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(1)
    
    pdf.metrics([
        ("1. YIL (2027)", "Yem Bitkisi (Fiğ)", "Toprağa Azot & Dinlenme", BLUE),
        ("2. YIL (2028)", "Ekmeklik Buğday", "1.468 ₺/da Destek & Gıda", GREEN),
        ("3. YIL (2029)", "Nohut / Baklagil", "Sıfır Sulama / Azot Kazancı", AMBER),
        ("4. YIL (2030)", "Yağlık Ayçiçeği", "1.541 ₺/da Destek / Düşük Su", RED),
    ])
    pdf.ln(4)
    
    # Alt Durum Çubuğu
    pdf.set_fill_color(*NAVY)
    pdf.rect(16, pdf.get_y(), 178, 13, "F")
    bar_y = pdf.get_y()
    pdf.set_xy(22, bar_y + 2)
    pdf.set_font("DejaVu", "B", 7.8)
    pdf.set_text_color(*YELLOW)
    pdf.cell(100, 4, "[OK] SİSTEM DURUMU: %100 GERÇEK NASA VE SOILGRIDS VERİLERİ AKTİF", align="L")
    pdf.set_font("DejaVu", "", 7.2)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(68, 4, "Konya, 14–15 Kasım 2026", align="R", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    pdf.set_xy(22, bar_y + 6.8)
    pdf.set_font("DejaVu", "", 7.2)
    pdf.set_text_color(203, 213, 225)
    pdf.cell(100, 4, "Geliştirici: BasinShift Çekirdek Ekibi · Python 3.11 / Streamlit / SciPy / xarray", align="L")
    pdf.cell(68, 4, "Lisans: Açık Kaynak (MIT)", align="R")
    
    pdf.set_fill_color(*NAVY)
    pdf.rect(0, 289, 210, 8, "F")
    pdf.set_fill_color(*BLUE)
    pdf.rect(0, 287, 210, 2, "F")

    # =========================================================================
    # SAYFA 2: İÇİNDEKİLER
    # =========================================================================
    pdf.add_exact_page("İçindekiler")
    pdf.set_font("DejaVu", "B", 18)
    pdf.set_text_color(*NAVY)
    pdf.cell(0, 9, "İçindekiler", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    pdf.set_draw_color(*BLUE)
    pdf.set_line_width(0.8)
    pdf.line(16, pdf.get_y(), 35, pdf.get_y())
    pdf.set_draw_color(*BORDER_COLOR)
    pdf.set_line_width(0.3)
    pdf.line(35, pdf.get_y(), 194, pdf.get_y())
    pdf.ln(5)
    
    toc_data = [
        ("01", "BasinShift'e Kısa Bakış (Giriş ve Yönetici Özeti)", "3"),
        ("02", "Yarışma ve Görev: NASA Space Apps Challenge 2026", "5"),
        ("03", "Sorun: Konya'dan Dünyaya (739 Obruk ve Akifer Çöküşü)", "7"),
        ("04", "Temel Kavramlar: Sıfırdan Zirveye (Agronomi, Su ve Ekonomi)", "9"),
        ("4.1", "Tarla, Ekim Nöbeti ve Fenoloji", "9"),
        ("4.2", "Su Bütçesi: FAO-56 Penman-Monteith, ET0, TAW ve RAW", "11"),
        ("4.3", "Verim Fonksiyonu (Ky), Maliyet ve Brüt Kâr", "14"),
        ("4.4", "Yeni 2026 Tarımsal Destekleri ve Su Kısıtı Kuralları (Sarı/Kırmızı Kart)", "15"),
        ("4.5", "Uydu ve İklim Verisi Kavramları: Çözünürlük Piramidi", "16"),
        ("4.6", "Risk ve Çok Boyutlu Karar: CVaR, Pareto ve Gölge Fiyat", "18"),
        ("05", "Çözüm: BasinShift'in Dört Temel İlkesi", "20"),
        ("06", "Veriler: Ne, Nereden, Nerede? (%100 Gerçek NASA & Global Veri Doğrulaması)", "22"),
        ("07", "Hesap Nasıl Yapılıyor? (11 Adımlı Matematiksel Modelleme Hattı)", "24"),
        ("08", "Arayüz Turu: Her Ekran, Her Grafik ve Görsel Rehber", "27"),
        ("09", "Adım Adım Kullanım: 3 Gerçekçi Senaryo", "41"),
        ("10", "Kodun Yapısı, Mimarisi ve Yazılım Mühendisliği", "44"),
        ("11", "Kurulum, Çalıştırma ve Canlı Veri İndirme Rehberi", "47"),
        ("12", "Küresel Ticaret, Emtia Piyasaları ve Sanal Su (YENİ STRATEJİK BÖLÜM)", "50"),
        ("13", "Hedef Kitle, Çiftçi Deneyimi, İş Modeli ve Jüri Savunması (YENİ BÖLÜM)", "56"),
        ("Ek A", "Kısaltmalar ve Terimler Sözlüğü", "62"),
        ("Ek B", "Kaynakça, Bilimsel Literatür ve NASA API Referansları", "64"),
    ]
    
    for code, title, page in toc_data:
        is_main = len(code) == 2 or code.startswith("Ek")
        if is_main:
            pdf.ln(1)
            pdf.set_font("DejaVu", "B", 8.2)
            pdf.set_text_color(*NAVY)
            pdf.cell(14, 4.6, code, align="L")
            pdf.cell(146, 4.6, title, align="L")
            pdf.set_text_color(*BLUE)
            pdf.cell(18, 4.6, page, align="R", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        else:
            pdf.set_font("DejaVu", "", 7.5)
            pdf.set_text_color(*SLATE_DARK)
            pdf.cell(8, 4.0, "", align="L")
            pdf.cell(12, 4.0, code, align="L")
            pdf.cell(140, 4.0, title, align="L")
            pdf.set_text_color(*SLATE_MED)
            pdf.cell(18, 4.0, page, align="R", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            
    pdf.ln(4)
    pdf.callout(
        "KILAVUZ KULLANIM NOTU (SÜRÜM 2.0)",
        "Bu kılavuz, projenin hem teknik agronomik hesaplamalarını (FAO-56, AquaCrop mantığı, Pareto optimizasyonu) "
        "hem de yarışma jürisi ve son kullanıcı çiftçiler için pratik kullanım adımlarını eksiksiz kapsayacak şekilde "
        "güncellenmiştir. Tüm tablolar ve hesaplamalar canlı projedeki 8/8 gerçek NASA verileri ve Eylül 2026 resmi "
        "destekleme mevzuatıyla birebir eşleşmektedir.",
        "verified"
    )

    # =========================================================================
    # SAYFA 3: BÖLÜM 01 - BASINSHIFT'E KISA BAKIŞ (GİRİŞ)
    # =========================================================================
    pdf.add_exact_page("Bölüm 01 · BasinShift'e Kısa Bakış")
    pdf.chapter_title(
        "01",
        "BasinShift'e Kısa Bakış",
        "Bu bölümü okuyan kişi, projenin ne yaptığını tek cümleyle anlatabilir ve kılavuzun geri kalanında nereye bakacağını bilir."
    )
    
    pdf.section_title("Tek Cümleyle Tanım")
    pdf.body(
        "BasinShift, çiftçinin önümüzdeki 4 yıl için düşündüğü ekim planını son 44 yılın gerçek NASA iklim verileriyle "
        "ve 2040'ların CMIP6 iklim projeksiyonlarıyla sınayan, resmi tarımsal destekleme kurallarına (su kısıtı ve rotasyon "
        "mevzuatı) uyan en kârlı ve en dayanıklı planları 20.736 olasılık arasından kendisi bulup gerekçesiyle açıklayan ve "
        "aynı kararı havzadaki tüm çiftçiler verirse yeraltı suyuna, obruk oluşumuna ve küresel emtia dengesine ne olacağını "
        "gösteren bütünleşik bir karar destek sistemidir."
    )
    pdf.body(
        "Adındaki iki kelime projenin çift yönlü ölçeğini simgeler: Basin (Havza: Suyu aynı akifere süzülen, aynı yeraltı "
        "suyunu paylaşan ortak coğrafi alan) ve Shift (Kaydırmak/Dönüştürmek: Ekim desenini tükenen suya ve değişen iklime "
        "uyumlu olarak sürdürülebilir ürünlere doğru bilimsel ve ekonomik temelde kaydırmak)."
    )
    
    pdf.section_title("Ne Yapıyor? Üç Katmanlı Mimari")
    pdf.body(
        "BasinShift, sorunu tek bir ölçeğe sıkıştırmaz; mikro ölçekten makro ölçeğe uzanan üç entegre katmanda çalışır:"
    )
    pdf.bullet("1. Katman · Tarla (Planını Sına):", "Çiftçi mevcut tarlasının koordinatını, toprak yapısını, kuyu derinliğini ve "
               "alışılagelmiş 4 yıllık ekim planını (ör. Mısır-Pancar-Mısır-Pancar) girer. Sistem, bu planı 1981-2025 arasındaki 44 yıllık "
               "gerçek NASA hava koşullarında oynatır; su tüketimini, reel maliyetleri, net kârı ve kırmızı kart kural ihlallerini raporlar.")
               
    pdf.bullet("2. Katman · Öneri (Daha İyisini Bul ve Nedenini Açıkla):", "Konya havzasındaki 12 ürünün tüm 4 yıllık permütasyonları "
               "(12^4 = 20.736 plan) elenir. Kural dışı olanlar (sarı/kırmızı kart) elendikten sonra, 3 boyutlu Pareto Analizi ile üç "
               "stratejik kart seçilir: Denge (En yüksek Sharpe oranı), Kâr (Maksimum nakit getiri) ve Akifer (Maksimum su tasarrufu). "
               "Her kartın altında doğal dille formüle edilmiş 'Neden bu plan?' gerekçesi ve tek sayfalık indirilebilir resmi PDF karne yer alır.")
               
    pdf.bullet("3. Katman · Havza ve Küresel Boyut (Hepimiz Yaparsak Ne Olur?):", "Bütün çiftçiler sadece kendi kısa vadeli kârına bakarak "
               "aşırı su çekerse akifer çöker ('Ortak Malların Trajedisi'). BasinShift, binlerce çiftçinin toplam su çekimini NASA GRACE "
               "uydu verileriyle ilişkilendirir; koordinasyonsuzluğun havzaya maliyetini (Price of Anarchy) ve suyun gölge fiyatını "
               "(Shadow Price) hesaplar. Ayrıca CBOT/Euronext emtia paritesi ve sanal su ihracatı dengesini ortaya koyar.")

    # =========================================================================
    # SAYFA 4: BÖLÜM 01 - KİMİN İÇİN? PAYDAŞ MATRİSİ & ŞEMA
    # =========================================================================
    pdf.add_exact_page("Bölüm 01 · Kimin İçin? Paydaş Matrisi")
    pdf.section_title("Kimin İçin? Paydaş ve Kullanıcı Rolleri Matrisi")
    pdf.body(
        "BasinShift, sahadaki pratik çiftçiden Bakanlık düzeyindeki politika yapıcılara kadar çok paydaşlı bir kullanıcı kitlesine hitap eder:"
    )
    
    headers = ["Kullanıcı Profili", "Temel Sorusu ve İhtiyacı", "BasinShift'teki Karşılığı"]
    rows = [
        ["Küçük Aile Çiftçisi", "Önümüzdeki 4 yıl ne ekersem desteğimi kaybetmem, borcumu öderim ve kuyum kurumaz?", "Tarla -> 3 Tıkla Karar -> Renkli Kartlar -> Basit Karne"],
        ["Ziraat Mühendisi / Danışman", "Toprağın TAW/RAW su kapasitesi nedir? Hangi fenolojik evrede su stresi oluşur?", "İklim Geçmişi -> Su Dengesi Tablosu -> Mühendis Görünümü"],
        ["Ziraat Bankası & Tarım Kredi", "Kredi verdiğim üreticinin 4 yıllık ekim planı kuraklığa ve iflasa dayanıklı mı?", "Karne (Tek sayfalık Risk ve Su Karnesi, CVaR risk skoru)"],
        ["TARSİM (Tarım Sigortaları)", "Bu parselin aşırı sıcak ve kuraklık frekansı nedir? Sigorta prim riski ne?", "44 Yıllık NASA POWER İklim Stresi ve Aşırı Olay Frekansları"],
        ["Şeker Fabrikaları / Alıcılar", "Sözleşmeli pancar/mısır ekimi için çiftçinin su kotası ve rotasyon hakkı var mı?", "Yasal Kural Motoru (Mevzuat Uyum Denetimi & Sarı/Kırmızı Kart)"],
        ["DSİ & Tarım Bakanlığı", "Havzada ürün deseni nasıl kaydırılırsa akifer seviyesi dengelenir, su tasarrufu ne olur?", "Havza Görünümü -> Gölge Su Fiyatı -> Koordinasyon Kazancı"],
        ["NASA Space Apps Jürisi", "NASA'nın açık uydu verileri sahada gerçek bir sorunu bilimsel olarak çözüyor mu?", "Yöntem ve Veriler -> 8/8 Gerçek Veri Matrisi -> Doğrulama Paneli"]
    ]
    pdf.table(headers, rows, [38, 75, 65], ["L", "L", "L"])
    
    if os.path.exists(DIAG_3TIER):
        pdf.figure(DIAG_3TIER, "BasinShift'in Üç Ölçekli Mimarisi: Tek Tarla Analizi -> Çok Kriterli Öneri Kartları -> Havza ve Küresel Su Dengesi", max_h=55, max_w=165)

    # =========================================================================
    # SAYFA 5: BÖLÜM 02 - YARIŞMA VE GÖREV
    # =========================================================================
    pdf.add_exact_page("Bölüm 02 · Yarışma ve Görev")
    pdf.chapter_title(
        "02",
        "Yarışma ve Görev",
        "BasinShift neden bu biçimde tasarlandı? Çünkü NASA Space Apps Challenge 2026'nın en kritik saha görevine yanıt veriyor."
    )
    
    pdf.section_title("NASA Space Apps Challenge Nedir?")
    pdf.body(
        "NASA Space Apps Challenge, NASA'nın (Amerikan Ulusal Havacılık ve Uzay Dairesi) dünya genelinde her yıl düzenlediği "
        "dünyanın en büyük küresel hackathonudur. Yüzlerce şehirde aynı anda binlerce araştırmacı, mühendis, yazılımcı ve agronomist "
        "bir araya gelerek NASA'nın halka açık yer gözlem, iklim ve uydu verilerini kullanarak Dünya'nın ve insanlığın en acil "
        "sorunlarına çözüm üretir. 14–15 Kasım 2026 Konya yerel etkinliği, Türkiye'nin tahıl ambarı ve aynı zamanda en büyük yeraltı suyu "
        "krizi bölgesi olan Konya Kapalı Havzası'nda gerçekleştirilmiştir."
    )
    
    pdf.section_title("Görev: Field Shift (Adapting Farms with NASA Data)")
    pdf.body(
        "Yarışmanın 'Field Shift: Adapting Farms with NASA Data' (Saha Dönüşümü: Çiftlikleri NASA Verileriyle Uyarlamak) görevi, "
        "takımlardan şu temel soruyu çözmelerini istemektedir:"
    )
    
    pdf.callout(
        "NASA FIELD SHIFT GÖREV TANIMININ ÖZÜ",
        "İklim değişikliği; sıcaklık rejimlerini, yağış düzenlerini ve su mevcudiyetini hızla değiştirmektedir. Çiftçiler nesillerdir "
        "sürdürdükleri geleneksel ekim alışkanlıklarını sürdüremez hale gelmiştir. Çiftçilerin yeni iklim gerçeklerine uyum sağlayabilmesi "
        "için tarlaya özgü koşulları, su kısıtlarını, yerel mevzuat kurallarını ve pazar gerçeklerini dikkate alarak ürün desenini "
        "akıllıca dönüştüren (shift), NASA'nın açık yer gözlem verilerini anlaşılır karar mekanizmalarına çeviren araçlar geliştirilmelidir.",
        "info"
    )
    
    pdf.body(
        "BasinShift bu misyonu yalnızca teorik bir veri görselleştirmesi olarak değil, çiftçinin cebine, tarlanın toprağına ve "
        "bölgesel su güvenliğine doğrudan dokunan uygulanabilir bir mühendislik ürünü olarak ele almıştır."
    )

    # =========================================================================
    # SAYFA 6: BÖLÜM 02 - BEKLENTİLER VE TAŞINABİLİRLİK
    # =========================================================================
    pdf.add_exact_page("Bölüm 02 · NASA Beklentileri & Küresel Taşınabilirlik")
    pdf.section_title("NASA Beklentileri ve BasinShift'teki Birebir Karşılıkları")
    
    headers = ["NASA'nın Beklentisi", "Geleneksel Yaklaşımların Eksiği", "BasinShift'teki Somut Çözüm"]
    rows = [
        ["Açık NASA Verilerini Kullanmak", "Sadece hava durumu API'si veya genel uydu fotoğrafları göstermek", "8/8 Gerçek Veri: POWER günlük iklim, GPM yağış, SMAP nem, GRACE akifer, SRTM eğim, CMIP6 iklim"],
        ["Tarlaya Özel Çözüm Sunmak", "Bütün ilçeye veya bölgeye tek bir ürün önermek", "Parsel koordinatına özel toprak yapısı (SoilGrids), kuyu derinliği, eğim ve çiftlik tipolojisi"],
        ["Çiftçinin Kısıtlarını Dikkate Almak", "Pratikte uygulanamayacak kuramsal ürünler dayatmak", "Su kotası, sulama altyapısı (damla/yağmurlama), makine parkuru, sözleşme, pazar ve yem ihtiyacı"],
        ["Yasal Mevzuata Tam Uyum", "Resmi teşvikleri ve tarım politikası cezalarını göz ardı etmek", "Eylül 2026 Destekleme Kararnamesi kuralları, su kısıtı ilçeleri, sarı ve kırmızı kart kural motoru"],
        ["Açıklanabilirlik ve Güven", "Kara kutu yapay zekâ ile kaynağı belirsiz tavsiyeler vermek", "Tamamen deterministik agronomik formüller (FAO-56), şeffaf su bütçesi ve doğal dille 'Neden?' izahatı"],
        ["Çiftçi Dostu Anlaşılır Arayüz", "Karmaşık bilimsel terimlerle çiftçiyi boğmak", "3 Tıkla Karar sade görünümü, renkli risk/kâr kartları, tek sayfalık Risk ve Su Karnesi"],
        ["Taşınabilirlik (Scalability)", "Sadece tek bir köye veya tarlaya sıkışıp kalmak", "Yapılandırılabilir havza mimarisi: Konya'dan Hindistan Pencap ve ABD California havzalarına tam uyum"]
    ]
    pdf.table(headers, rows, [42, 60, 76], ["L", "L", "L"])
    
    pdf.section_title("Yerelden Küresele Ölçeklenebilirlik")
    pdf.body(
        "BasinShift'in çekirdek motoru coğrafyadan bağımsızdır. Sistem, Konya Kapalı Havzası'ndaki 739 obruk ve aşırı yeraltı suyu "
        "kullanımı için sıfırdan doğrulanmış olsa da, mimari küreseldir. Örneğin Hindistan Pencap havzasında pirinç-buğday monokültürünün "
        "yarattığı akifer krizine veya Kaliforniya Central Valley'deki badem-yonca kuraklık baskısına, sadece ilgili havzanın yerel "
        "ürün tablosu (`crops.yaml`) ve su kuralları (`rules.yaml`) tanımlanarak dakikalar içinde uyarlanabilmektedir."
    )

    # =========================================================================
    # SAYFA 7: BÖLÜM 03 - SORUN: KONYA'DAN DÜNYAYA
    # =========================================================================
    pdf.add_exact_page("Bölüm 03 · Sorun: Konya'dan Dünyaya")
    pdf.chapter_title(
        "03",
        "Sorun: Konya'dan Dünyaya",
        "Çiftçinin önünde basit görünen ama aslında devasa bir matematiksel ve ekolojik kriz var: 'Önümüzdeki 4 yıl ne ekeyim?'"
    )
    
    pdf.section_title("Konya Kapalı Havzası Hidrolojisi ve Akifer Krizi")
    pdf.body(
        "Kapalı havza; yağmur ve kar suyunun denizlere akmayıp havza tabanındaki göllere veya yer altı akiferine süzüldüğü coğrafyalardır. "
        "Konya Kapalı Havzası, Türkiye tarım arazilerinin yaklaşık %13'ünü barındırır ve 'Türkiye'nin Tahıl Ambarı' olarak anılır. "
        "Ancak bölgenin yıllık ortalama yağışı yalnızca 320–350 mm civarındadır (yarı kurak iklim). Buna karşılık buğdayın su ihtiyacı "
        "yaklaşık 400–450 mm, dane mısırın 700–800 mm ve şeker pancarının 850–1.000 mm'dir. Aradaki devasa açık, on binlerce derin kuyu ile "
        "yeraltı suyundan çekilmektedir."
    )
    pdf.body(
        "Son 30 yılda havzadaki derin kuyu sayısı 100.000'i aşmış (çoğu ruhsatsız), yeraltı su seviyesi her yıl ortalama 1 ila 3 metre "
        "derine düşmüş, bazı bölgelerde statik su seviyesi 40 metreden 150–200 metreye kadar gerilemiştir. NASA GRACE uydu ölçümleri, "
        "Konya havzası akifer kütlesinin her yıl ortalama 1,3 cm eşdeğer su kalınlığı kaybettiğini doğrulamaktadır."
    )
    
    pdf.section_title("739 Obruk: Akifer Çöküşünün Somut Jeolojik Kanıtı")
    pdf.body(
        "Aşırı su çekimi sadece suyun bitmesi anlamına gelmez; havza jeolojisinin fiziksel olarak çökmesine neden olur. Karstik kireçtaşı "
        "tabakalarındaki yeraltı boşlukları, suyun kaldırma kuvveti kalktığında aniden çökmekte ve tarım arazilerinin ortasında devasa "
        "obruklar (sinkholes) meydana gelmektedir. 2026 yılı itibarıyla Konya havzasında kayıtlı obruk sayısı 739'a ulaşmıştır. "
        "Bu obruklar tarım makinelerini, yolları ve köyleri doğrudan tehdit eden fiziksel bir felakettir."
    )

    # =========================================================================
    # SAYFA 8: BÖLÜM 03 - SORU NEDEN BU KADAR ZOR? (20.736 PLAN)
    # =========================================================================
    pdf.add_exact_page("Bölüm 03 · Soru Neden Bu Kadar Zor?")
    pdf.section_title("Soru Neden Bu Kadar Zor? (20.736 Olasılık)")
    pdf.body(
        "Bir çiftçi 'Önümüzdeki 4 yıl ne ekmeliyim?' diye düşündüğünde insan beyninin sezgisel kapasitesini aşan dört temel zorlukla karşılaşır:"
    )
    pdf.bullet("1. Seçenek Sayısının Çokluğu (Kombinatorik Patlama):", "Konya havzasında 12 temel ürün bulunmaktadır (Buğday, Arpa, "
               "Dane Mısır, Silajlık Mısır, Şeker Pancarı, Yağlık Ayçiçeği, Nohut, Kuru Fasulye, Mercimek, Patates, Aspir, Nadas). "
               "4 yıllık bir plan için olası kombinasyon sayısı 12 x 12 x 12 x 12 = 20.736 farklı rotasyondur. Hiçbir çiftçi veya danışman "
               "bu 20.736 planın kârını, su tüketimini ve kuraklık riskini kafasında hesaplayamaz.")
               
    pdf.bullet("2. İklimin Aşırı Dalgalanması ve Şoklar:", "Bir ürün ortalama bir yılda harika kâr bırakabilir; fakat son 44 yılın "
               "verileri göstermektedir ki Konya'da her 4-5 yılda bir şiddetli kuraklık, ilkbahar geç donu veya aşırı sıcak hava dalgası "
               "yaşanmaktadır. Üst üste iki kurak yıla denk gelen yüksek su talepli bir plan (ör. Mısır-Pancar), çiftçiyi iflasa sürükler.")
               
    pdf.bullet("3. Rotasyon Bağımlılığı ve Fitopatolojik Riskler:", "Yıllar birbirinden bağımsız değildir. Aynı tarlaya üst üste mısır "
               "ekildiğinde mısır kurdu ve kök çürüklüğü riski katlanır, azot tükenir. Pancar üst üste ekildiğinde nematod zararlısı toprağı "
               "felç eder. Buna karşılık buğdaydan önce fiğ veya nohut ekilirse, baklagiller toprağa saf organik azot bağlar ve buğday verimi %15 artar.")
               
    pdf.bullet("4. Yeni 2026 Su Kısıtı Mevzuatı (Sarı ve Kırmızı Kart):", "Eski yıllarda çiftçi suyu çekip dilediğini ekebiliyordu. "
               "Eylül 2026 kararnamesiyle su kısıtı ilçelerinde 4 yılda 2'den fazla mısır/pancar eken veya ardışık eken çiftçilerin "
               "bütün tarımsal destekleri kesilmekte (kırmızı kart) ve 5 yıl men cezası uygulanmaktadır.")
               
    pdf.callout(
        "ORTAK MALLARIN TRAJEDİSİ (TRAGEDY OF THE COMMONS)",
        "Akifer tüm çiftçilerin ortak mülküdür. Her çiftçi kendi bireysel kârını maksimize etmek için yüksek su isteyen mısır ve pancar "
        "ekerse, bireysel olarak doğru gibi görünen bu karar toplumsal olarak akiferin tamamen kurumasına ve su kuyularının tuzlanmasına yol açar. "
        "BasinShift, tarladaki bireysel kâr ile havzadaki kolektif hidrolojik dengeyi ilk kez aynı matematiksel modelde birleştirmektedir.",
        "danger"
    )

    # =========================================================================
    # SAYFA 9: BÖLÜM 04 - 4.1 TARLA VE EKİM
    # =========================================================================
    pdf.add_exact_page("Bölüm 04 · 4.1 Tarla ve Ekim")
    pdf.chapter_title(
        "04",
        "Temel Kavramlar: Sıfırdan Zirveye",
        "Uygulamayı ve algoritmaları anlamak için tarım, hidroloji, ekonomi ve uydu kavramları sıfırdan, adım adım anlatılmıştır."
    )
    
    pdf.section_title("4.1 Tarla ve Ekim Nöbeti (Rotasyon)")
    pdf.body(
        "Dekar (da) Türkiye tarımında standart arazi birimidir: 1 da = 1.000 m² (yaklaşık 31,6 m × 31,6 m). Uluslararası "
        "literatürde hektar (ha) kullanılır: 1 ha = 10 da = 10.000 m². Kılavuzdaki tüm tarla hesapları dekar (da) bazındadır."
    )
    pdf.body(
        "Ekim nöbeti (münavebe / rotasyon), aynı parselde her yıl aynı ürünü ekmek yerine, farklı kök derinliklerine, su tüketimlerine "
        "ve besin ihtiyaçlarına sahip bitkilerin belirli bir sırayla ardışık olarak ekilmesidir. Monokültür (sürekli aynı ürünü ekmek), "
        "topraktaki belirli mikro besin elementlerini tüketir, aynı kök zararlılarının (nematod, mısır kurdu, mantari kök çürüklükleri) "
        "çoğalmasına neden olur ve toprağın biyolojik canlılığını öldürür."
    )
    pdf.body(
        "Konya Kapalı Havzası'nda modelimize dahil edilen 12 temel ürün grubu şunlardır:\n"
        "1) Ekmeklik Buğday, 2) Yemlik Arpa, 3) Dane Mısır, 4) Silajlık Mısır, 5) Şeker Pancarı, 6) Yağlık Ayçiçeği, "
        "7) Nohut, 8) Kuru Fasulye, 9) Kırmızı/Yeşil Mercimek, 10) Patates, 11) Yağlık Aspir, 12) Nadas. "
        "(Yonca çok yıllık bir yem bitkisi olduğu için 4 yıllık yıllık rotasyon optimizasyonuna sokulmaz; münferit yem tarlası olarak değerlendirilir)."
    )

    # =========================================================================
    # SAYFA 10: BÖLÜM 04 - 4.1 ÖN BİTKİ ETKİSİ VE BAKLAGİLLER
    # =========================================================================
    pdf.add_exact_page("Bölüm 04 · 4.1 Ön Bitki Etkisi")
    pdf.section_title("Ön Bitki Etkisi (Preceding Crop Effect) ve Toprak Sağlığı")
    pdf.body(
        "Ön bitki etkisi; bir tarlada hasat edilen ürünün kendisinden sonra gelen ürüne bıraktığı biyolojik, kimyasal ve fiziksel mirastır. "
        "Yıllar birbirinden bağımsız değildir; bu yıl ekilen ürün gelecek yılın verimini doğrudan tayin eder:"
    )
    pdf.bullet("Baklagillerin Biyolojik Mirası (Nohut, Fiğ, Mercimek):", "Köklerindeki Rhizobium bakterileri vasıtasıyla atmosferdeki "
               "azotu organik forma dönüştürüp toprağa bağlar. Kendisinden sonra ekilen buğday veya arpaya dekarda 4–6 kg saf azot bırakır. "
               "Bu sayede buğday verimi %10–15 artarken çiftçinin kimyasal üre/amonyum sülfat gübre faturası %20–30 düşer.")
               
    pdf.bullet("Kök Derinliği Dengesi:", "Sığ köklü buğday (0.8–1.0 m) üst toprak katmanındaki besinleri alırken, derin köklü ayçiçeği "
               "ve aspir (1.5–2.0 m) toprağın derinliklerindeki su ve mineralleri yukarı çeker, toprağın sıkışmış taban taşını kırar.")
               
    pdf.bullet("Hastalık ve Yabancı Ot Kırıcı Etki:", "Geniş yapraklı bir ürünün (ayçiçeği/nohut) ardından dar yapraklı bir hububat "
               "(buğday/arpa) ekildiğinde, hububata musallat olan kök boğazı çürüklüğü ve sarı pas gibi mantari hastalıkların yaşam döngüsü kırılır.")
               
    pdf.callout(
        "KONYA'DA YANLIŞ BİLİNEN ALIŞKANLIK: MISIR ÜSTÜNE MISIR",
        "Çumra ve Karapınar'da pek çok üretici yüksek gelir hevesiyle üst üste dane mısır ekmektedir. "
        "Oysa ikinci yıl mısır kurdu popülasyonu 4 katına çıkmakta, toprak azot bakımından tükenmekte ve dekara fazladan "
        "15 kg kimyasal azot gübresi atılmak zorunda kalınmaktadır. Bu hem yeraltı sularının nitratla kirlenmesine yol açar "
        "hem de çiftçinin net kârını eritir.",
        "warning"
    )

    # =========================================================================
    # SAYFA 11: BÖLÜM 04 - 4.2 SU: 1 MM SU VE FAO-56 PENMAN-MONTEITH
    # =========================================================================
    pdf.add_exact_page("Bölüm 04 · 4.2 Su ve FAO-56")
    pdf.section_title("4.2 Su: 1 mm Su Ne Demek? ve FAO-56 Penman-Monteith")
    pdf.body(
        "1 mm yağış veya sulama suyu, 1 m² alana 1 litre su düşmesi demektir. 1 dekar 1.000 m² olduğundan:\n"
        "1 mm su = 1 m³/da = 1 ton su/da anlamına gelir. Uygulamada sulama suyu bu yüzden 'm³/da' birimiyle verilir. "
        "Örneğin 'Mısır 600 m³/da su istedi' demek, o tarlaya dekarda 600 ton su basıldığı anlamına gelir."
    )
    
    if os.path.exists(IMG_1MM):
        pdf.figure(IMG_1MM, "1 mm Yağışın Fiziksel Anlamı: 1 m²'ye 1 Litre = 1 Dekara 1 Ton Su", max_h=35, max_w=140)
        
    pdf.subsection_title("FAO-56 Penman-Monteith Referans Buharlaşma (ET0) Standardı")
    pdf.body(
        "Atmosferin buharlaştırma gücünü ölçen uluslararası standart FAO-56 Penman-Monteith yöntemidir. BasinShift, "
        "NASA POWER uydusundan çektiği günlük 7 meteorolojik değişkenle her gün için ET0'ı hesaplar:"
    )
    pdf.callout(
        "PENMAN-MONTEITH REFERANS ET0 FORMÜLÜ",
        "ET0 = [ 0.408 * Δ * (Rn - G) + γ * (900 / (T + 273)) * u2 * (es - ea) ] / [ Δ + γ * (1 + 0.34 * u2) ]\n"
        "Rn: Net radyasyon (MJ/m²/gün), G: Toprak ısı akısı, T: 2m ortalama sıcaklık (°C), u2: 2m rüzgar hızı (m/s), "
        "(es - ea): Doymuş buhar basıncı açığı (kPa), Δ: Buhar basıncı eğimi, γ: Psikrometrik sabit.",
        "info"
    )

    # =========================================================================
    # SAYFA 12: BÖLÜM 04 - 4.2 TOPRAK SU DEPOSU (KOVA MODELİ: TAW & RAW)
    # =========================================================================
    pdf.add_exact_page("Bölüm 04 · 4.2 Toprak Su Deposu (Kova Modeli)")
    pdf.section_title("Toprak Su Deposu: TAW ve RAW (Kova Prensibi)")
    pdf.body(
        "Toprak, bitkinin kök bölgesinde suyu depolayan doğal bir sünger gibidir:"
    )
    pdf.bullet("Doygunluk (Saturation):", "Topraktaki tüm gözeneklerin suyla dolduğu durumdur. Havalanma durur, fazla su yerçekimiyle süzülür.")
    pdf.bullet("Tarla Kapasitesi (FC):", "Yerçekimi süzülmesi bittikten sonra toprak taneciklerinin tutabildiği maksimum faydalı su seviyesidir.")
    pdf.bullet("Sürekli Solma Noktası (WP):", "Toprağın suyu aşırı sıkı tuttuğu, bitki köklerinin emiş gücünün yetmediği ve solmanın başladığı alt sınırdır.")
    pdf.bullet("Toplam Kullanılabilir Su (TAW):", "TAW = 1.000 * (FC - WP) * Zr (mm). FC ve WP SoilGrids'ten çekilir; Zr kök derinliğidir.")
    pdf.bullet("Kolay Alınabilir Su (RAW):", "RAW = p * TAW. Bitki su stresi yaşamadan bu suyu rahatça tüketir. p katsayısı mısırda 0.55, buğdayda 0.65'tir.")

    if os.path.exists(IMG_BUCKET):
        pdf.figure(IMG_BUCKET, "Toprak Su Deposu Kova Prensibi: Tarla Kapasitesi, Stres Eşiği (RAW) ve Solma Noktası", max_h=45, max_w=150)

    # =========================================================================
    # SAYFA 13: BÖLÜM 04 - 4.2 SULAMA RANDIMANI VE ENERJİ MALİYETİ
    # =========================================================================
    pdf.add_exact_page("Bölüm 04 · 4.2 Sulama Randımanı ve Enerji")
    pdf.section_title("Sulama Yöntemleri, Randıman ve Pompa Elektrik Maliyeti")
    pdf.body(
        "Kuyudan çekilen suyun tamamı bitkiye ulaşmaz; kanallarda sızar, rüzgarda savrulur veya tarla yüzeyinden buharlaşır. "
        "Bitki köküne ulaşan faydalı suyun kuyudan çekilen brüt suya oranına sulama randımanı (η) denir:"
    )
    pdf.bullet("Damla Sulama (η = %90):", "Suyu doğrudan kök bölgesine damlatır. Buharlaşma minimumdur, rüzgardan etkilenmez.")
    pdf.bullet("Yağmurlama Sulama (η = %75):", "Borular ve fıskiyelerle havaya püskürtülür. Rüzgarda ve sıcak saatlerde buharlaşma kaybı %25'e çıkar.")
    pdf.bullet("Salma / Vahşi Sulama (η = %50):", "Araziden kontrolsüzce akıtılır. Suyun yarısı kaybolur; toprağı tuzlandırır ve taban taşını bozar.")
    
    if os.path.exists(IMG_EFF):
        pdf.figure(IMG_EFF, "Sulama Yöntemlerinin Randıman Karşılaştırması: Damla (%90), Yağmurlama (%75), Salma (%50)", max_h=35, max_w=140)
        
    pdf.subsection_title("Kuyu Derinliği ve Elektrik Pompaj Maliyeti")
    pdf.body(
        "Konya havzasında su derinliği arttıkça 1 m³ suyu yüzeye çıkarmanın elektrik maliyeti katlanarak artar:\n"
        "Enerji (kWh/m³) = (Derinlik * g) / (3.600.000 * η_pompa). 120 metre derinlikteki bir kuyudan su çeken çiftçi, "
        "40 metredeki çiftçiye kıyasla 3 kat daha fazla elektrik faturası öder."
    )

    # =========================================================================
    # SAYFA 14: BÖLÜM 04 - 4.3 VERİM FONKSİYONU VE BRÜT KÂR
    # =========================================================================
    pdf.add_exact_page("Bölüm 04 · 4.3 Verim ve Ekonomi")
    pdf.section_title("4.3 Verim Fonksiyonu (Ky) ve Brüt Kâr Hesabı")
    pdf.body(
        "Topraktaki su RAW seviyesinin altına indiğinde bitki su stresine girer ve verim kaybı başlar. "
        "Verim kaybı FAO-33 / FAO-56 Stewart su-verim azalış denklemiyle hesaplanır:"
    )
    pdf.callout(
        "FAO STEWART SU-VERİM AZALIŞ EŞİTLİĞİ",
        "(1 - Ya / Ym) = Ky * (1 - ETa / ETc)\n"
        "Ym: Potansiyel maksimum verim, Ya: Gerçekleşen fiili verim, ETc: İdeal su ihtiyacı, ETa: Karşılanan fiili su tüketimi. "
        "Ky: Bitkinin su açığına duyarlılık katsayısıdır. Ky > 1 olan ürünler (ör. Dane Mısır Ky=1.25) su kısıtına karşı aşırı hassastır; "
        "su %20 azalırsa verim %25 çöker. Kuraklığa dayanıklı aspir (Ky=0.7) veya nohutta (Ky=0.6) ise verim kaybı çok daha hafiftir.",
        "info"
    )
    
    if os.path.exists(IMG_KY):
        pdf.figure(IMG_KY, "FAO-56 Su-Verim Azalış Eğrisi (Ky) ve Aşırı Sıcaklık/Don Verim Kaybı Fonksiyonu", max_h=38, max_w=145)
        
    pdf.subsection_title("Brüt Kâr Formülasyonu")
    pdf.body(
        "Brüt Kâr (₺/da) = [ Verim (kg/da) * Satış Fiyatı (₺/kg) ] + Tarımsal Destekler (₺/da) - Değişken Maliyetler (₺/da)\n"
        "Değişken maliyetler tohum, gübre, ilaç, mazot, işçilik ve kuyu elektrik enerjisini kapsar. "
        "Kırmızı kart alan planlarda devlet desteği 0 ₺'ye düşerken su maliyeti ikiye katlanır."
    )

    # =========================================================================
    # SAYFA 15: BÖLÜM 04 - 4.4 YENİ 2026 DESTEKLERİ VE SU KISITI KURALLARI
    # =========================================================================
    pdf.add_exact_page("Bölüm 04 · 4.4 Yeni 2026 Destekleri")
    pdf.section_title("4.4 Yeni 2026 Tarımsal Destekleme Mevzuatı (Sarı ve Kırmızı Kart)")
    pdf.body(
        "Resmi Gazete'de yayımlanan Eylül 2026 Tarımsal Destekleme Kararnamesi ile temel destek katsayısı birimi 367 ₺/da olarak belirlenmiştir. "
        "Su kısıtı ilan edilen Konya havzası ilçelerinde şu devrim niteliğindeki kurallar uygulanmaktadır:"
    )
    
    headers = ["Ürün Adı", "Temel Katsayı", "Temel Destek", "Su Kısıtı İlavesi", "Toplam Destek", "2026 Fiyatı", "Borsa / Alıcı"]
    rows = [
        ["Ekmeklik Buğday", "2.6", "954 ₺/da", "+514 ₺/da", "1.468 ₺/da", "16,50 ₺/kg", "TMO Taban Fiyat"],
        ["Yemlik Arpa", "2.6", "954 ₺/da", "+514 ₺/da", "1.468 ₺/da", "12,75 ₺/kg", "TMO Taban Fiyat"],
        ["Yağlık Ayçiçeği", "3.0", "1.101 ₺/da", "+440 ₺/da", "1.541 ₺/da", "34,00 ₺/kg", "Karadenizbirlik / Trakya"],
        ["Nohut / Fasulye", "2.0", "734 ₺/da", "+294 ₺/da", "1.028 ₺/da", "42,00 ₺/kg", "Serbest Piyasa / Borsa"],
        ["Aspir (Yağlık)", "2.0", "734 ₺/da", "+294 ₺/da", "1.028 ₺/da", "26,00 ₺/kg", "Sözleşmeli Sanayi"],
        ["Şeker Pancarı", "1.8", "660 ₺/da", "0 ₺ (Kota Primi)", "660 ₺/da", "3,72 ₺/kg", "TÜRKŞEKER Alımı"],
        ["Dane Mısır", "0.0*", "0 ₺/da", "0 ₺ (Kısıt)", "0 ₺/da", "11,50 ₺/kg", "TMO Taban Fiyat"],
        ["Patates", "0.0*", "0 ₺/da", "0 ₺ (Kısıt)", "0 ₺/da", "9,50 ₺/kg", "Tüccar / Hal Fiyatı"],
    ]
    pdf.table(headers, rows, [28, 20, 24, 26, 26, 24, 30], ["L", "C", "C", "C", "C", "C", "L"])
    
    pdf.subsection_title("Sarı ve Kırmızı Kart Kural Mekanizması")
    pdf.bullet("Sarı Kart:", "Su kısıtı ilçelerindeki sulu alanlarda 4 yılda 2'den fazla aşırı su tüketen ürün (mısır/patates/pancar) ekilmesi. "
               "İlk ihlalde o yılın tüm temel ve mazot/gübre destekleri iptal edilir.")
    pdf.bullet("Kırmızı Kart:", "Aşırı su tüketen ürünlerin art arda iki yıl ekilmesi veya su kısıtı kurallarının mükerrer ihlali. "
               "Kırmızı kart alan çiftçi ÇKS havza planlama mevzuatı gereği 5 YIL BOYUNCA HİÇBİR DEVLET DESTEĞİ ALAMAZ.")
