"""
BasinShift Kılavuzu - Kısım 4: Bölüm 12, 13, Ek A, Ek B
"""
import os
from fpdf.enums import XPos, YPos
from pdf_builder import (
    NAVY, CADET, BLUE, YELLOW, RED, GREEN, AMBER,
    SLATE_DARK, SLATE_MED, SLATE_LIGHT, BG_LIGHT, BG_CARD, BORDER_COLOR
)

MEVCUT_DIR = r"c:\Users\yunus\Desktop\spaceapps\mevcutarayuzler"
IMG_16 = os.path.join(MEVCUT_DIR, "16_kuresel_ticaret_ve_sanal_su.png")
IMG_15 = os.path.join(MEVCUT_DIR, "15_ingilizce_planlar_dashboard.png")


def build_chapter_12(pdf):
    pdf.chapter_header(
        "12",
        "Küresel Ticaret, Emtia Piyasaları ve Sanal Su",
        "Tarladaki ekim kararını dünya borsalarıyla (CBOT/Euronext), Türkiye'nin dış ticaret dengesiyle ve sanal su akışıyla buluşturan yeni stratejik katman."
    )
    
    # 12.1 Giriş
    pdf.section_header("12.1 Çiftçinin Tarlasından Dünya Borsalarına")
    pdf.body_p(
        "Modern tarımda hiçbir tarla küresel piyasadan ve ulusal gıda arz güvenliğinden izole değildir. Bir çiftçinin 'bu yıl mısır mı ekeyim, "
        "buğday mı yoksa ayçiçeği mi?' kararı; sadece kuyusunun elektrik faturasını değil, Türkiye'nin cari açığını, un ihracatı liderliğini "
        "ve binlerce yıllık fosil yeraltı suyunun sanal olarak yurt dışına transfer edilmesini doğrudan etkiler. BasinShift, mentör ve jüri "
        "tavsiyeleri doğrultusunda tarladaki agronomik modeli küresel emtia borsaları (CBOT ve Euronext) ve dış ticaret dengesiyle entegre etmiştir."
    )
    
    # 12.2 Buğday ve Un İhracatı
    pdf.section_header("12.2 Türkiye'nin Un İhracatı Liderliği (#1) ve Buğday Arz Güvenliği")
    pdf.body_p(
        "Türkiye, son 10 yıldır kesintisiz olarak dünyanın 1 numaralı un ihracatçısıdır. Yılda yaklaşık 3,5–4 milyon ton un ihraç ederek "
        "1 milyar doların üzerinde döviz girdisi sağlamaktadır. Bu devasa sanayinin ayakta kalabilmesi, kaliteli ve yüksek proteinli yerli buğday "
        "arzına bağlıdır. Konya Kapalı Havzası buğdayı, glüten yapısı ve sert dane kalitesiyle un sanayisinin bel kemiğidir. "
        "Eylül 2026 kararnamesiyle buğdaya verilen 1.468 ₺/da toplam destekleme (temel + su kısıtı hibesi), üreticinin buğdayda kalmasını "
        "teşvik ederek Türkiye'nin küresel un ihracatı liderliğini güvence altına almaktadır."
    )
    
    # 12.3 Bitkisel Yağ Açığı ve Ayçiçeği
    pdf.section_header("12.3 Bitkisel Ham Yağ Açığı ve Ayçiçeğinin Kurtarıcı Rolü")
    pdf.body_p(
        "Türkiye'nin tarımsal dış ticaretindeki en büyük kanayan yarası bitkisel yağ açığıdır. Ülkemiz tükettiği bitkisel ham yağın yaklaşık "
        "%60'ını ithal etmekte ve her yıl yaklaşık 3 milyar dolar döviz ödemektedir. Ayçiçeği, Konya havzası için çifte kazanç sağlayan bir üründür:"
    )
    pdf.bullet("Su Tasarrufu:", "Dane mısır 700–800 m³/da su tüketirken, yağlık ayçiçeği 350–400 m³/da su ile yetiştirilebilir (yaklaşık %50 su tasarrufu).")
    pdf.bullet("Rekor Destekleme:", "2026 kararnamesinde ayçiçeği 1.101 ₺ temel + 440 ₺ su kısıtı olmak üzere tam 1.541 ₺/da toplam destekle ödüllendirilmektedir.")
    pdf.bullet("Cari Açığı Kapatma:", "Havzada mısırdan ayçiçeğine kayan her 100 bin dekar arazi, Türkiye'nin ham yağ ithalat faturasını on milyonlarca dolar hafifletir.")

    # 12.4 Mısır ve Sanal Su İhracatı
    pdf.section_header("12.4 Mısır ve Sanal Su İhracatı (Virtual Water Footprint)")
    pdf.body_p(
        "Sanal Su (Virtual Water), Nobel adayı Prof. Tony Allan tarafından tanımlanmış stratejik bir kavramdır: Bir tarımsal veya endüstriyel "
        "ürünün üretilmesi sürecinde harcanan görünmez toplam tatlı su miktarıdır."
    )
    
    pdf.callout(
        "KONYA HAVZASINDA MISIRIN SANAL SU BİLANÇOSU",
        "Konya Kapalı Havzası'nda 1 ton dane mısır üretebilmek için kuyulardan ortalama 1.280 m³ (1.280 ton) yeraltı suyu pompalanmaktadır. "
        "Aşırı su isteyen mısırı üretip başka şehirlere veya ülkelere ucuz hayvan yemi olarak satmak; aslında Konya'nın 10.000 yılda birikmiş "
        "kıymetli fosil yeraltı suyunu bedavaya ihraç etmek ve karşılığında geride 739 obruk bırakmak demektir. "
        "BasinShift, mısır yerine düşük sanal su ayak izine sahip nohut (650 m³/ton) ve ayçiçeği (780 m³/ton) önererek akiferi korur.",
        "danger"
    )

    # 12.5 Baklagiller ve Azot Döngüsü
    pdf.section_header("12.5 Baklagillerin Azot Döngüsü ve İthal Kimyasal Gübre Tasarrufu")
    pdf.body_p(
        "Nohut, kuru fasulye ve mercimek; köklerindeki Rhizobium bakterileri aracılığıyla atmosferdeki serbest azotu toprağa fikse eder. "
        "Bu biyolojik mucize, dekara 4–6 kg saf organik azot kazandırır. Türkiye kimyasal azotlu gübrelerin (üre, amonyum nitrat) hammaddesi "
        "olan doğalgazda tamamen dışa bağımlıdır. Baklagillerin rotasyona girmesi; tarlanın kimyasal gübre ihtiyacını %20–30 düşürür, "
        "çiftçinin girdi maliyetini azaltır ve döviz çıkışını engeller."
    )

    # 12.6 Küresel Emtia Karşılaştırma Tablosu
    pdf.section_header("12.6 Küresel Emtia Borsaları ve Sanal Su Karşılaştırma Matrisi")
    pdf.body_p(
        "Uygulamadaki `tables/commodity_trade.csv` veri tabanından canlı olarak çekilen karşılaştırma tablosu:"
    )
    
    headers = ["Ürün", "Yerel Borsa (₺/kg)", "Küresel Benchmark", "Dış Ticaret Dengesi", "Sanal Su (m³/ton)", "Stratejik Politika Tavsiyesi"]
    rows = [
        ["Ekmeklik Buğday", "16,50 ₺", "CBOT: ~220 $/ton", "Net İhracatçı (Un lideri #1)", "890 m³", "TMO alım garantisi ve su kısıtı primiyle havza omurgası olarak korunmalı."],
        ["Yağlık Ayçiçeği", "34,00 ₺", "Euronext: ~480 €/ton", "Net İthalatçı (%60 Açık)", "780 m³", "Mısırın yerine 1 numaralı ikame; 1.541 ₺/da destekle teşvik edilmeli."],
        ["Dane Mısır", "11,50 ₺", "CBOT: ~170 $/ton", "Dönemsel İthalatçı / Yem", "1.280 m³", "Aşırı sanal su kaybı; su kısıtı desteği 0 ₺, 4 yılda en fazla 1 kez ekilmeli."],
        ["Nohut / Fasulye", "42,00 ₺", "Küresel Akdeniz Piyasası", "Dengeli / Net İhracatçı", "650 m³", "Sıfır sulama ihtiyacı; toprağa azot bağlar; rotasyonun can damarıdır."],
        ["Şeker Pancarı", "3,72 ₺", "Dünya Beyaz Şeker Paritesi", "Yurtiçi Tüketim (Kota)", "920 m³", "Sözleşmeli kota dahilinde tutulmalı; ardışık ekim kesinlikle yasaklanmalı."]
    ]
    pdf.table(headers, rows, [26, 22, 34, 34, 24, 38], ["L", "C", "L", "L", "C", "L"])
    
    if os.path.exists(IMG_16):
        pdf.figure(IMG_16, "Uygulama İçi Küresel Ticaret, İhracat/İthalat Dengesi ve Sanal Su Ayak İzi Gösterge Paneli", max_h=58, max_w=165)


def build_chapter_13(pdf):
    pdf.chapter_header(
        "13",
        "Hedef Kitle, Çiftçi Deneyimi ve Jüri Savunması",
        "Mentör görüşmelerinden çıkan kritik sorular, çiftçi odaklı sade arayüz tasarımı (UX), B2B/B2G iş modeli ve jüri savunma kılavuzu."
    )
    
    # 13.1 Mentör Görüşmesi ve Sorular
    pdf.section_header("13.1 Mentör Görüşmesi Analizi ve Sorulan Sorular")
    pdf.body_p(
        "Hackathon sürecinde alanında uzman mentörlerle yapılan değerlendirmelerde projenin gücünü katlayan üç hayati geri bildirim alınmıştır:"
    )
    pdf.bullet("1. Soru (Hedef Kitle):", "'Bu projenin nihai kullanıcısı kim? Eğer çiftçi ise, köylü Mehmet Amca bu karmaşık formülleri ve "
               "grafikleri nasıl anlayacak? Çiftçi için basit bir görünüm var mı?'")
    pdf.bullet("2. Soru (Dış Ticaret ve Emtia):", "'Sistem sadece 'şunu ek' mi diyor, yoksa un ve mısır gibi ürünlerin dünya piyasası, ihracat/ithalat "
               "dengesi ve gelir skalasını küresel ölçekte kıyaslıyor mu?'")
    pdf.bullet("3. Soru (İş Modeli ve Sürdürülebilirlik):", "'Bu proje yarışmadan sonra nasıl yaşayacak? Finansal sürdürülebilirliği ve kamu entegrasyonu nasıl sağlanacak?'")

    # 13.2 Çiftçi Odaklı UX: 3 Tıkla Karar
    pdf.section_header("13.2 Çiftçi Odaklı Kullanıcı Deneyimi (UX): '3 Tıkla Karar'")
    pdf.body_p(
        "BasinShift, mentör eleştirisi doğrultusunda arayüzünü iki kademeli kullanıcı deneyimiyle (Dual-UX) tasarlamıştır:"
    )
    pdf.callout(
        "ÇİFTÇİ GÖRÜNÜMÜ: 3 TIKLA KARAR VE RENKLİ KARTLAR",
        "Okuma yazması veya dijital okuryazarlığı sınırlı bir çiftçi tarlasına geldiğinde hiçbir karmaşık grafiğe bakmak zorunda değildir:\n"
        "1. Tık: 'Örnek tarlayı yükle' veya haritadan köyünü seçer.\n"
        "2. Tık: 'Planları Gör' butonuna basar.\n"
        "3. Tık: Önüne çıkan büyük Yeşil 'Denge Kartı'nı görür: 4 yıllık ürün sırası büyük piktogramlarla gösterilir, yanında 'Kazanacağın Para: "
        "+4.108 ₺ İlave Destek', 'Kuyunun Kurtaracağı Su: 1.600 Ton' yazar. 'Karneyi İndir' butonuna basarak muhtara veya bankaya götürür.",
        "verified"
    )
    
    pdf.body_p(
        "Ziraat Mühendisi ve Karar Verici Görünümü ise; aynı sayfada 'Mühendis Görünümünü Aç' kutucuğu işaretlendiğinde devreye girer. "
        "Bu modda FAO-56 Penman-Monteith denklemleri, SoilGrids toprak nem açığı, 3D Pareto saçılım grafikleri ve GRACE Mascon serileri detaylanır."
    )

    # 13.3 B2B ve B2G İş Modeli
    pdf.section_header("13.3 B2B ve B2G Kurumsal İş Modeli ve Ekosistem Değeri")
    pdf.body_p(
        "BasinShift'in maliyet tarafı son derece hafiftir: NASA verileri tamamen açık ve ücretsizdir, çekirdek hesaplama standart bir sunucuda "
        "0,2 saniye sürer. Sistemin asıl ekonomik değeri B2B (şirketlere) ve B2G (kamuya) sunduğu kurumsal risk analitiğindedir:"
    )
    pdf.bullet("Ziraat Bankası & Tarım Kredi Kooperatifleri:", "Çiftçiye verilen 4 yıllık tarımsal işletme ve yatırım kredilerinde "
               "kredi risk puanlaması (Credit Scoring). BasinShift Denge planını uygulayan çiftçilere sübvansiyonlu faiz indirimi ve teminat kolaylığı.")
    pdf.bullet("TARSİM (Devlet Destekli Tarım Sigortaları Havuzu):", "44 yıllık NASA POWER iklim verileriyle kuraklık, aşırı sıcaklık ve don "
               "risklerinin aktüeryal hesaplaması. Parsel bazlı dinamik sigorta primi belirleme.")
    pdf.bullet("Şeker Fabrikaları (Konya Şeker, TÜRKŞEKER):", "Sözleşmeli pancar üreticilerinin su kısıtına ve rotasyon kurallarına uyumunun "
               "otomatik denetimi; hammadde tedarik zinciri sürdürülebilirliği.")
    pdf.bullet("DSİ (Devlet Su İşleri) & Tarım ve Orman Bakanlığı:", "Havza su tahsis planlaması ve 2026 havza bazlı desteklerin etkinliğinin izlenmesi.")

    # 13.4 NASA Space Apps Tasarım Sistemi
    pdf.section_header("13.4 NASA Space Apps Challenge 2026 Resmi Tasarım Sistemi")
    pdf.body_p(
        "Uygulamanın görsel kimliği, NASA Space Apps Challenge 2026 Brand Guidelines el kitabına harfiyen uyarlanmıştır:"
    )
    pdf.bullet("Deep Space Navy (#07173F):", "Uzayın derinliğini simgeleyen birincil arka plan rengi.")
    pdf.bullet("Space Cadet (#0D1B47):", "Kartlar, paneller ve kenar çubuğu ikincil arka plan rengi.")
    pdf.bullet("Electric Blue (#0042A6):", "Güven ve teknolojiyi temsil eden ana aksan rengi, aktif sekmeler ve butonlar.")
    pdf.bullet("Neon Yellow (#EAFE07):", "Enerji ve dikkati çeken aksan rengi; çağrı (CTA) butonları ve önemli uyarılar.")
    pdf.bullet("Rocket Red (#E43700):", "Kırmızı kart, kural ihlali ve kritik akifer uyarıları.")
    pdf.bullet("Tipografi Standartları:", "Başlıklarda güçlü Fira Sans, gövde metinlerinde okunabilir Overpass, teknik kod ve sayılarda Fira Code.")

    # 13.5 Jüriye Karşı 10 Kritik Soru ve 3 Cümlelik Net Cevaplar
    pdf.section_header("13.5 Jüriye Karşı 10 Kritik Soru ve 3 Cümlelik Net Cevaplar")
    pdf.body_p(
        "Jüri üyelerinin sorabileceği en zorlayıcı 10 soru ve projenin 3 cümlelik net savunma yanıtları:"
    )
    
    qa_list = [
        ("1. Veriler gerçekten NASA'dan mı, sentetik veri mi?",
         "Sistemimizdeki 8 veri setinin 8'i de NASA (POWER, GPM, GRACE, SMAP, SRTM, CMIP6) ve SoilGrids'ten resmi API'lerle çekilmiş %100 gerçek verilerdir. "
         "Sentetik veriler ilk mimari testlerin ardından tamamen kaldırılmış ve canlı doğrulama paneli eklenmiştir. "
         "Uygulamanın 'Yöntem ve Veriler' sayfasında 8/8 yeşil onay rozeti canlı olarak görülebilir."),
         
        ("2. 12 ürünün 4 yıllık kombinasyonu (20.736 plan) nasıl bu kadar hızlı taranıyor?",
         "Hesaplama yükü, önceden derlenen 12 ürün x 44 yıl = 528 durumlu 'Ürün-Yıl Matrisi' üzerine kurulmuştur. "
         "Kayan pencere döngüleri Python'ın yüksek performanslı NumPy ve SciPy vektörize operasyonlarıyla optimize edilmiştir. "
         "20.736 planın kural kontrolü ve 3D Pareto analizi standart bir dizüstü bilgisayarda yalnızca 0,2 saniye sürmektedir."),
         
        ("3. Köylü çiftçi bu sistemi anlayıp tarlasında uygulayabilir mi?",
         "Evet; çünkü çiftçi karmaşık formüllerle değil, '3 Tıkla Karar' veren sadeleştirilmiş renkli karar kartlarıyla karşılaşır. "
         "Sistem çiftçiye sadece kaç ton su tasarruf edeceğini, ne kadar net para ve devlet desteği kazanacağını büyük harflerle söyler. "
         "Ayrıca bankaya veya kooperatife ibraz edebileceği resmi tek sayfalık 'Risk ve Su Karnesi'ni tek tıkla PDF olarak basar."),
         
        ("4. Eylül 2026 tarımsal destekleme katsayıları gerçeği yansıtıyor mu?",
         "Evet; modelimiz Resmi Gazete'de yayımlanan Eylül 2026 Tarımsal Destekleme Kararnamesi'nin katsayı birim değerini (367 ₺/da) birebir uygulamaktadır. "
         "Su kısıtı ilan edilen Konya ilçelerinde buğdaya 1.468 ₺/da, ayçiçeğine 1.541 ₺/da destek verilirken, dane mısır ve patatese sıfır (0 ₺) destek kuralı eksiksiz kodlanmıştır. "
         "Ardışık ekim yapanlara uygulanan 5 yıl ÇKS men cezası (kırmızı kart) kural motorumuz tarafından tam denetlenir."),
         
        ("5. Konya'daki 739 obruk tehlikesi modelde nasıl yer alıyor?",
         "Obruk oluşumu, NASA GRACE uydu ölçümleriyle kanıtlanan yıllık -1,3 cm'lik akifer su kütlesi kaybının doğrudan jeolojik sonucudur. "
         "BasinShift'in 'Havza' katmanı, aşırı su tüketen mısır ve pancar yerine ayçiçeği ve baklagil ekildiğinde akiferdeki çekimin nasıl duracağını hesaplar. "
         "Böylece model sadece tarlada kâr hesabı yapmaz, havzadaki karstik obruk çöküşünü önleyen bölgesel su politikasını yönlendirir."),
         
        ("6. Dünya emtia fiyatlarındaki dalgalanmalar çiftçinin planını nasıl etkiler?",
         "BasinShift, yerel TMO fiyatlarının yanı sıra CBOT (Chicago) ve Euronext (Paris) uluslararası vadeli emtia piyasalarını modele entegre etmiştir. "
         "Çiftçi planını seçerken küresel fiyat paritesini ve Türkiye'nin dış ticaret açığını göz önünde bulundurur. "
         "Böylece küresel piyasada fiyatı çöken ürünler yerine, arz açığı olan ve katma değeri yüksek ürünlere güvenle yönelir."),
         
        ("7. Sanal su ihracatı neden bir milli güvenlik meselesidir?",
         "Konya'da 1 ton dane mısır üretmek kuyulardan 1.280 m³ kıymetli yeraltı suyu çekilmesini gerektirir. "
         "Aşırı su tüketen mısırı ucuz yem olarak satmak veya ihraç etmek, Türkiye'nin binlerce yıllık yeraltı su rezervini sanal olarak yurt dışına bedavaya transfer etmektir. "
         "BasinShift sanal su ihracatını görünür kılarak milli su güvenliğimizi koruyan ürün desenini savunur."),
         
        ("8. Bu sistem başka bir ülkeye veya havzaya taşınabilir mi?",
         "Kesinlikle evet; mimarimiz tamamen parametrik ve modüler olarak inşa edilmiştir. "
         "Hindistan Pencap havzası için çeltik-buğday deseni veya ABD California Central Valley için badem-yonca kuralları tek bir YAML dosyasında tanımlanabilir. "
         "NASA uyduları küresel kapsama alanına sahip olduğu için sistem dünyanın herhangi bir noktasında sıfır ek maliyetle çalışır."),
         
        ("9. Neden bir yapay zekâ dil modeli (LLM) yerine deterministik agronomik model tercih edildi?",
         "Çünkü tarımsal kararlarda ve su yönetiminde halüsinasyon (uydurma rakamlar) felaketle sonuçlanır. "
         "Çiftçinin hayatı ve devletin su bütçesi, kaynağı belirsiz bir yapay zekâ sohbet robotuna emanet edilemez. "
         "BasinShift'in arkasında FAO-56 Penman-Monteith, Stewart verim denklemleri ve resmi mevzuat kurallarından oluşan %100 doğrulanabilir bilimsel modeller vardır."),
         
        ("10. Projenin ticarileşme ve kamuya entegrasyon vizyonu nedir?",
         "BasinShift çiftçiye her zaman ücretsiz bir kamu hizmeti olarak kalacaktır. "
         "Gelir modelimiz; Ziraat Bankası gibi kurumlara tarımsal kredi risk skorlama API'si satmak ve TARSİM'e kuraklık aktüeryal risk haritaları sağlamaktır. "
         "Nihai hedefimiz ise yazılımı Tarım ve Orman Bakanlığı'nın Çiftçi Kayıt Sistemi'ne (ÇKS) entegre ederek Türkiye'nin resmi ekim planlama platformu haline getirmektir.")
    ]
    
    for q, a in qa_list:
        pdf.subsection_header(q)
        pdf.body_p(a, space_after=2)


def build_appendix_a(pdf):
    pdf.chapter_header(
        "Ek A",
        "Kısaltmalar ve Terimler Sözlüğü",
        "Kılavuzda ve uygulamada geçen tüm agronomik, hidrolojik, ekonomik ve uydu terimlerinin alfabetik tanımları."
    )
    
    headers = ["Kısaltma / Terim", "Açılımı / Anlamı", "Birim / Kapsam", "Tanımı ve Sistemdeki Rolü"]
    rows = [
        ["Akifer", "Yeraltı Su Deposu", "Hidroloji", "Yeraltında su tutan ve kuyulardan çekilen gözenekli jeolojik kaya/kum tabakası."],
        ["Brüt Kâr", "Brüt Tarımsal Gelir", "₺/da/yıl", "(Verim x Fiyat) + Destekler - Değişken Maliyetler (Tohum, gübre, mazot, elektrik)."],
        ["CBOT", "Chicago Board of Trade", "Küresel Borsa", "Dünyanın en büyük tarımsal vadeli işlemler borsası; buğday ve mısır küresel gösterge fiyatı."],
        ["CVaR", "Conditional Value at Risk", "₺/da/yıl", "En kötü %5'lik dönemde (kurak yıllarda) elde edilen ortalama yıllık gelir; risk ölçütü."],
        ["ÇKS", "Çiftçi Kayıt Sistemi", "Mevzuat", "Tarım ve Orman Bakanlığı'nın tarımsal destekleri dağıttığı ve ekimleri kaydettiği resmi sistem."],
        ["Dekar (da)", "1.000 Metrekare", "Alan Birimi", "Türkiye standart tarla alanı ölçüsü. 1 da = 1.000 m² = 0,1 ha."],
        ["ET0", "Referans Buharlaşma", "mm/gün", "FAO-56 standardı; 12 cm yüksekliğindeki yeşil çim yüzeyin potansiyel su tüketimi."],
        ["ETc", "Bitki Su İhtiyacı", "mm/gün", "Bitkinin fenolojik evresine göre su tüketimi: ETc = Kc * ET0."],
        ["Euronext", "Avrupa Emtia Borsası", "Küresel Borsa", "Paris merkezli Avrupa tarım borsası; yağlık ayçiçeği ve kolza küresel göstergesi."],
        ["FC", "Tarla Kapasitesi", "mm su / m", "Şiddetli yağıştan sonra yerçekimine direnip toprakta asılı kalan maksimum su miktarı."],
        ["GPM", "Global Precipitation Measurement", "NASA Uydu", "Küresel yağış radarı uydusu; IMERG v07 ürünüyle yüksek çözünürlüklü yağış sağlar."],
        ["GRACE", "Gravity Recovery and Climate Experiment", "NASA/DLR Uydu", "Dünya yerçekimi alanındaki değişimleri ölçerek akifer yeraltı su kütle kaybını izler."],
        ["HLS", "Harmonized Landsat-Sentinel", "NASA/USGS", "30 metre çözünürlükte 5 günlük sıklıkla bitki örtüsü (NDVI) sağlayan uydu serisi."],
        ["Kc", "Bitki Katsayısı", "Boyutsuz", "Bitkinin türüne ve büyüme evresine göre su tüketim katsayısı (0.3 ile 1.2 arası)."],
        ["Ky", "Verim Tepki Katsayısı", "Boyutsuz", "FAO Stewart su-verim azalış katsayısı; su eksikliğinde verimin ne kadar düşeceğini belirler."],
        ["Kırmızı Kart", "Destekleme Men Cezası", "Mevzuat Kuralı", "Su kısıtı kurallarına aykırı ardışık ekim yapan çiftçinin 5 yıl destekten men edilmesi."],
        ["Mascon", "Kütle Konsantrasyon Bloğu", "cm su eşdeğeri", "GRACE uydu verilerinin yerçekimsel kütle değişimini ifade eden hidrolojik birim."],
        ["Obruk", "Karstik Çöküntü", "Jeoloji", "Yeraltı suyu seviyesinin düşmesiyle karstik boşlukların tavanının çökmesi sonucu oluşan çukur."],
        ["Pareto Sınırı", "Optimal Etkinlik Sınırı", "Optimizasyon", "Kâr, su tasarrufu ve risk arasında birini kötüleştirmeden diğerini iyileştiremeyen planlar kümesi."],
        ["POWER", "Prediction of Worldwide Energy Resources", "NASA Projesi", "1981'den günümüze günlük güneş radyasyonu, sıcaklık, nem ve rüzgar sağlayan iklim API'si."],
        ["RAW", "Kolay Alınabilir Su", "mm su", "Toprak suyunun bitki strese girmeden kökleriyle kolayca emebildiği kısmı: RAW = p * TAW."],
        ["Sanal Su", "Virtual Water Footprint", "m³/ton", "Bir ürünün tohumdan hasada kadar üretilmesi için harcanan görünmez toplam tatlı su."],
        ["Sarı Kart", "Destek Askıya Alma", "Mevzuat Kuralı", "Su kısıtı ilçelerinde 4 yılda 2'den fazla mısır/pancar ekilmesi durumunda o yılın desteğinin kesilmesi."],
        ["Sharpe Oranı", "Risk-Verim Rasyosu", "Finansal Metrik", "Planın getirdiği ortalama brüt kârın, gelir dalgalanması riskine oranı."],
        ["SMAP", "Soil Moisture Active Passive", "NASA Uydu", "L-bant radyometre ile toprağın kök bölgesindeki nem seviyesini ölçen uydu."],
        ["SRTM", "Shuttle Radar Topography Mission", "NASA Radar", "Uzay mekiğiyle ölçülen 30 metre çözünürlüklü küresel sayısal yükseklik ve eğim modeli."],
        ["TAW", "Toplam Kullanılabilir Su", "mm su", "Tarla kapasitesi (FC) ile solma noktası (WP) arasındaki bitkinin emebileceği toplam su."],
        ["TMO", "Toprak Mahsulleri Ofisi", "Kamu Kurumu", "Türkiye'de tahıl taban fiyatlarını belirleyen ve alım garantisi veren resmi kamu kuruluşu."],
        ["WP", "Sürekli Solma Noktası", "mm su / m", "Toprak neminin bitki köklerinin ememeyeceği kadar kuruduğu ve bitkinin solduğu alt sınır."]
    ]
    pdf.table(headers, rows, [32, 44, 30, 72], ["L", "L", "C", "L"])


def build_appendix_b(pdf):
    pdf.chapter_header(
        "Ek B",
        "Kaynakça ve Bilimsel Literatür",
        "BasinShift'in arkasındaki bilimsel makaleler, Birleşmiş Milletler FAO standartları, NASA yayınları ve resmi mevzuat referansları."
    )
    
    pdf.section_header("Uluslararası Bilimsel Literatür ve Standartlar")
    pdf.bullet("1. Allen, R. G., Pereira, L. S., Raes, D., & Smith, M. (1998):", "Crop evapotranspiration: Guidelines for computing crop water requirements. "
               "FAO Irrigation and Drainage Paper No. 56, Rome: Food and Agriculture Organization of the United Nations (FAO-56 Standardı).")
    pdf.bullet("2. Doorenbos, J., & Kassam, A. H. (1979):", "Yield response to water. FAO Irrigation and Drainage Paper No. 33, Rome: FAO (Stewart Ky Modeli).")
    pdf.bullet("3. Allan, J. A. (1998):", "Virtual water: A strategic resource global solutions to local deficits. Groundwater, 36(4), 545-546 (Sanal Su Teorisi).")
    pdf.bullet("4. Tapley, B. D., Watkins, M. M., Flechtner, F., et al. (2019):", "Contributions of GRACE to understanding climate change. "
               "Nature Climate Change, 9(5), 358-369 (GRACE Yeraltı Suyu Ölçüm Metodolojisi).")
    pdf.bullet("5. Huffman, G. J., Bolvin, D. T., Braithwaite, D., et al. (2020):", "Integrated Multi-satellitE Retrievals for GPM (IMERG) technical documentation. "
               "NASA Goddard Space Flight Center (GPM IMERG v07 Yağış Algoritmaları).")
    pdf.bullet("6. Entekhabi, D., Njoku, E. G., O'Neill, P. E., et al. (2010):", "The Soil Moisture Active Passive (SMAP) mission. "
               "Proceedings of the IEEE, 98(5), 704-716 (SMAP Toprak Nemi Ölçümleri).")
    pdf.bullet("7. Hengl, T., Mendes de Jesus, J., Heuvelink, G. B., et al. (2017):", "SoilGrids250m: Global gridded soil information based on machine learning. "
               "PLoS ONE, 12(2), e0169748 (ISRIC Küresel Toprak Veri Tabanı).")
    pdf.bullet("8. Farr, T. G., Rosen, P. A., Caro, E., et al. (2007):", "The Shuttle Radar Topography Mission. Reviews of Geophysics, 45(2) (SRTM 30m DEM).")
    pdf.bullet("9. Thrasher, B., Wang, W., Michaelis, A., et al. (2022):", "NASA Global Daily Downscaled Projections, CMIP6 (NEX-GDDP-CMIP6). "
               "Scientific Data, 9(1), 262 (NASA Gelecek İklim Senaryoları).")

    pdf.section_header("Resmi Mevzuat ve Kurumsal Raporlar")
    pdf.bullet("10. T.C. Cumhurbaşkanlığı Kararı (Eylül 2026):", "2026–2028 Yıllarında Yapılacak Bitkisel Üretime Yönelik Desteklemeler ile Diğer Bazı Tarımsal Desteklemelere İlişkin Karar. "
               "T.C. Resmî Gazete, Sayı: 32647 (Birim katsayı 367 ₺/da, su kısıtı destekleri ve havza planlama kuralları).")
    pdf.bullet("11. DSİ (Devlet Su İşleri) Genel Müdürlüğü (2025):", "Konya Kapalı Havzası Hidrolojik Etüt Raporu ve Yeraltı Suyu Seviye Değişimleri Bülteni, Ankara.")
    pdf.bullet("12. TMO (Toprak Mahsulleri Ofisi) (2026):", "2026 Dönemi Hububat ve Bakliyat Müdahale Alım Fiyatları ve Piyasa Değerlendirme Raporu, Ankara.")
    pdf.bullet("13. TÜRKŞEKER (Türkiye Şeker Fabrikaları A.Ş.) (2026):", "2026–2027 Kampanya Dönemi Şeker Pancarı Alım Kesin Fiyatı ve Kota Primleri Tebliği, Ankara.")
    pdf.bullet("14. TARSİM (Tarım Sigortaları Havuzu) (2026):", "Köy Bazlı Kuraklık Verim Sigortası ve İklim Riskleri Tarife ve Talimatları, İstanbul.")
