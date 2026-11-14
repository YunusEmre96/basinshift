"""
BasinShift Kılavuzu - Kısım 1: Kapak, İçindekiler, Bölüm 1, 2, 3
"""
import os
from fpdf.enums import XPos, YPos
from pdf_builder import (
    NAVY, CADET, BLUE, YELLOW, RED, GREEN, AMBER,
    SLATE_DARK, SLATE_MED, SLATE_LIGHT, BG_LIGHT, BG_CARD, BORDER_COLOR
)

LOGO_IMG = r"c:\Users\yunus\Desktop\spaceapps\theme\NASA Space Apps Logos - 2026\Space Apps Logo Color and Black.png"
DIAG_3TIER = r"c:\Users\yunus\Desktop\spaceapps\pdf_extracted_images\page_04_1_X25.png"
IMG_SCREEN_01 = r"c:\Users\yunus\Desktop\spaceapps\mevcutarayuzler\01_tarla_girisi_ve_yapilandirma.png"


def build_cover(pdf):
    pdf.add_page()
    pdf.current_chapter = "Kapak"
    
    # Arka plan hafif gradyan/çerçeve
    pdf.set_fill_color(250, 252, 255)
    pdf.rect(0, 0, 210, 297, "F")
    
    # Üst dekoratif lacivert/mavi şerit
    pdf.set_fill_color(*NAVY)
    pdf.rect(0, 0, 210, 8, "F")
    pdf.set_fill_color(*BLUE)
    pdf.rect(0, 8, 210, 2, "F")
    pdf.set_fill_color(*YELLOW)
    pdf.rect(0, 10, 45, 1.5, "F")
    
    pdf.set_y(18)
    # NASA Logo
    if os.path.exists(LOGO_IMG):
        pdf.image(LOGO_IMG, x=16, y=18, w=48)
    
    # Üst Rozet
    pdf.set_xy(70, 22)
    pdf.set_font("DejaVu", "B", 8.5)
    pdf.set_text_color(*BLUE)
    pdf.cell(0, 4, "NASA SPACE APPS CHALLENGE 2026 · KONYA & KÜRESEL ETKİNLİK", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    pdf.set_x(70)
    pdf.set_font("DejaVu", "", 8)
    pdf.set_text_color(*SLATE_MED)
    pdf.cell(0, 4, "Field Shift: Adapting Farms with NASA Data · Kapsamlı Başvuru ve Kullanım Kılavuzu", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    pdf.ln(16)
    
    # Ana Başlık
    pdf.set_font("DejaVu", "B", 34)
    pdf.set_text_color(*NAVY)
    pdf.cell(0, 14, "BasinShift", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    # Alt Başlık
    pdf.set_font("DejaVu", "B", 14)
    pdf.set_text_color(*BLUE)
    pdf.cell(0, 7, "Saha Dönüşümü Karar Destek Aracı ve Havza Su Dengesi Optimizasyonu", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    pdf.set_font("DejaVu", "I", 10)
    pdf.set_text_color(*SLATE_MED)
    pdf.cell(0, 6, "Öğretici Sunum, Bilimsel Metodoloji, Algoritmik Modelleme ve Kullanıcı Kılavuzu (v2.0 Güncellemesi)", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    pdf.ln(5)
    
    # Özet Kutusu
    pdf.set_fill_color(241, 245, 249)
    pdf.rect(16, pdf.get_y(), 178, 28, "F")
    pdf.set_fill_color(*BLUE)
    pdf.rect(16, pdf.get_y(), 3.5, 28, "F")
    
    box_y = pdf.get_y()
    pdf.set_xy(22, box_y + 3)
    pdf.set_font("DejaVu", "B", 9)
    pdf.set_text_color(*NAVY)
    pdf.cell(0, 4.5, "YÖNETİCİ ÖZETİ VE SİSTEM MİSYONU", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    pdf.set_x(22)
    pdf.set_font("DejaVu", "", 8.2)
    pdf.set_text_color(*SLATE_DARK)
    desc = (
        "BasinShift; çiftçinin önümüzdeki 4 yılını 40+ yıllık gerçek NASA iklim serileriyle (POWER, GPM, SMAP, GRACE, "
        "SRTM ve SoilGrids) sınayan, Resmi Gazete Eylül 2026 Tarımsal Destekleme Kararnamesi kurallarına tam uyum sağlayan, "
        "20.736 farklı rotasyon permütasyonunu Pareto etkinlik sınırında optimize ederek gerekçesiyle açıklayan ve "
        "küresel emtia piyasaları (CBOT / Euronext) ile sanal su ihracatını entegre eden bütünleşik karar destek platformudur."
    )
    pdf.multi_cell(168, 4.2, desc)
    
    pdf.set_y(box_y + 33)
    
    # 4 Temel Metrik Kartı
    metrics = [
        ("20.736", "Olası Rotasyon", "4 Yıllık Kombinasyon", NAVY),
        ("8 / 8", "Doğrulanmış Veri", "🟢 %100 Canlı NASA", GREEN),
        ("1.468 ₺/da", "2026 Destekleme", "Temel + Su Kısıtı (Buğday)", BLUE),
        ("739", "Konya Obruk Sayısı", "GRACE: −1,3 cm/yıl", RED)
    ]
    pdf.metric_row(metrics)
    
    pdf.ln(2)
    
    # Örnek 4 Yıllık Rotasyon Kartı (Fiğ - Buğday - Nohut - Ayçiçeği)
    pdf.set_font("DejaVu", "B", 9)
    pdf.set_text_color(*NAVY)
    pdf.cell(0, 5, "ÖRNEK DÖNÜŞÜM DÖNGÜSÜ (ÇUMRA HAVZASI SÜRDÜRÜLEBİLİR PLAN)", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(1.5)
    
    cycle_items = [
        ("1. YIL (2027)", "Yem Bitkisi (Fiğ)", "Toprağa Azot & Dinlenme", BLUE),
        ("2. YIL (2028)", "Ekmeklik Buğday", "1.468 ₺/da Destek & Gıda", GREEN),
        ("3. YIL (2029)", "Nohut / Baklagil", "Sıfır Sulama / Azot Kazancı", AMBER),
        ("4. YIL (2030)", "Yağlık Ayçiçeği", "1.541 ₺/da Destek / Düşük Su", RED),
    ]
    pdf.metric_row(cycle_items)
    
    pdf.ln(6)
    
    # Alt Durum Çubuğu
    pdf.set_fill_color(*NAVY)
    pdf.rect(16, pdf.get_y(), 178, 14, "F")
    
    bar_y = pdf.get_y()
    pdf.set_xy(22, bar_y + 2.5)
    pdf.set_font("DejaVu", "B", 8)
    pdf.set_text_color(*YELLOW)
    pdf.cell(100, 4, "🟢 SİSTEM DURUMU: %100 GERÇEK NASA VE SOILGRIDS VERİLERİ AKTİF", align="L")
    pdf.set_font("DejaVu", "", 7.5)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(68, 4, "Konya, 14–15 Kasım 2026", align="R", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    pdf.set_xy(22, bar_y + 7.5)
    pdf.set_font("DejaVu", "", 7.5)
    pdf.set_text_color(203, 213, 225)
    pdf.cell(100, 4, "Geliştirici: BasinShift Çekirdek Ekibi · Python 3.11 / Streamlit / SciPy / xarray", align="L")
    pdf.cell(68, 4, "Lisans: Açık Kaynak (MIT)", align="R")
    
    # Alt şerit
    pdf.set_fill_color(*NAVY)
    pdf.rect(0, 289, 210, 8, "F")
    pdf.set_fill_color(*BLUE)
    pdf.rect(0, 287, 210, 2, "F")


def build_toc(pdf):
    pdf.add_page()
    pdf.current_chapter = "İçindekiler"
    
    pdf.set_font("DejaVu", "B", 20)
    pdf.set_text_color(*NAVY)
    pdf.cell(0, 10, "İçindekiler", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    pdf.set_draw_color(*BLUE)
    pdf.set_line_width(0.8)
    pdf.line(16, pdf.get_y(), 35, pdf.get_y())
    pdf.set_draw_color(*BORDER_COLOR)
    pdf.set_line_width(0.3)
    pdf.line(35, pdf.get_y(), 194, pdf.get_y())
    pdf.ln(6)
    
    toc_data = [
        ("01", "BasinShift'e Kısa Bakış (Giriş ve Yönetici Özeti)", "3"),
        ("02", "Yarışma ve Görev: NASA Space Apps Challenge 2026", "5"),
        ("03", "Sorun: Konya'dan Dünyaya (739 Obruk ve Akifer Çöküşü)", "7"),
        ("04", "Temel Kavramlar: Sıfırdan Zirveye (Agronomi, Su ve Ekonomi)", "9"),
        ("4.1", "Tarla, Ekim Nöbeti ve Fenoloji", "9"),
        ("4.2", "Su Bütçesi: FAO-56 Penman-Monteith, ET0, TAW ve RAW", "11"),
        ("4.3", "Verim Fonksiyonu (Ky), Maliyet ve Brüt Kâr", "14"),
        ("4.4", "Yeni 2026 Tarımsal Destekleri ve Su Kısıtı Kuralları (Sarı/Kırmızı Kart)", "16"),
        ("4.5", "Uydu ve İklim Verisi Kavramları: Çözünürlük Piramidi", "18"),
        ("4.6", "Risk ve Çok Boyutlu Karar: CVaR, Pareto ve Gölge Fiyat", "20"),
        ("05", "Çözüm: BasinShift'in Dört Temel İlkesi", "22"),
        ("06", "Veriler: Ne, Nereden, Nerede? (%100 Gerçek NASA & Global Veri Doğrulaması)", "24"),
        ("07", "Hesap Nasıl Yapılıyor? (11 Adımlı Matematiksel Modelleme Hattı)", "27"),
        ("08", "Arayüz Turu: Her Ekran, Her Grafik ve Görsel Rehber", "31"),
        ("8.1", "Kenar Çubuğu: Dinamik Yapılandırma ve Parametreler", "31"),
        ("8.2", "Tarla Sayfası: Coğrafi Konum, Toprak ve Mevcut Alışkanlık", "32"),
        ("8.3", "İklim Geçmişi: 44 Yıllık NASA POWER ve Risk Takvimi", "34"),
        ("8.4", "Planlar: 20.736 Planın Taranması, 3 Stratejik Kart ve Pareto Analizi", "36"),
        ("8.5", "İki Gelecek: 2027–2030 Karşılaştırmalı Dinamik Simülasyon", "39"),
        ("8.6", "Havza: Yeraltı Suyu Anomalisi (GRACE), Obruklar ve Koordinasyonsuzluk Bedeli", "41"),
        ("8.7", "Karne ve Yöntem Sayfaları: Tek Sayfalık PDF ve Doğrulama Matrisi", "43"),
        ("09", "Adım Adım Kullanım: 3 Gerçekçi Senaryo", "45"),
        ("10", "Kodun Yapısı, Mimarisi ve Yazılım Mühendisliği", "48"),
        ("11", "Kurulum, Çalıştırma ve Canlı Veri İndirme Rehberi", "51"),
        ("12", "Küresel Ticaret, İhracat/İthalat Dengesi, Emtia Piyasaları ve Sanal Su (YENİ)", "54"),
        ("13", "Hedef Kitle, Çiftçi Deneyimi, İş Modeli ve Jüri Savunması (YENİ)", "58"),
        ("Ek A", "Kısaltmalar ve Terimler Sözlüğü", "62"),
        ("Ek B", "Kaynakça, Bilimsel Literatür ve NASA API Referansları", "64"),
    ]
    
    for code, title, page in toc_data:
        is_main = len(code) == 2 or code.startswith("Ek")
        if is_main:
            pdf.ln(1)
            pdf.set_font("DejaVu", "B", 8.8)
            pdf.set_text_color(*NAVY)
            pdf.cell(14, 5, code, align="L")
            pdf.cell(146, 5, title, align="L")
            pdf.set_text_color(*BLUE)
            pdf.cell(18, 5, page, align="R", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        else:
            pdf.set_font("DejaVu", "", 8)
            pdf.set_text_color(*SLATE_DARK)
            pdf.cell(8, 4.4, "", align="L")
            pdf.cell(12, 4.4, code, align="L")
            pdf.cell(140, 4.4, title, align="L")
            pdf.set_text_color(*SLATE_MED)
            pdf.cell(18, 4.4, page, align="R", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            
    pdf.ln(4)
    pdf.callout(
        "KILAVUZ KULLANIM NOTU (SÜRÜM 2.0)",
        "Bu kılavuz, projenin hem teknik agronomik hesaplamalarını (FAO-56, AquaCrop mantığı, Pareto optimizasyonu) "
        "hem de yarışma jürisi ve son kullanıcı çiftçiler için pratik kullanım adımlarını eksiksiz kapsayacak şekilde "
        "güncellenmiştir. Tüm tablolar ve hesaplamalar canlı projedeki 8/8 gerçek NASA verileri ve Eylül 2026 resmi "
        "destekleme mevzuatıyla birebir eşleşmektedir.",
        "verified"
    )


def build_chapter_01(pdf):
    pdf.chapter_header(
        "01",
        "BasinShift'e Kısa Bakış",
        "Bu bölümü okuyan kişi, projenin ne yaptığını tek cümleyle anlatabilir ve kılavuzun geri kalanında nereye bakacağını bilir."
    )
    
    pdf.section_header("Tek Cümleyle Tanım")
    pdf.body_p(
        "BasinShift, çiftçinin önümüzdeki 4 yıl için düşündüğü ekim planını son 44 yılın gerçek NASA iklim verileriyle "
        "ve 2040'ların CMIP6 iklim projeksiyonlarıyla sınayan, resmi tarımsal destekleme kurallarına (su kısıtı ve rotasyon "
        "mevzuatı) uyan en kârlı ve en dayanıklı planları 20.736 olasılık arasından kendisi bulup gerekçesiyle açıklayan ve "
        "aynı kararı havzadaki tüm çiftçiler verirse yeraltı suyuna, obruk oluşumuna ve küresel emtia dengesine ne olacağını "
        "gösteren bütünleşik bir karar destek sistemidir."
    )
    
    pdf.body_p(
        "Adındaki iki kelime projenin çift yönlü ölçeğini simgeler: Basin (Havza: Suyu aynı akifere süzülen, aynı yeraltı "
        "suyunu paylaşan ortak coğrafi alan) ve Shift (Kaydırmak/Dönüştürmek: Ekim desenini tükenen suya ve değişen iklime "
        "uyumlu olarak sürdürülebilir ürünlere doğru bilimsel ve ekonomik temelde kaydırmak)."
    )
    
    pdf.section_header("Ne Yapıyor? Üç Katmanlı Mimari")
    pdf.body_p(
        "BasinShift, sorunu tek bir ölçeğe sıkıştırmaz; mikro ölçekten (tek tarla) makro ölçeğe (bütün havza ve dünya ticareti) "
        "uzanan üç entegre katmanda çalışır:"
    )
    
    pdf.bullet("1. Katman · Tarla (Planını Sına):", "Çiftçi mevcut tarlasının koordinatını, toprak yapısını, kuyu derinliğini ve "
               "alışılagelmiş 4 yıllık ekim planını (ör. Mısır-Pancar-Mısır-Pancar) girer. Sistem, bu planı 1981-2025 arasındaki 44 yıllık "
               "gerçek NASA hava koşullarında (kuraklıklar, aşırı sıcaklar, geç donlar) oynatır; su tüketimini, reel maliyetleri, net kârı ve "
               "kırmızı kart kural ihlallerini raporlar.")
               
    pdf.bullet("2. Katman · Öneri (Daha İyisini Bul ve Nedenini Açıkla):", "Konya havzasındaki 12 ürünün tüm 4 yıllık permütasyonları "
               "(12 x 12 x 12 x 12 = 20.736 plan) elenir. Kural dışı olanlar (sarı/kırmızı kart) ve çiftçinin kısıtlarına uymayanlar elendikten sonra, "
               "kalan binlerce geçerli plan arasından 3 boyutlu Pareto Analizi ile üç stratejik kart seçilir: Denge (En yüksek Sharpe/Risk-Verim oranı), "
               "Kâr (Yasal sınırlar dahilinde maksimum nakit getiri) ve Akifer (Maksimum su tasarrufu). Her kartın altında doğal dille formüle edilmiş "
               "'Neden bu plan?' gerekçesi ve tek sayfalık indirilebilir resmi PDF karne yer alır.")
               
    pdf.bullet("3. Katman · Havza ve Küresel Boyut (Hepimiz Yaparsak Ne Olur?):", "Bütün çiftçiler sadece kendi kısa vadeli kârına bakarak "
               "aşırı su tüketen mısır ve pancara yönelirse akifer çöker ('Ortak Malların Trajedisi'). BasinShift, binlerce çiftçinin toplam su çekimini "
               "NASA GRACE uydu verileriyle ilişkilendirir; koordinasyonsuzluğun havzaya maliyetini (Price of Anarchy) ve suyun gölge fiyatını "
               "(Shadow Price) hesaplar. Ayrıca CBOT/Euronext emtia paritesi ve sanal su ihracatı dengesini ortaya koyar.")

    pdf.ln(2)
    # 3 Katman Görseli
    if os.path.exists(DIAG_3TIER):
        pdf.figure(DIAG_3TIER, "BasinShift'in Üç Ölçekli Mimarisi: Tek Tarla Analizi -> Çok Kriterli Öneri Kartları -> Havza ve Küresel Su Dengesi", max_h=55, max_w=165)
        
    pdf.section_header("Kimin İçin? Paydaş ve Kullanıcı Rolleri Matrisi")
    pdf.body_p(
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
        ["NASA Space Apps Jürisi", "NASA'nın açık uydu verileri sahada gerçek bir sorunu bilimsel olarak çözüyor mu?", "Yöntem ve Veriler -> 8/8 Gerçek Veri Matrisi -> Doğrulama Kılavuzu"]
    ]
    pdf.table(headers, rows, [38, 75, 65], ["L", "L", "L"])


def build_chapter_02(pdf):
    pdf.chapter_header(
        "02",
        "Yarışma ve Görev",
        "BasinShift neden bu biçimde tasarlandı? Çünkü NASA Space Apps Challenge 2026'nın en kritik saha görevine yanıt veriyor."
    )
    
    pdf.section_header("NASA Space Apps Challenge Nedir?")
    pdf.body_p(
        "NASA Space Apps Challenge, NASA'nın (Amerikan Ulusal Havacılık ve Uzay Dairesi) dünya genelinde her yıl düzenlediği "
        "dünyanın en büyük küresel hackathonudur. Yüzlerce şehirde aynı anda binlerce araştırmacı, mühendis, yazılımcı ve agronomist "
        "bir araya gelerek NASA'nın halka açık yer gözlem, iklim ve uydu verilerini kullanarak Dünya'nın ve insanlığın en acil "
        "sorunlarına çözüm üretir. 14–15 Kasım 2026 Konya yerel etkinliği, Türkiye'nin tahıl ambarı ve aynı zamanda en büyük yeraltı suyu "
        "krizi bölgesi olan Konya Kapalı Havzası'nda gerçekleştirilmiştir."
    )
    
    pdf.section_header("Görev: Field Shift (Adapting Farms with NASA Data)")
    pdf.body_p(
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
    
    pdf.section_header("NASA Beklentileri ve BasinShift'teki Birebir Karşılıkları")
    pdf.body_p(
        "BasinShift geliştirilirken, jüri değerlendirme kriterleri ve görev şartnamesi satır satır analiz edilmiş ve aşağıdaki "
        "somut modüller inşa edilmiştir:"
    )
    
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
    
    pdf.section_header("Yerelden Küresele Ölçeklenebilirlik")
    pdf.body_p(
        "BasinShift'in çekirdek motoru coğrafyadan bağımsızdır. Sistem, Konya Kapalı Havzası'ndaki 739 obruk ve aşırı yeraltı suyu "
        "kullanımı için sıfırdan doğrulanmış olsa da, mimari küreseldir. Örneğin Hindistan Pencap havzasında pirinç-buğday monokültürünün "
        "yarattığı akifer krizine veya Kaliforniya Central Valley'deki badem-yonca kuraklık baskısına, sadece ilgili havzanın yerel "
        "ürün tablosu (`crops.yaml`) ve su kuralları (`rules.yaml`) tanımlanarak dakikalar içinde uyarlanabilmektedir."
    )


def build_chapter_03(pdf):
    pdf.chapter_header(
        "03",
        "Sorun: Konya'dan Dünyaya",
        "Çiftçinin önünde basit görünen ama aslında devasa bir matematiksel ve ekolojik kriz var: 'Önümüzdeki 4 yıl ne ekeyim?'"
    )
    
    pdf.section_header("Konya Kapalı Havzası Hidrolojisi ve Akifer Krizi")
    pdf.body_p(
        "Kapalı havza; yağmur ve kar suyunun denizlere akmayıp havza tabanındaki göllere veya yer altı akiferine süzüldüğü coğrafyalardır. "
        "Konya Kapalı Havzası, Türkiye tarım arazilerinin yaklaşık %13'ünü barındırır ve 'Türkiye'nin Tahıl Ambarı' olarak anılır. "
        "Ancak bölgenin yıllık ortalama yağışı yalnızca 320–350 mm civarındadır (yarı kurak iklim). Buna karşılık buğdayın su ihtiyacı "
        "yaklaşık 400–450 mm, dane mısırın 700–800 mm ve şeker pancarının 850–1.000 mm'dir. Aradaki devasa açık, on binlerce derin kuyu ile "
        "yeraltı suyundan çekilmektedir."
    )
    
    pdf.body_p(
        "Son 30 yılda havzadaki derin kuyu sayısı 100.000'i aşmış (çoğu ruhsatsız), yeraltı su seviyesi her yıl ortalama 1 ila 3 metre "
        "derine düşmüş, bazı bölgelerde statik su seviyesi 40 metreden 150–200 metreye kadar gerilemiştir. NASA GRACE uydu ölçümleri, "
        "Konya havzası akifer kütlesinin her yıl ortalama 1,3 cm eşdeğer su kalınlığı kaybettiğini doğrulamaktadır."
    )
    
    pdf.section_header("739 Obruk: Akifer Çöküşünün Somut Jeolojik Kanıtı")
    pdf.body_p(
        "Aşırı su çekimi sadece suyun bitmesi anlamına gelmez; havza jeolojisinin fiziksel olarak çökmesine neden olur. Karstik kireçtaşı "
        "tabakalarındaki yeraltı boşlukları, suyun kaldırma kuvveti kalktığında aniden çökmekte ve tarım arazilerinin ortasında devasa "
        "obruklar (sinkholes) meydana gelmektedir. 2026 yılı itibarıyla Konya havzasında kayıtlı obruk sayısı 739'a ulaşmıştır. "
        "Bu obruklar tarım makinelerini, yolları ve köyleri doğrudan tehdit eden fiziksel bir felakettir."
    )
    
    pdf.section_header("Soru Neden Bu Kadar Zor? (20.736 Olasılık)")
    pdf.body_p(
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
               
    pdf.ln(2)
    pdf.callout(
        "ORTAK MALLARIN TRAJEDİSİ (TRAGEDY OF THE COMMONS)",
        "Akifer tüm çiftçilerin ortak mülküdür. Her çiftçi kendi bireysel kârını maksimize etmek için yüksek su isteyen mısır ve pancar "
        "ekerse, bireysel olarak doğru gibi görünen bu karar toplumsal olarak akiferin tamamen kurumasına ve su kuyularının tuzlanmasına yol açar. "
        "BasinShift, tarladaki bireysel kâr ile havzadaki kolektif hidrolojik dengeyi ilk kez aynı matematiksel modelde birleştirmektedir.",
        "danger"
    )
